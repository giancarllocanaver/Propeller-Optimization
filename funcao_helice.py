import numpy as np
import xfoil_funcao as xfoil
import os
import pandas as pd
from scipy.interpolate import interp1d
import time

class helice:
    """
    -------------------
    FUNÇÃO HELICE
    -------------------

    Objetivo: Calcular a eficiência de uma determinada hélice como um todo.

    Parâmetros de input:
        Aerofolios: Lista das coordenadas do aerofólio ou nome do arquivo a ser lido (especificação dada pelo parâmetro 'ler_coord_arq_ext'); a lista deve ter tamanho igual a quantidade de seções
        Velocidade_da_aeronave:Velocidade da aeronave em m/s
        Viscosidade_dinamica: Viscodiade dinâmica do ar em 1/ms
        Temperatura: Temperatura do ar em K
        Densidade_do_ar: Densidade do ar em kg/m3
        Diametro_helice: Diâmetro da hélice em m
        Numero_de_pas: Quantidade de pás
        Array_raio_da_secao: Lista com as coordenadas do raio das seções em m
        Array_tamanho_de_corda_da_secao: Lista com o tamanho da corda de cada seção em m
        Array_angulo_beta_da_secao: Ângulo de cada seção em rad
        Rotacao_motor: Rotação do motor em rpm
        ler_coord_arq_ext=False: Leitura das coordenadas do aerofólio em um arquivo (por definição é falso)
        validacao=False: Geração de um arquivo externo para possível vizualização dos resultados do xfoil (por definição é falso)
    
    Parâmetros de output:
        eta: Eficiência da hélice
        self.df_val_aerof: DataFrame contendo os resultados do xfoil (somente será gerado caso 'validacao' for verdadeiro)
        self.df_val_helice: DataFrame contendo os resultados para a hélice como um todo
    """
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
        Array_angulo_alpha_da_secao: list,
        Rotacao_motor: float,
        Solucoes_ligadas: list=['solucao_1', 'solucao_2', 'solucao_3'],
        ler_coord_arq_ext: bool=False,
        condicao_cl_grande: bool=False,
        ligar_interpolacao_2a_ordem: bool=False,
        ligar_solucao_aerof_naca: bool=False,
        particula_com_interseccao: bool=False
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
        self.alpha = Array_angulo_alpha_da_secao
        self.rpm = Rotacao_motor
        self.solucoes = Solucoes_ligadas
        self.ler = ler_coord_arq_ext
        self.condicao_cl = condicao_cl_grande
        self.condicao_2a_ordem = ligar_interpolacao_2a_ordem
        self.solucao_naca = ligar_solucao_aerof_naca
        self.solucao_interseccao = particula_com_interseccao
        self.solucao_aerofolio_unico = True
        

    def integracao(self, f, x):
        """
        Função com objetivo de realizar a integração numérica dos dados inputados
        """
        I = 0.0

        for i in range(1, len(x)):
            I += (x[i] - x[i - 1]) * (f[i] + f[i - 1]) / 2.0

        return I


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

        if self.solucao_interseccao:
            resultados = {
                "velocidade": [self.v],
                "rpm": [self.rpm],
                "J": [J],
                "eta": [0],
                "T": [0],
                "Q": [0],
                "Cp": [0],
                "Ct": [0],
                "Cq": [0]
            }
            
            for al in range(len(self.alpha)):
                resultados[f"Alpha {al}"] = self.alpha[al]

            for bet in range(len(beta)):
                resultados[f"Beta {bet}"] = beta[bet] * 180 / np.pi
            return resultados

        dT = []
        dQ = []
        r_new = []

        # Cálculo para cada seção
        for i in range(len(self.aerof) - 1):
            reynolds = self.rho * vr[i] * self.c[i] / self.mi
            Ma_1 = vr[i] / (np.sqrt(1.4 * 287 * self.T))
            Ma_2 = self.v / (np.sqrt(1.4 * 287 * self.T))

            Ma_array = np.array([Ma_1, Ma_2])

            coef_l, coef_d = self.descobrir_alpha_mais_eficiente(
                aerofolio=self.aerof[i],
                re=reynolds,
                Ma=Ma_array.max()
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

        if Cp != 0:
            eta = J * Ct / Cp
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

        for al in range(len(alpha)):
            resultados[f"Alpha {al}"] = alpha[al]

        for bet in range(len(beta)):
            resultados[f"Beta {bet}"] = beta[bet] * 180 / np.pi

        return resultados


    def descobrir_alpha_mais_eficiente(self, aerofolio, re, Ma):
        cl_cd_best = 0
        if Ma < 1:
            for alpha in range(0,11):
                xfoil.rodar_xfoil(
                    aerofolio,
                    str(alpha),
                    str(alpha),
                    "0",
                    str(re),
                    str(Ma),
                    "9",
                    "100",
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
                    
                    cl_cd = cl / cd

                    if cl_cd > cl_cd_best:
                        cl_cd_best = cl_cd                    
                        melhor_alpha = alpha
                        cl_best = cl
                        cd_best = cd
        
        if cl_cd_best > 0:
            return cl_best, cd_best
        else:
            return 0, 1
