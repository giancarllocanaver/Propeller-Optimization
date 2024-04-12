import os
import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt

from .optimizer import PSO


class OutputProcess:
    def __init__(self, uuid: str, optimization_instance: PSO, results_dir: str) -> None:
        self.uuid = uuid
        self.opt_inst = optimization_instance
        self.results_dir = results_dir

    def process_outputs(self):
        self.__create_excel_output_file()
        self.__create_FO_per_time_graph()
        self.__create_variables_per_time_graph()
        self.__create_airfoils_graph()
        self.__create_ct_and_cq_graphs_per_j()

    def __create_excel_output_file(self):
        pass

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
        pass
