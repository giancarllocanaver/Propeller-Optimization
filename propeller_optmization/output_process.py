import os
import plotly.express as px
import pandas as pd

from matplotlib import pyplot as plt
from tqdm import tqdm

from .optimizer import PSO
from .data_reader import DataReader
from .blade_element_theory import BladeElementTheory
from .utilities.airfoil_creation import AirfoilCreation


class OutputProcess:
    def __init__(
        self,
        uuid: str,
        optimization_instance: PSO,
        results_dir: str,
        data_reader: DataReader,
    ) -> None:
        self.uuid = uuid
        self.opt_inst = optimization_instance
        self.results_dir = results_dir
        self.data_reader = data_reader

    def process_outputs(self):
        self.__create_excel_output_file()
        self.__create_FO_per_time_graph()
        self.__create_variables_per_time_graph()
        self.__create_airfoils_graph()
        self.__create_ct_and_cq_graphs_per_j()

    def __create_excel_output_file(self):
        vars_time = [
            (
                time,
                id_part,
                particle.results.get("traction"),
                particle.results.get("torque"),
                particle.results.get("tCoefficient"),
                particle.results.get("qCoefficient"),
                particle.results.get("pCoefficient"),
                particle.results.get("efficiency"),
            )
            for time in self.opt_inst.results_per_time
            for id_part, particle in self.opt_inst.results_per_time.get(time).items()
        ]

        df_result = pd.DataFrame(
            vars_time,
            columns=[
                "iteration",
                "idParticle",
                "Traction",
                "Torque",
                "Ct",
                "Cq",
                "Cp",
                "efficiency",
            ],
        )

        with pd.ExcelWriter(
            os.path.join(self.results_dir, "dataResults.xlsx"), engine="xlsxwriter"
        ) as writer:
            df_result.to_excel(writer, sheet_name="particlesResults", index=False)

    def __create_FO_per_time_graph(self):
        plt.plot(
            list(self.opt_inst.fo_per_time.keys()),
            list(self.opt_inst.fo_per_time.values()),
            "--o",
        )
        plt.xlabel("Iteration pass")
        plt.ylabel("Value")
        plt.grid()
        plt.savefig(os.path.join(self.results_dir, f"foIterTime.jpeg"), dpi=300)

    def __create_variables_per_time_graph(self):
        path_vars_time = "varsPerTime"
        os.makedirs(
            os.path.join(
                self.results_dir,
                path_vars_time,
            ),
            exist_ok=True,
        )

        vars_time = [
            (
                time,
                id_part,
                particle.variables[0],
                particle.variables[1],
                particle.variables[2],
                particle.variables[3],
                particle.variables[4],
                particle.variables[5],
                particle.variables[6],
            )
            for time in self.opt_inst.results_per_time
            for id_part, particle in self.opt_inst.results_per_time.get(time).items()
        ]
        df_vars_time = pd.DataFrame(
            vars_time,
            columns=["iteration", "idParticle"] + [f"var{i}" for i in range(7)],
        )

        for var in range(6):
            fig = px.scatter(
                data_frame=df_vars_time,
                x=f"var{var}",
                y=f"var{var+1}",
                color="iteration",
                color_continuous_scale=px.colors.diverging.Spectral,
            )
            fig.write_image(
                os.path.join(
                    self.results_dir,
                    path_vars_time,
                    f"Var{var}-Var{var+1}PerIteration.jpeg",
                )
            )

    def __create_airfoils_graph(self):
        best_particle = list(self.opt_inst.best.get("g_best").keys())[0]
        particle = self.opt_inst.particles.get(best_particle)

        fig, axs = plt.subplots(2, 4)

        for section in range(7):
            row = 0 if section < 4 else 1
            column = section if section < 4 else (section - 4)

            axs[row, column].plot(
                particle.splines[section][0], particle.splines[section][1]
            )
            axs[row, column].set_title(f"Section {section}")

        axs[1, 3].plot(particle.splines[6][0], particle.splines[6][1])
        axs[1, 3].set_title(f"Section 7")

        for ax in axs.flat:
            ax.set(xlabel="x", ylabel="y")
            ax.label_outer()
            ax.set_xlim((-0.05, 1))
            ax.set_ylim((-0.5, 0.5))
            ax.grid()

        fig.savefig(
            os.path.join(self.results_dir, f"airfoils.jpeg"),
            dpi=300,
        )

    def __create_ct_and_cq_graphs_per_j(self):
        def create_airfoil_files():
            id_best_particle = list(self.opt_inst.best.get("g_best").keys())[0]
            splines = self.opt_inst.particles.get(id_best_particle).splines

            return {
                section: AirfoilCreation.create_airfoil_in_xfoil_from_splines(
                    splines[section]
                )
                for section in range(len(splines))
            }

        def execute_blade_element_theory(airfoil_files: dict, flight_conditions: dict):
            blade_instance = BladeElementTheory(
                uuid=self.uuid,
                airfoils=airfoil_files,
                flight_conditions=flight_conditions,
                propeller_geometric_conditions=self.data_reader.propeller_geometric_conditions,
                xfoil_instances=self.data_reader.optimization_data.get(
                    "xfoilInstances"
                ),
            )
            blade_instance.calculate_propeller_results()

            return blade_instance.results

        airfoil_files = create_airfoil_files()
        velocities = [vel for vel in range(1, 100, 5)]
        flight_cond = self.data_reader.flight_conditions.copy()

        total_results = {
            "advanceRate": list(),
            "efficiency": list(),
            "tractionCoefficient": list(),
            "toqueCoefficient": list(),
        }

        for velocity in tqdm(velocities):
            flight_cond["speed"] = velocity
            result = execute_blade_element_theory(airfoil_files, flight_cond)

            total_results["advanceRate"].append(result.get("advanceRate"))
            total_results["efficiency"].append(result.get("efficiency"))
            total_results["tractionCoefficient"].append(result.get("tCoefficient"))
            total_results["toqueCoefficient"].append(result.get("qCoefficient"))

        for type_result in ["efficiency", "tractionCoefficient", "toqueCoefficient"]:
            fig, axs = plt.subplots(1, 1)
            axs.plot(
                total_results.get("advanceRate"), total_results.get(type_result), "--o"
            )
            axs.set(xlabel=r"$J$", ylabel=type_result)
            axs.grid()

            fig.savefig(
                os.path.join(self.results_dir, f"{type_result}-J.jpeg"),
                dpi=300,
            )
