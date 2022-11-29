import os
from turtle import color
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px
import re
import numpy as np
from utilidades import (
    aplicar_rotacao,
    montar_array_coordenadas_aerofolios,
    montar_array_dT_dr_e_dQ,
    gerar_dados_diveras_velocidades
)

class GerenciaGraficos:
    def __init__(
        self,
        **kwargs
    ):
        self.df_aerodinamicos: pd.DataFrame = kwargs["dados_aerodinamicos"]
        self.df_pso: pd.DataFrame = kwargs["dados_pso"]
        self.path_local_cenario: str = kwargs["path_local_cenario"]
        self.passos_iteracao: list = kwargs["passos_iteracao"]
        self.valores_fo: list = kwargs["valores_fo"]
        self.condicoes_de_voo: dict = kwargs.get("condicao_de_voo")
        self.condicoes_geometricas: dict = kwargs.get("condicoes_geometricas")
        self.gerador_graficos_externo = False
        self.particula_escolhida = None
        self.iteracao_escolhida = None

        if "graficos_externos" in kwargs.keys():
            self.gerador_graficos_externo = kwargs.get("graficos_externos")

        if "particula_escolhida" in kwargs.keys():
            self.particula_escolhida = kwargs.get("particula_escolhida")

        if "iteracao_escolhida" in kwargs.keys():
            self.iteracao_escolhida = kwargs.get("iteracao_escolhida")            

        self.gerar_pastas()
        if not self.gerador_graficos_externo:
            self.realizar_grafico_fo_iteracao()
            self.realizar_graficos_escalares_iteracoes()
        self.selecionar_melhor_particula()
        self.gerar_grafico_aerofolios()
        self.gerar_grafico_cT_e_cQ_por_J()
        if not self.gerador_graficos_externo:
            self.gerar_grafico_beta_por_r()
        self.gerar_grafico_caminho_particula_unica()

    def gerar_pastas(self):
        if not os.path.isdir(f"{self.path_local_cenario}/graficos"):
            os.mkdir(f"{self.path_local_cenario}/graficos")

        if self.gerador_graficos_externo:
            if not os.path.isdir(f"{self.path_local_cenario}/graficos_extras"):
                os.mkdir(f"{self.path_local_cenario}/graficos_extras")

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
        if self.particula_escolhida is None:
            if self.iteracao_escolhida is None:
                selecao = self.df_aerodinamicos["eficiencia"] == self.valores_fo[-1]
                df_melhor_particula = self.df_aerodinamicos[selecao].sample()
            else:
                selecao = self.df_aerodinamicos["iteracao"] == self.iteracao_escolhida
                df_particulas = self.df_aerodinamicos[selecao]
                selecao_melhor_particula = df_particulas["eficiencia"] == df_particulas["eficiencia"].max()
                df_melhor_particula = df_particulas[selecao_melhor_particula].sample()
        else:
            selecao = self.df_aerodinamicos["Particula"] == self.particula_escolhida
            df_selecao_particula = self.df_aerodinamicos[selecao]
            if self.iteracao_escolhida is None:
                selecao = df_selecao_particula["Iteracao"] == df_selecao_particula["Iteracao"].max()
                df_melhor_particula = df_selecao_particula[selecao]
            else:
                selecao = df_selecao_particula["Iteracao"] == self.iteracao_escolhida
                df_melhor_particula = df_selecao_particula[selecao]
        
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
            # x_left, x_right = ax.get_xlim()
            # y_low, y_high = ax.get_ylim()
            # ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*1)
            ax.set_xlim((-0.5,0.5))
            ax.set_ylim((-0.5,0.5))
            ax.grid()

        for figura in range(8):
            if figura < 4:
                axs[0,figura].set_title(f"Seção {figura+1}")
            else:
                axs[1,(figura - 4)].set_title(f"Seção {figura+1}")

        if not self.gerador_graficos_externo:
            fig.savefig(f'{self.path_local_cenario}/graficos/Aerofolios.jpeg', dpi=300)
        else:
            fig.savefig(f"{self.path_local_cenario}/graficos_extras/Aerofolios.jpeg", dpi=300)


    def gerar_grafico_dT_e_dQ_vs_dr(self):
        valores = montar_array_dT_dr_e_dQ(
            df=self.df_melhor_particula
        )

        fig_dT, axs_dT = plt.subplots(1,1)
        axs_dT.plot(valores["dr values"], valores["dT values"], "--o", color='blue')
        axs_dT.set(xlabel=r"$dr$", ylabel=r"$dT$")
        axs_dT.grid()

        if not self.gerador_graficos_externo:
            fig_dT.savefig(f'{self.path_local_cenario}/graficos/dT_vs_dr.jpeg', dpi=300)
        else:
            fig_dT.savefig(f"{self.path_local_cenario}/graficos_extras/dT_vs_dr.jpeg", dpi=300)

        fig_dQ, axs_dQ = plt.subplots(1,1)
        axs_dQ.plot(valores["dr values"], valores["dQ values"], "--o", color='blue')
        axs_dQ.set(xlabel=r"$dr$", ylabel=r"$dQ$")
        axs_dQ.grid()

        if not self.gerador_graficos_externo:
            fig_dQ.savefig(f'{self.path_local_cenario}/graficos/dQ_vs_dr.jpeg', dpi=300)
        else:
            fig_dQ.savefig(f"{self.path_local_cenario}/graficos_extras/dQ_vs_dr.jpeg", dpi=300)


    def gerar_grafico_cT_e_cQ_por_J(self):
        resultados = gerar_dados_diveras_velocidades(
            df=self.df_melhor_particula,
            corda=self.condicoes_geometricas["corda"],
            raio=self.condicoes_geometricas["raio"],
            condicoes_de_voo=self.condicoes_de_voo
        )

        fig_1, axs_1 = plt.subplots(1,1)
        axs_1.plot(
            resultados["razão de avanço"], resultados["resultados Ct"], '--o', color='blue'
        )
        axs_1.set(xlabel=r"$J$", ylabel=r"$C_T$")
        axs_1.grid()

        if not self.gerador_graficos_externo:
            fig_1.savefig(f'{self.path_local_cenario}/graficos/CT_vs_J.jpeg', dpi=300)
        else:
            fig_1.savefig(f'{self.path_local_cenario}/graficos_extras/CT_vs_J.jpeg', dpi=300)

        fig_2, axs_2 = plt.subplots(1,1)
        axs_2.plot(
            resultados["razão de avanço"], resultados["resultados Cq"], '--o', color='red'
        )
        axs_2.set(xlabel=r"$J$", ylabel=r"$C_Q$")
        axs_2.grid()

        if not self.gerador_graficos_externo:
            fig_2.savefig(f'{self.path_local_cenario}/graficos/CQ_vs_J.jpeg', dpi=300)
        else:
            fig_2.savefig(f'{self.path_local_cenario}/graficos_extras/CQ_vs_J.jpeg', dpi=300)

        fig_3, axs_3 = plt.subplots(1,1)
        axs_3.plot(
            resultados["razão de avanço"], resultados["resultados eficiencia"], '--o', color='orange'
        )
        axs_3.set(xlabel=r"$J$", ylabel=r"$\eta$")
        axs_3.grid()

        if not self.gerador_graficos_externo:
            fig_3.savefig(f'{self.path_local_cenario}/graficos/eta_vs_J.jpeg', dpi=300)
        else:
            fig_3.savefig(f'{self.path_local_cenario}/graficos_extras/eta_vs_J.jpeg', dpi=300)


    def gerar_grafico_beta_por_r(self):
        nomes_betas = [f"Beta {secao}" for secao in range(8)]
        betas = self.df_melhor_particula.loc[:, nomes_betas].values.tolist()[0]
        raio = self.condicoes_geometricas["raio"]

        fig, ax = plt.subplots(1,1)
        ax.plot(
            raio, betas, '--o', color="blue"
        )
        ax.grid()
        ax.set(xlabel=r"$Raio [m]$", ylabel=r"$\beta$")
        fig.savefig(f'{self.path_local_cenario}/graficos/beta_vs_r.jpeg', dpi=300)


    def gerar_grafico_caminho_particula_unica(self):
        if self.particula_escolhida is not None:
            selecao = self.df_pso["particula"] == self.particula_escolhida
            df_pso_particula = self.df_pso[selecao]
        else:
            particula = self.df_pso["particula"].sample().values[0]
            selecao = self.df_pso["particula"] == particula
            df_pso_particula = self.df_pso[selecao]        
        
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
            df_pso_particula.rename(
                columns={
                    coluna: f"Escalar Ay seção {num_escalar}"
                },
                inplace=True
            )

        df_pso_particula.rename(
            columns={
                "iteracao": "Iteração"
            },
            inplace=True
        )

        for num_secao in range(6):
            fig = px.scatter(
                data_frame=df_pso_particula,
                x=f"Escalar Ay seção {num_secao+1}",
                y=f"Escalar Ay seção {num_secao+2}",
                color="Iteração",
                color_continuous_scale=px.colors.diverging.Spectral
            )
            if self.particula_escolhida is None:
                fig.write_image(
                    f"{self.path_local_cenario}/graficos/Escalar {num_secao+1} vs Escalar {num_secao+2} particula {particula} por iteracao.jpeg"
                )
            else:
                fig.write_image(
                    f"{self.path_local_cenario}/graficos_extras/Escalar {num_secao+1} vs Escalar {num_secao+2} particula {self.particula_escolhida} por iteracao.jpeg"
                )