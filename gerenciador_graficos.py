import os
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px
import re
import numpy as np
from utilidades import (
    aplicar_rotacao,
    montar_array_coordenadas_aerofolios,
    montar_array_dT_dr_e_dQ
)

class GerenciaGraficos:
    def __init__(
        self,
        **kwargs
    ):
        self.df_aerodinamicos: pd.DataFrame = kwargs["dados_aerodinamicos"]
        self.df_pso: pd.DataFrame = kwargs["dados_pso"]
        self.path_local_cenario: str = kwargs["path_local_cenario"]
        # self.aerofolios: list = kwargs["aerofolios"]
        self.passos_iteracao: list = kwargs["passos_iteracao"]
        self.valores_fo: list = kwargs["valores_fo"]

        self.gerar_pastas()
        self.realizar_grafico_fo_iteracao()
        self.realizar_graficos_escalares_iteracoes()
        self.selecionar_melhor_particula()
        self.gerar_grafico_aerofolios()

    def gerar_pastas(self):
        if not os.path.isdir(f"{self.path_local_cenario}/graficos"):
            os.mkdir(f"{self.path_local_cenario}/graficos")


    def realizar_grafico_fo_iteracao(self):
        df = pd.DataFrame(
            data={
                'Iteração': self.passos_iteracao,
                'Função Objetivo': self.valores_fo
            }
        )

        plt.plot(df["Iteração"].values, df["Função Objetivo"].values, '--o')
        plt.xlabel('Iteração')
        plt.ylabel('Função Objetivo')
        plt.grid()
        plt.savefig(f'{self.path_local_cenario}/graficos/Grafico-convergencia-otimizacao.jpeg', dpi=300)


    def realizar_graficos_escalares_iteracoes(self):
        """
        Método responsável por gerar os gráficos escalar por
        escalar ao longo das iterações
        """
        colunas_escalares = [
            "escalar 1 Ay3",
            "escalar 2 Ay3",
            "escalar 3 Ay3",
            "escalar 4 Ay3",
            "escalar 5 Ay3",
            "escalar 6 Ay3",
            "escalar 7 Ay3"
        ]

        for coluna in colunas_escalares:
            coluna_nova = coluna.replace(" Ay3", "")
            num_escalar = coluna_nova.replace("escalar ", "")
            self.df_pso.rename(
                columns={
                    coluna: f"Escalar Ay seção {num_escalar}"
                },
                inplace=True
            )

        self.df_pso.rename(
            columns={
                "iteracao": "Iteração"
            },
            inplace=True
        )

        for num_secao in range(6):
            fig = px.scatter(
                data_frame=self.df_pso,
                x=f"Escalar Ay seção {num_secao+1}",
                y=f"Escalar Ay seção {num_secao+2}",
                color="Iteração",
                color_continuous_scale=px.colors.diverging.Spectral
            )
            fig.write_image(
                f"{self.path_local_cenario}/graficos/Escalar {num_secao+1} vs Escalar {num_secao+2} por iteracao.jpeg"
            )


    def selecionar_melhor_particula(self):
        selecao = self.df_aerodinamicos["eficiencia"] == self.valores_fo[-1]
        df_melhor_particula = self.df_aerodinamicos[selecao].sample()

        self.df_melhor_particula = df_melhor_particula.copy()


    def gerar_grafico_aerofolios(self):
        fig, axs = plt.subplots(2,4)
        for secao in range(4):
            nome_arq_aerofolio = self.df_melhor_particula[f"Aerofolio secao {secao}"].values[0]
            coordenadas = montar_array_coordenadas_aerofolios(nome_arq_aerofolio)
            coordenadas = aplicar_rotacao(
                coordenadas=coordenadas,
                beta=self.df_melhor_particula[f"Beta {secao}"].values[0]
            )
            axs[0,secao].plot(coordenadas[:,0], coordenadas[:,1])
        
        for secao in range(3):
            nome_arq_aerofolio = self.df_melhor_particula[f"Aerofolio secao {secao+4}"].values[0]
            coordenadas = montar_array_coordenadas_aerofolios(nome_arq_aerofolio)
            coordenadas = aplicar_rotacao(
                coordenadas=coordenadas,
                beta=self.df_melhor_particula[f"Beta {secao+4}"].values[0]
            )
            axs[1,secao].plot(coordenadas[:,0], coordenadas[:,1])        

        axs[1,3].plot(coordenadas[:,0], coordenadas[:,1])

        for ax in axs.flat:
            ax.set(xlabel='x', ylabel='y')
            ax.label_outer()
            ax.set_ylim((-0.25, 0.25))
            ax.grid()

        for figura in range(8):
            if figura < 4:
                axs[0,figura].set_title(f"Seção {figura+1}")
            else:
                axs[1,(figura - 4)].set_title(f"Seção {figura+1}")

        fig.savefig(f'{self.path_local_cenario}/graficos/Aerofolios.jpeg', dpi=300)


    def gerar_grafico_dT_e_dQ_vs_dr(self):
        valores = montar_array_dT_dr_e_dQ(
            df=self.df_melhor_particula
        )

        fig_dT, axs_dT = plt.subplots(1,1)
        axs_dT.plot(valores["dr values"], valores["dT values"], "--o", color='blue')
        axs_dT.set(xlabel=r"$dr$", ylabel=r"$dT$")
        axs_dT.grid()
        fig_dT.savefig(f'{self.path_local_cenario}/graficos/dT_vs_dr.jpeg', dpi=300)

        fig_dQ, axs_dQ = plt.subplots(1,1)
        axs_dQ.plot(valores["dr values"], valores["dQ values"], "--o", color='blue')
        axs_dQ.set(xlabel=r"$dr$", ylabel=r"$dQ$")
        axs_dQ.grid()
        fig_dQ.savefig(f'{self.path_local_cenario}/graficos/dQ_vs_dr.jpeg', dpi=300)


            