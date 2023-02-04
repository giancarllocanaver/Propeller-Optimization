from genericpath import isfile
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
        alpha: float,
        particula_com_interseccao: bool=False,
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
        self.alpha = alpha

        self.vt = None
        self.J = None
        self.vr = None
        self.reynolds = None
        self.ma = None
        self.cl = None
        self.cd = None
        self.gamma = []
        self.eficiencia = None
        self.dT = []
        self.dQ = []
        self.beta = []
        self.r_integrar = []
        self.cl = []
        self.cd = []

        self.calcular_velocidade_tangencial()
        self.calcular_razao_de_avanco()
        self.calcular_phi()
        self.calcular_vr()
        self.calcular_reynolds()
        self.calcular_mach()

        if not particula_com_interseccao:
            self.calcular_cl_cd_alpha_5()
            self.calcular_gamma()
            self.calcular_dt_e_dq()
            self.calcular_eficiencia()
            self.calcular_beta()
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
        for aerofolio in self.aerof:
            xfoil.rodar_xfoil(
                aerofolio,
                str(self.alpha),
                str(self.alpha),
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

            encontrou = 0
            try:
                dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
                encontrou = 1
            except (OSError, Exception):
                time.sleep(0.5)
            
            try:
                dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
                encontrou = 1
            except (OSError, Exception):
                cl = 0
                cd = 1
            
            if os.path.isfile("arquivo_dados_s1.txt"):
                os.remove("arquivo_dados_s1.txt")

            if encontrou:
                if (dados.size != 0) & (self.ma < 1):
                    cl = dados[1]
                    cd = abs(dados[2])

                    cl = cl / (np.sqrt(1 - self.ma**2))
                    cd = cd / (np.sqrt(1 - self.ma**2))
                else:
                    cl = 0
                    cd = 1
            else:
                cl = 0
                cd = 1

            self.cl.append(cl)
            self.cd.append(cd)


    def calcular_gamma(self):
        for secao in range(len(self.cl)):
            if self.cl[secao] != 0:
                self.gamma.append(np.arctan(self.cd[secao]/self.cl[secao]))
            else:
                self.gamma.append(None)


    def calcular_dt_e_dq(self):
        q = 0.5 * self.rho * self.v**2
        
        for secao in range(len(self.phi) - 1):
            if self.gamma[secao] != None:
                dt = q*self.cl[secao]*self.c[secao]*(np.cos(self.phi[secao] + self.gamma[secao]))/(np.cos(self.gamma[secao])*np.sin(self.phi[secao])**2)
                dq = q*self.cl[secao]*self.c[secao]*self.r[secao]*(np.sin(self.phi[secao] + self.gamma[secao]))/(np.cos(self.gamma[secao])*np.sin(self.phi[secao])**2)

                self.dT.append(dt)
                self.dQ.append(dq)
            else:
                self.dT.append(0)
                self.dQ.append(0)
        
        self.dT.append(0)
        self.dQ.append(0)


    def integracao(self, f, x):
        """
        Função com objetivo de realizar a integração numérica dos dados inputados
        """
        I = 0.0

        for i in range(1, len(x)):
            I += (x[i] - x[i - 1]) * (f[i] + f[i - 1]) / 2.0

        return I


    def calcular_eficiencia(self):
        if len(self.dT) == len(self.r):
            T = self.integracao(self.dT, self.r)
            Q = self.integracao(self.dQ, self.r)
        
            n = self.rpm / 60

            self.Ct = T/(self.rho * n**2 * self.D**4)
            self.Cq = Q/(self.rho * n**2 * self.D**5)
            self.Cp = 2 * np.pi * self.Cq

            self.T = T
            self.Q = Q
        else:
            T = 0
            Q = 0

            self.Ct = 0
            self.Cq = 0
            self.Cp = 0

            self.T = T
            self.Q = Q

        if self.Cp != 0:
            self.eficiencia = self.J * self.Ct / self.Cp
        else:
            self.gamma = 0


    def calcular_beta(self):
        self.beta = 5/180*np.pi + self.phi


    def computar_resultados(self):
        if self.eficiencia is not None:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [self.J],
                "reynolds": [self.reynolds],
                "mach": [self.ma],
                "eficiencia": [self.eficiencia],
                "tracao": [self.T],
                "torque": [self.Q],
                "Ct": self.Ct,
                "Cq": self.Cq,
                "Cp": self.Cp
            }

            for bet in range(len(self.beta)):
                resultados[f"Beta {bet}"] = self.beta[bet] * 180 / np.pi

            for secao in range(len(self.aerof)):
                resultados[f"Aerofolio secao {secao}"] = self.aerof[secao]

            for diferencial in range(len(self.dT)):
                resultados[f"dT Seção {diferencial}"] = self.dT[diferencial]
            
            for diferencial in range(len(self.dQ)):
                resultados[f"dQ Seção {diferencial}"] = self.dQ[diferencial]

            for diferencial in range(len(self.r)):
                resultados[f"dr Seção {diferencial}"] = self.r[diferencial]

            for corda in range(len(self.c)):
                resultados[f"c Seção {corda}"] = self.c[corda]
        else:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [self.J],
                "reynolds": [self.reynolds],
                "mach": [self.ma],
                "eficiencia": [0],
                "tracao": [self.T],
                "torque": [self.Q],
                "Ct": self.Ct,
                "Cq": self.Cq,
                "Cp": self.Cp
            }

            for bet in range(len(self.beta)):
                resultados[f"Beta {bet}"] = self.beta[bet] * 180 / np.pi
            
            for secao in range(len(self.aerof)):
                resultados[f"Aerofolio secao {secao}"] = self.aerof[secao]
            
            for diferencial in range(len(self.dT)):
                resultados[f"dT Seção {diferencial}"] = 0
            
            for diferencial in range(len(self.dQ)):
                resultados[f"dQ Seção {diferencial}"] = 0

            for diferencial in range(len(self.r)):
                resultados[f"dr Seção {diferencial}"] = self.r[diferencial]

            for corda in range(len(self.c)):
                resultados[f"c Seção {corda}"] = self.c[corda]

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




class HeliceGeral:
    def __init__(
        self,
        aerofolios: list,
        condicoes_geometricas: dict,
        condicoes_de_voo: dict,
        **kwargs      
    ):
        self.aerofolios = aerofolios
        self.v = condicoes_de_voo["Velocidade"]
        self.mi = condicoes_de_voo["Viscosidade"]
        self.T = condicoes_de_voo["Temperatura"]
        self.rho = condicoes_de_voo["Densidade do Ar"]
        self.D = condicoes_de_voo["Diametro da Helice"]
        self.n = condicoes_de_voo["Numero de pas"]
        self.rpm = condicoes_de_voo["Rotacao do Motor"]
        self.r = condicoes_geometricas["Raio Secao"]
        self.c = condicoes_geometricas["Corda Secao"]
        self.beta = condicoes_geometricas["Beta"]

        self.cl = []
        self.cd = []
        self.gamma = []
        self.dT = []
        self.dQ = []

        self.eficiencia = None

        self.calcular_velocidade_tangencial()
        self.calcular_razao_de_avanco()
        self.calcular_phi()
        self.calcular_vr()
        self.calcular_reynolds()
        self.calcular_mach()
        self.calcular_alpha()
        self.calcular_cl_e_cd()
        self.calcular_gamma()
        self.calcular_dt_e_dq()
        self.calcular_eficiencia()
        self.computar_resultados()

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


    def calcular_alpha(self):
        self.beta = self.beta * np.pi / 180
        self.alpha = self.beta - self.phi
        self.alpha = self.alpha * 180 / np.pi


    def calcular_cl_e_cd(self):
        for secao in range(len(self.aerofolios)):       
            xfoil.rodar_xfoil(
                self.aerofolios[secao],
                str(self.alpha[secao]),
                str(self.alpha[secao]),
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

            encontrou = 0

            try:
                dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
                encontrou = 1
            except OSError:
                time.sleep(0.5)
            
            try:
                dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
                encontrou = 1
            except (OSError, Exception):
                cl = 0
                cd = 1
            
            if os.path.isfile("arquivo_dados_s1.txt"):
                os.remove("arquivo_dados_s1.txt")

            if encontrou:
                if (dados.size != 0) & (self.ma < 1):
                    cl = dados[1]
                    cd = abs(dados[2])

                    cl = cl / (np.sqrt(1 - self.ma**2))
                    cd = cd / (np.sqrt(1 - self.ma**2))
                else:
                    cl = 0
                    cd = 1
            else:
                cl=0
                cd=1

            self.cl.append(cl)
            self.cd.append(cd)


    def calcular_gamma(self):
        for secao in range(len(self.cl)):
            if self.cl[secao] != 0:
                self.gamma.append(np.arctan(self.cd[secao]/self.cl[secao]))
            else:
                self.gamma.append(None)


    def calcular_dt_e_dq(self):
        q = 0.5 * self.rho * self.v**2
        
        for secao in range(len(self.aerofolios)):
            if self.gamma[secao] != None:
                dt = q*self.cl[secao]*self.c[secao]*(np.cos(self.phi[secao] + self.gamma[secao]))/(np.cos(self.gamma[secao])*np.sin(self.phi[secao])**2)
                dq = q*self.cl[secao]*self.c[secao]*self.r[secao]*(np.sin(self.phi[secao] + self.gamma[secao]))/(np.cos(self.gamma[secao])*np.sin(self.phi[secao])**2)

                self.dT.append(dt)
                self.dQ.append(dq)
            else:
                self.dT.append(0)
                self.dQ.append(0)
        
        self.dT.append(0)
        self.dQ.append(0)

    
    def integracao(self, f, x):
        I = 0.0
        for i in range(1, len(x)):
            I += (x[i] - x[i - 1]) * (f[i] + f[i - 1]) / 2.0

        return I


    def calcular_eficiencia(self):
        if len(self.dT) == len(self.r):
            T = self.integracao(self.dT, self.r)
            Q = self.integracao(self.dQ, self.r)
        
            n = self.rpm / 60

            self.Ct = T/(self.rho * n**2 * self.D**4)
            self.Cq = Q/(self.rho * n**2 * self.D**5)
            self.Cp = 2 * np.pi * self.Cq

            self.T = T
            self.Q = Q
        else:
            T = 0
            Q = 0

            self.Ct = 0
            self.Cq = 0
            self.Cp = 0

            self.T = T
            self.Q = Q

        if self.Cp != 0:
            self.eficiencia = self.J * self.Ct / self.Cp
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
                "eficiencia": [self.eficiencia],
                "tracao": [self.T],
                "torque": [self.Q],
                "Ct": self.Ct,
                "Cq": self.Cq,
                "Cp": self.Cp
            }

            for bet in range(len(self.beta)):
                resultados[f"Beta {bet}"] = self.beta[bet] * 180 / np.pi

            for secao in range(len(self.aerofolios)):
                resultados[f"Aerofolio secao {secao}"] = self.aerofolios[secao]

            for diferencial in range(len(self.dT)):
                resultados[f"dT Seção {diferencial}"] = self.dT[diferencial]
            
            for diferencial in range(len(self.dQ)):
                resultados[f"dQ Seção {diferencial}"] = self.dQ[diferencial]

            for diferencial in range(len(self.r)):
                resultados[f"dr Seção {diferencial}"] = self.r[diferencial]

            for corda in range(len(self.c)):
                resultados[f"c Seção {corda}"] = self.c[corda]
        else:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [self.J],
                "reynolds": [self.reynolds],
                "mach": [self.ma],
                "eficiencia": [0],
                "tracao": [self.T],
                "torque": [self.Q],
                "Ct": self.Ct,
                "Cq": self.Cq,
                "Cp": self.Cp
            }

            for bet in range(len(self.beta)):
                resultados[f"Beta {bet}"] = self.beta[bet] * 180 / np.pi
            
            for secao in range(len(self.aerofolios)):
                resultados[f"Aerofolio secao {secao}"] = self.aerofolios[secao]
            
            for diferencial in range(len(self.dT)):
                resultados[f"dT Seção {diferencial}"] = 0
            
            for diferencial in range(len(self.dQ)):
                resultados[f"dQ Seção {diferencial}"] = 0

            for diferencial in range(len(self.r)):
                resultados[f"dr Seção {diferencial}"] = self.r[diferencial]

            for corda in range(len(self.c)):
                resultados[f"c Seção {corda}"] = self.c[corda]

        self.resultados = resultados