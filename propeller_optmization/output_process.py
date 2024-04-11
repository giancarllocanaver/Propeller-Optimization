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
        pass

    def __create_ct_and_cq_graphs_per_j(self):
        pass
