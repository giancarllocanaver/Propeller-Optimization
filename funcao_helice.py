import numpy as np
import xfoil_funcao as xfoil
import os


class helice:
    def __init__(
        self,
        Aerofolios,
        Velocidade_da_aeronave,
        Viscosidade_dinamica,
        Temperatura,
        Densidade_do_ar,
        Diametro_helice,
        Numero_de_pas,
        Array_raio_da_secao,
        Array_tamanho_de_corda_da_secao,
        Array_angulo_beta_da_secao,
        Rotacao_motor,
        ler_coord_arq_ext=False,
        validacao=None,
    ):

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
        self.df_val = validacao

    def integracao(self, f, x):

        I = 0.0

        for i in range(1, len(x)):
            I += (x[i] - x[i - 1]) * (f[i] + f[i - 1]) / 2.0

        return I

    def rodar_xfoil(aerofolio, re, alpha, Ma):
        if (Ma < 1) and (alpha <= 20 and alpha >= -20):
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

            if dados_v.size != 0:
                cl = dados_v[1]
                cd = abs(dados_v[2])

                cl = cl / (np.sqrt(1 - Ma**2))
                cd = cd / (np.sqrt(1 - Ma**2))

                if self.df_val != None:
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

                    if self.df_val != None:
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

                    if self.df_val != None:
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

            if self.df_val != None:
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

    def rodar_helice(self, integracao, rodar_xfoil):
        q = 0.5 * self.rho * self.v**2  # Pressão Dinâmica

        vt = 2.0 * np.pi / 60.0 * self.rpm * self.r  # Velocidade Tangencial

        phi = np.arctan(self.v / vt)
        phi[-1] = 0.0

        vr = vt / np.cos(phi)  # Velocidade Resultante

        alpha_np = (self.beta - phi) * 180 / np.pi
        alpha = [round(i, 2) for i in alpha_np]

        alpha[-1] = 0.0

        dCT = []
        dCQ = []
        r_new = []

        for i in range(len(self.aerof) - 1):
            reynolds = self.rho * vr[i] * self.c[i] / self.mi
            Ma = vr[i] / (np.sqrt(1.4 * 287 * self.T))

            coef_l, coef_d = rodar_xfoil(
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

        coef_T = integracao(np.array(dCT), r_new) * self.n
        coef_Q = integracao(np.array(dCQ), r_new) * self.n

        if coef_T > 0 and coef_Q > 0:
            coef_P = 2 * np.pi * coef_Q

            eta = J * coef_T / coef_P
        else:
            eta = 0.1

        if self.df_val != None:
            return eta, self.df_val
        else:
            return eta
