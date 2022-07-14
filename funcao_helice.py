import numpy as np
import xfoil_funcao as xfoil
import os
import pandas as pd

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
        self.df_val: DataFrame contendo os resultados do xfoil (somente será gerado caso 'validacao' for verdadeiro)
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
        Array_angulo_beta_da_secao: list,
        Rotacao_motor: float,
        ler_coord_arq_ext=False,
        validacao=False,
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
        self.bool_val = False
        
        # Caso o usuário queira ver validação, gera-se um DataFrame vazio
        if validacao == True:
            self.df_val = pd.DataFrame(
                {"Velocidade": [], "RPM": [], "Alpha": [], "Re": [], "Cl": [], "Cd": [], "Tipo": []}
            )
            self.bool_val = True

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
        if (Ma < 1) and (alpha <= 20 and alpha >= -20):
            # Tentativa de rodar solução viscosa
            xfoil.rodar_xfoil(
                aerofolio,
                str(alpha),
                str(alpha),
                "0",
                str(re),
                str(Ma),
                "9",
                "100",
                "arquivo_dados_v.txt",
                mudar_paineis=True,
                mostrar_grafico=False,
                ler_arquivo_coord=self.ler,
                compressibilidade=False,
                solucao_viscosa=True,
            )

            dados_v = np.loadtxt("arquivo_dados_v.txt", skiprows=12)
            os.remove("arquivo_dados_v.txt")

            # Sucesso na solução viscosa
            if dados_v.size != 0:
                cl = dados_v[1]
                cd = abs(dados_v[2])

                cl = cl / (np.sqrt(1 - Ma**2))
                cd = cd / (np.sqrt(1 - Ma**2))

                if self.bool_val == True:
                    self.df_val = self.df_val.append(
                        pd.DataFrame(
                            {
                                "Velocidade": [self.v],
                                "RPM": [self.rpm],
                                "Alpha": [alpha],
                                "Re": [re],
                                "Cl": [cl],
                                "Cd": [cd],
                                "Tipo": ["Solucao viscosa"],
                            }
                        ),
                        ignore_index=True,
                    )

            # Fracasso na solução viscosa:
            if dados_v.size == 0:
                xfoil.rodar_xfoil(
                    aerofolio,
                    str(alpha),
                    str(alpha),
                    "0",
                    str(re),
                    str(Ma),
                    "9",
                    "100",
                    "arquivo_dados_i.txt",
                    mudar_paineis=True,
                    mostrar_grafico=False,
                    ler_arquivo_coord=self.ler,
                    compressibilidade=False,
                    solucao_viscosa=False,
                )

                dados_i = np.loadtxt("arquivo_dados_i.txt", skiprows=12)
                os.remove("arquivo_dados_i.txt")

                cl = dados_i[1]
                cd = abs(dados_i[3])

                if dados_i.size != 0:
                    cl = cl / (np.sqrt(1 - Ma**2))
                    cd = cd / (np.sqrt(1 - Ma**2))

                    if self.bool_val == True:
                        self.df_val = self.df_val.append(
                            pd.DataFrame(
                                {
                                    "Velocidade": [self.v],
                                    "RPM": [self.rpm],
                                    "Alpha": [alpha],
                                    "Re": [re],
                                    "Cl": [cl],
                                    "Cd": [cd],
                                    "Tipo": ["Solucao inviscida"],
                                }
                            ),
                            ignore_index=True,
                        )
                else:
                    cl = 0
                    cd = 1

                    if self.bool_val == True:
                        self.df_val = self.df_val.append(
                            pd.DataFrame(
                                {
                                    "Velocidade": [self.v],
                                    "RPM": [self.rpm],
                                    "Alpha": [alpha],
                                    "Re": [re],
                                    "Cl": [cl],
                                    "Cd": [cd],
                                    "Tipo": ["Solucao não encontrada - tipo 1"],
                                }
                            ),
                            ignore_index=True,
                        )
        else:
            cl = 0
            cd = 1

            if self.bool_val == True:
                self.df_val = self.df_val.append(
                    pd.DataFrame(
                        {
                            "Velocidade": [self.v],
                            "RPM": [self.rpm],
                            "Alpha": [alpha],
                            "Re": [re],
                            "Cl": [0],
                            "Cd": [1],
                            "Tipo": ["Solucao não encontrada - tipo 2"],
                        }
                    ),
                    ignore_index=True,
                )

        return cl, cd

    def rodar_helice(self):
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
        alpha_np = (self.beta - phi) * 180 / np.pi
        alpha = [round(i, 2) for i in alpha_np]
        alpha[-1] = 0.0

        dCT = []
        dCQ = []
        r_new = []

        # Cálculo para cada seção
        for i in range(len(self.aerof) - 1):
            reynolds = self.rho * vr[i] * self.c[i] / self.mi
            Ma = vr[i] / (np.sqrt(1.4 * 287 * self.T))

            coef_l, coef_d = self.rodar_xfoil(
                self.aerof[i], round(reynolds, 0), alpha[i], Ma
            )

            sigma_R = self.n * self.c[i] / (np.pi * self.r[i])
            J = 60 * self.v / (self.rpm * self.D)
            coef_T = (
                np.pi
                / 8
                * sigma_R
                * J**2
                * (coef_l * np.cos(phi[i]) - coef_d * np.sin(phi[i]))
                / (np.sin(phi[i]) ** 2)
            )
            x = self.r[i] / (self.D / 2)
            coef_Q = (
                np.pi
                / 16
                * sigma_R
                * J**2
                * x
                * (coef_l * np.sin(phi[i]) + coef_d * np.cos(phi[i]))
                / (np.sin(phi[i]) ** 2)
            )

            dCT.append(coef_T)
            dCQ.append(coef_Q)

            r_new.append(self.r[i])

        dCT.append(0)
        dCQ.append(0)

        r_new.append(self.r[-1])

        coef_T = self.integracao(np.array(dCT), r_new) * self.n
        coef_Q = self.integracao(np.array(dCQ), r_new) * self.n

        if coef_T > 0 and coef_Q > 0:
            coef_P = 2 * np.pi * coef_Q

            eta = J * coef_T / coef_P
        else:
            eta = 0.1

        if self.bool_val == True:
            return eta, self.df_val
        else:
            return eta