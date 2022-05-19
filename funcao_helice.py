import numpy as np
import xfoil_funcao as xfoil
import os
import pandas as pd
from scipy.interpolate import interp1d

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
        Array_angulo_beta_da_secao: list,
        Rotacao_motor: float,
        Solucoes_ligadas: list=['solucao_1', 'solucao_2', 'solucao_3'],
        ler_coord_arq_ext: bool=False,
        validacao: bool=False,
        condicao_cl_grande: bool=False,
        ligar_interpolacao_2a_ordem: bool=False
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
        self.solucoes = Solucoes_ligadas.sort()
        self.ler = ler_coord_arq_ext
        self.bool_val = False
        self.condicao_cl = condicao_cl_grande
        self.condicao_2a_ordem = ligar_interpolacao_2a_ordem
        
        # Caso o usuário queira ver validação, gera-se um DataFrame vazio
        if validacao == True:
            self.df_val_aerof = pd.DataFrame(
                {"Velocidade": [], "RPM": [], "Alpha": [], "Re": [], "Cl": [], "Cd": [], "Tipo": []}
            )

            self.df_val_helice = pd.DataFrame(
                {{"Velocidade": [], "RPM": [], "Eficiencia": []}}
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
                "100",
                "arquivo_dados_s1.txt",
                mudar_paineis=True,
                mostrar_grafico=False,
                ler_arquivo_coord=self.ler,
                compressibilidade=False,
                solucao_viscosa=True,
            )

            dados = np.loadtxt("arquivo_dados_s1.txt", skiprows=12)
            os.remove("arquivo_dados_s1.txt")

            if dados.size != 0:
                cl = dados[1]
                cd = abs(dados[2])

                cl = cl / (np.sqrt(1 - Ma**2))
                cd = cd / (np.sqrt(1 - Ma**2))
                
                return cl, cd, "Solucao viscosa sem interpolação"
            else:
                return 0, 0, "Sem solução"
        
        def solucao_2():
            delta_alpha = 0.25
            delta_parada = 0.05

            while (delta_alpha >= delta_parada):
                xfoil.rodar_xfoil(
                    aerofolio,
                    str(alpha - 5),
                    str(alpha + 5),
                    str(delta_alpha),
                    str(re),
                    str(Ma),
                    "9",
                    "100",
                    "arquivo_dados_s2.txt",
                    mudar_paineis=True,
                    mostrar_grafico=False,
                    ler_arquivo_coord=self.ler,
                    compressibilidade=False,
                    solucao_viscosa=True,
                    solucao_com_interpolacao=True
                )

                dados = np.loadtxt("arquivo_dados_s2.txt", skiprows=12)
                os.remove("arquivo_dados_s2.txt")

                try:
                    dados.shape[1]
                    delta_alpha = delta_parada
                except IndexError:
                    delta_alpha = delta_alpha - 0.05

            try:
                dados.shape[1]
                if (dados.shape[0] >= 2) and (dados.size != 0):
                    if (dados.shape[0] == 2):
                        cd = interp1d(dados[:,0], dados[:,2], kind='linear', fill_value='extrapolate')
                        cl = interp1d(dados[:,0], dados[:,1], kind='linear', fill_value='extrapolate')
                        solucao_type = "Solução viscosa com interpolação de 1ª ordem"
                    elif (dados.shape[0] == 3) and (self.ligar_interpolacao_2a_ordem):
                        cd = interp1d(dados[:,0], dados[:,2], kind='quadratic', fill_value='extrapolate')
                        cl = interp1d(dados[:,0], dados[:,1], kind='quadratic', fill_value='extrapolate')
                        solucao_type = "Solução viscosa com interpolação de 2ª ordem"
                    else:
                        cd = interp1d(dados[:,0], dados[:,2], kind='cubic', fill_value='extrapolate')
                        cl = interp1d(dados[:,0], dados[:,1], kind='cubic', fill_value='extrapolate')
                        solucao_type = "Solução viscosa com interpolação de 3ª ordem"

                    cl = cl / (np.sqrt(1 - Ma**2))
                    cd = cd(alpha) / (np.sqrt(1 - Ma**2))

                    if (self.condicao_cl == True):
                        if (cl > 2.5):
                            cl = 0.0
                
                    return cl, cd, solucao_type
                else:
                    return 0, 0, "Sem solução"
            except IndexError:
                return 0, 0, "Sem solução"

        def solucao_3():
            xfoil.rodar_xfoil(
                    aerofolio,
                    str(alpha),
                    str(alpha),
                    "0",
                    str(re),
                    str(Ma),
                    "9",
                    "100",
                    "arquivo_dados_s3.txt",
                    mudar_paineis=True,
                    mostrar_grafico=False,
                    ler_arquivo_coord=self.ler,
                    compressibilidade=False,
                    solucao_viscosa=False,
                )

            dados = np.loadtxt("arquivo_dados_s3.txt", skiprows=12)
            os.remove("arquivo_dados_s3.txt")

            cl = dados[1]
            if (self.condicao_cl == True):
                if (cl > 2.5):
                    cl = 0

            cd = abs(dados[3])

            cl = cl / (np.sqrt(1 - Ma**2))
            cd = cd / (np.sqrt(1 - Ma**2))

            return cl, cd, "Solução invíscida"

        
        if (Ma < 1):
            if (len(self.solucoes) == 3):
                cl, cd, tipo_solucao = solucao_1()

                if (cl == 0 and cd == 0):
                    cl, cd, tipo_solucao = solucao_2()
                    
                    if (cl == 0 and cd == 0):
                        cl, cd, tipo_solucao = solucao_3()
            elif (len(self.solucoes) == 1):
                cl, cd, tipo_solucao = locals()[self.solucoes[0]]()
        elif (Ma > 0):
            cl = 0
            cd = 1
            tipo_solucao = "Ma > 1"
        else:
            cl = 0
            cd = 1
            tipo_solucao = "Error sem solução"

        if self.bool_val == True:
            self.df_val_aerof = self.df_val_aerof.append(
                pd.DataFrame(
                    {
                        "Velocidade": [self.v],
                        "RPM": [self.rpm],
                        "Alpha": [alpha],
                        "Re": [re],
                        "Cl": [cl],
                        "Cd": [cd],
                        "Tipo": [tipo_solucao],
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

        dT = []
        dQ = []
        r_new = []

        # Cálculo para cada seção
        for i in range(len(self.aerof) - 1):
            reynolds = self.rho * vr[i] * self.c[i] / self.mi
            Ma = vr[i] / (np.sqrt(1.4 * 287 * self.T))

            coef_l, coef_d = self.rodar_xfoil(
                self.aerof[i], round(reynolds, 0), alpha[i], Ma
            )

            if coef_l != 0:
                gamma = np.arctan(coef_d/coef_l)

                dt = q*coef_l*self.c[i]*(np.cos(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                dq = q*coef_l*self.c[i]*self.r[i]*(np.sin(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                
                dT.append(dt)
                dQ.append(dq)

                r_new.append(self.r[i])

        J = 60 * self.v / (self.rpm * self.D)

        dT.append(0)
        dQ.append(0)

        r_new.append(self.r[-1])

        T = self.integracao(np.array(dCT), r_new) * self.n
        Q = self.integracao(np.array(dCQ), r_new) * self.n

        P = 2 * np.pi * coef_Q

        eta = J * T / P
        
        if (self.bool_val == True) and (T >= 0) and (Q > 0):
            self.df_val_helice = self.df_val_helice.append(
                pd.DataFrame({"Velocidade": [self.v], "RPM": [self.rpm], "Eficiencia": [eta]}),
                ignore_index=True
            )
            
            return eta, self.df_val_aerof, self.df_val_helice
        elif (T <= 0) and (Q <= 0) and (self.bool_val == True):
            self.df_val_helice = self.df_val_helice.append(
                pd.DataFrame({"Velocidade": [self.v], "RPM": [self.rpm], "Eficiencia": [eta]}),
                ignore_index=True
            )
            
            return eta, self.df_val_aerof, self.df_val_helice
        else:
            return np.NaN