from genericpath import isfile
import numpy as np
import xfoil_funcao as xfoil
import os
import pandas as pd

class helice:
    def __init__(
        self,
        Aerofolios,
        Velocidade_da_aeronave: float,
        Viscosidade_dinamica: float,
        Temperatura: float,
        Densidade_do_ar: float,
        Diametro_helice: float,
        Numero_de_pas: int,
        Array_raio_da_secao: list,
        Array_tamanho_de_corda_da_secao: list,
        Array_angulo_beta_da_secao: list,
        Rotacao_motor: float,
        ler_coord_arq_ext: bool=False,
        ligar_solucao_aerof_naca: bool=False,
    ):
        # Inicialização dos parâmetros de input
        self.aerof = Aerofolios
        self.v = Velocidade_da_aeronave
        self.mi = Viscosidade_dinamica
        self.T = Temperatura
        self.rho = Densidade_do_ar
        self.D = Diametro_helice
        self.n = Numero_de_pas
        self.r = Array_raio_da_secao
        self.c = Array_tamanho_de_corda_da_secao
        self.beta = Array_angulo_beta_da_secao
        self.rpm = Rotacao_motor
        self.ler = ler_coord_arq_ext
        self.solucao_naca = ligar_solucao_aerof_naca

    def integracao(self, f, x):
        """
        Função com objetivo de realizar a integração numérica dos dados inputados
        """
        I = 0.0

        for i in range(1, len(x)):
            I += (x[i] - x[i - 1]) * (f[i] + f[i - 1]) / 2.0

        return I

    def rodar_xfoil(self, aerofolio, re, alpha, Ma):
        """
        Função com objetivo de rodar os dados no xfoil, chamando uma função externa.

        Pode=se utilizar duas análises para as rodagens: análise com viscosidade, sem viscosidade; prioridade será viscosa

        Caso Mach maior que 1 ou não convergência dos dados, será utililzado como padrão: CL=0 e CD=1
        """

        def solucao_1():
            # Tentativa de rodar solução viscosa
            xfoil.rodar_xfoil(
                aerofolio,
                str(alpha),
                str(alpha),
                "0",
                str(re),
                str(Ma),
                "9",
                "500",
                "arquivo_dados_s1.txt",
                mudar_paineis=True,
                mostrar_grafico=False,
                ler_arquivo_coord=self.ler,
                compressibilidade=False,
                solucao_viscosa=True,
                solucoes_NACA=self.solucao_naca
            )

            dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
            os.remove("arquivo_dados_s1.txt")

            if dados.size != 0:
                cl = dados[1]
                cd = abs(dados[2])

                cl = cl / (np.sqrt(1 - Ma**2))
                cd = cd / (np.sqrt(1 - Ma**2))
                
                return cl, cd
            else:
                return 0, 0
        
        if (Ma < 1):
            cl, cd = solucao_1()
        elif (Ma > 0):
            cl = 0
            cd = 1
        else:
            cl = 0
            cd = 1

        return cl, cd

    def rodar_helice(self):
        J = 60 * self.v / (self.rpm * self.D)
        
        # Pressão Dinâmica
        q = 0.5 * self.rho * self.v**2

        # Velocidade Tangencial
        vt = 2.0 * np.pi / 60.0 * self.rpm * self.r

        # Ângulo phi de cada seção
        phi = np.arctan(self.v / vt)
        phi[-1] = 0.0

        # Velocidade resultante
        vr = vt / np.cos(phi)

        # Ângulo de ataque de cada seção
        # alpha = self.alpha.copy()
        # alpha_rad = self.alpha * np.pi / 180
        # beta = alpha_rad + phi

        beta = self.beta.copy()
        alpha_rad = beta - phi
        alpha_deg = alpha_rad*180/np.pi

        dT = []
        dQ = []
        r_new = []

        # Cálculo para cada seção
        for i in range(len(self.aerof) - 1):
            reynolds = self.rho * self.v * self.D / self.mi
            Ma = vr[i] / (np.sqrt(1.4 * 287 * self.T))

            coef_l, coef_d = self.rodar_xfoil(
                self.aerof[i], round(reynolds, 0), alpha_deg[i], Ma
            )
 
            if coef_l != 0:
                gamma = np.arctan(coef_d/coef_l)

                dt = q*coef_l*self.c[i]*(np.cos(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                dq = q*coef_l*self.c[i]*self.r[i]*(np.sin(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                
                dT.append(dt)
                dQ.append(dq)

                r_new.append(self.r[i])

        dT.append(0)
        dQ.append(0)

        r_new.append(self.r[-1])

        T = self.integracao(np.array(dT), r_new) * self.n
        Q = self.integracao(np.array(dQ), r_new) * self.n

        n = self.rpm / 60

        Ct = T/(self.rho * n**2 * self.D**4)
        Cq = Q/(self.rho * n**2 * self.D**5)

        Cp = 2 * np.pi * Cq

        # if Cp != 0:
        #     eta = J * Ct / Cp
        # else:
        #     eta = 0

        if Q != 0:
            eta = T * self.v / (2 * np.pi / 60 * self.rpm * Q)
        else:
            eta = 0

        resultados = {
            "velocidade": [self.v],
            "rpm": [self.rpm],
            "J": [J],
            "eta": [eta],
            "T": [T],
            "Q": [Q],
            "Cp": [Cp],
            "Ct": [Ct],
            "Cq": [Cq]
        }

        for al in range(len(alpha_deg)):
            resultados[f"Alpha {al}"] = alpha_deg[al]

        for bet in range(len(beta)):
            resultados[f"Beta {bet}"] = beta[bet] * 180 / np.pi

        if not os.path.isfile(f"Resultados-validacao-helice.csv"):
            df = pd.DataFrame(resultados)
            df.to_csv(f"Resultados-validacao-helice.csv", sep=';', index=False)
        else:
            df = pd.read_csv(f"Resultados-validacao-helice.csv", sep=';')
            df_resultados = pd.DataFrame(resultados)
            df = pd.concat(
                [df, df_resultados],
                ignore_index=True
            )
            df.to_csv(f"Resultados-validacao-helice.csv", sep=';', index=False)


condicao_de_voo = {
    "Velocidade": 3,
    "Viscosidade": 1.789e-5,
    "Temperatura": 288.2,
    "Densidade do Ar": 1.225,
    "Diametro da Helice": 96*0.0254,
    "Numero de pas": 2,
    "Rotacao do Motor": 1000.
}

diametro = 2
raio_R = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
raio = raio_R * diametro / 2
c_D = np.array([
    0.05313,
    0.06913,
    0.07602,
    0.07337,
    0.06593,
    0.05627,
    0.04461,
    0
])
c = c_D * diametro
beta = np.array([
    41.95,
    36.96,
    31.96,
    28.49,
    26.01,
    24.19,
    22.77,
    0
]) * np.pi / 180

velocidades = list(np.linspace(1,100,200))

aerofolios = [f"aerofolio_{aer}.txt" for aer in range(8)]
# velocidades = [vel for vel in range(5, 100, )]

for velocidade in velocidades:
    helice(
        Aerofolios=aerofolios,
        Velocidade_da_aeronave=velocidade,
        Viscosidade_dinamica=condicao_de_voo["Viscosidade"],
        Temperatura=condicao_de_voo["Temperatura"],
        Densidade_do_ar=condicao_de_voo["Densidade do Ar"],
        Diametro_helice=diametro,
        Numero_de_pas=2,
        Array_raio_da_secao=raio,
        Array_tamanho_de_corda_da_secao=c,
        Array_angulo_beta_da_secao=beta,
        Rotacao_motor=condicao_de_voo["Rotacao do Motor"],
        ler_coord_arq_ext=True,
        ligar_solucao_aerof_naca=False,
    ).rodar_helice()