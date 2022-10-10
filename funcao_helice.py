import re
import numpy as np
import xfoil_funcao as xfoil
import os
import pandas as pd
from scipy.interpolate import interp1d
import time

class Helice:
    def __init__(
        self,
        aerofolios: list,
        condicoes_voo: dict,
        condicoes_geometricas_helice: dict,
        particula_com_interseccao: bool=False
    ):
        self.aerof = aerofolios
        self.v = condicoes_voo["Velocidade"]
        self.mi = condicoes_voo["Viscosidade"]
        self.T = condicoes_voo["Temperatura"]
        self.rho = condicoes_voo["Densidade do Ar"]
        self.D = condicoes_voo["Diametro da Helice"]
        self.n = condicoes_voo["Numero de pas"]
        self.rpm = condicoes_voo["Rotacao do Motor"]
        self.r = condicoes_geometricas_helice["Raio Secao"]
        self.c = condicoes_geometricas_helice["Corda Secao"]
        self.solucao_interseccao = particula_com_interseccao

        self.vt = None
        self.J = None
        self.vr = None
        self.reynolds = None
        self.ma = None
        self.cl = None
        self.cd = None
        self.gamma = None
        self.eficiencia = None

        self.calcular_velocidade_tangencial()
        self.calcular_razao_de_avanco()
        self.calcular_phi()
        self.calcular_vr()
        self.calcular_reynolds()
        self.calcular_mach()

        if not particula_com_interseccao:
            self.calcular_cl_cd_alpha_5()
            self.calcular_gamma()
            self.calcular_eficiencia()
            self.computar_resultados()
        else:
            self.computar_resultados_interseccao()


    def calcular_velocidade_tangencial(self):
        self.vt = 2.0 * np.pi / 60.0 * self.rpm * self.r
    

    def calcular_razao_de_avanco(self):
        self.J = 60 * self.v / (self.rpm * self.D)


    def calcular_phi(self):
        phi = np.arctan(self.v / self.vt)
        phi[-1] = 0.

        self.phi = phi


    def calcular_vr(self):
        self.vr = self.vt / np.cos(self.phi)


    def calcular_reynolds(self):
        self.reynolds = self.rho * self.v * self.D / self.mi


    def calcular_mach(self):
        Ma = self.vr / (np.sqrt(1.4 * 287 * self.T))
        self.ma = Ma.max()


    def calcular_cl_cd_alpha_5(self):
        xfoil.rodar_xfoil(
            self.aerof[4],
            str(5),
            str(5),
            "0",
            str(self.reynolds),
            str(self.ma),
            "9",
            "200",
            "arquivo_dados_s1.txt",
            mudar_paineis=True,
            mostrar_grafico=False,
            ler_arquivo_coord=True,
            compressibilidade=False,
            solucao_viscosa=True,
            solucoes_NACA=False
        )

        dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
        os.remove("arquivo_dados_s1.txt")

        if (dados.size != 0) & (self.ma < 1):
            cl = dados[1]
            cd = abs(dados[2])

            cl = cl / (np.sqrt(1 - self.ma**2))
            cd = cd / (np.sqrt(1 - self.ma**2))
        else:
            cl = 0
            cd = 1

        self.cl = cl
        self.cd = cd


    def calcular_gamma(self):
        if self.cl != 0:
            self.gamma = np.arctan(self.cd/self.cl)


    def calcular_eficiencia(self):
        if self.gamma is not None:
            self.eficiencia = np.tan(self.phi[4]) / np.tan(self.phi[4] + self.gamma)
        else:
            self.gamma = 0


    def computar_resultados(self):
        if self.eficiencia is not None:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [self.J],
                "reynolds": [self.reynolds],
                "mach": [self.ma],
                "eficiencia": [self.eficiencia]
            }
        else:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [self.J],
                "reynolds": [self.reynolds],
                "mach": [self.ma],
                "eficiencia": [0]
            }

        self.resultados = resultados


    def computar_resultados_interseccao(self):
        resultados = {
            "velocidade": [self.v],
            "rpm": [self.rpm],
            "J": [self.J],
            "reynolds": [self.reynolds],
            "mach": [self.ma],
            "eficiencia": [0]
        }

        self.resultados = resultados