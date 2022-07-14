import numpy as np
from funcoes_de_bezier_2 import Bezier
from xfoil_funcao_2 import rodar_xfoil as xfoil
import pandas as pd
import os
from random import randint

class gerar_dados():
    def __init__(self, gerar_dados_csv=True):
        self.pto_bez = None
        self.pto_bez_append = []
        self.ler_arquivo_de_dados = gerar_dados_csv
        self.cl_append = []
        self.cd_append = []
        self.alpha_append = []
        self.reynolds_append = []
        self.a_x_append = []
        self.a_y_append = []



    def mudar_ptos_bezier(self):
        self.a_x = round(np.random.uniform(-0.2, 0.2), 4)
        self.a_y = round(np.random.uniform(-0.09, 0.09), 4)

        bezier = Bezier()
        linhas, a, _ = bezier.gerar_bezier(tamanho_entre_pontos=10, retornar=True)

        self.pto_bez = randint(1,4)

        bezier.mudar_A(ponto=self.pto_bez, mudanca_x=self.a_x, mudanca_y=self.a_y, mudanca_adicional=True, retornar=False)

        self.linhas, a_out, _, _ = bezier.bezier_mudar_A(tamanho=10)


    
    def inputs_xfoil(self):
        self.alpha = round(np.random.uniform(-20, 20), 2)
        self.reynolds = round(np.random.uniform(150000, 5000000), 2)



    def rodar_xfoil_e_obter_dados(self):
        if self.linhas.shape[1] > 5:
            xfoil(curvas_aerofolio=self.linhas, alpha_inicial=str(self.alpha), alpha_final=str(self.alpha), alpha_step="0",
                Reynolds=str(self.reynolds), Mach="0", N_crit=str(9), iteracoes=str(100), nome_do_arquivo_de_output="Dados_output.txt",
                mudar_paineis=True, ler_arquivo_coord=False, compressibilidade=False, solucao_viscosa=True)

            dados = np.loadtxt("Dados_output.txt", skiprows=12)

            os.remove("Dados_output.txt")

            if dados.size != 0:
                self.cl = dados[1]
                self.cd = dados[2]

                self.cl_append.append(self.cl)
                self.cd_append.append(self.cd)

                self.a_x_append.append(self.a_x)
                self.a_y_append.append(self.a_y)

                self.alpha_append.append(self.alpha)
                self.reynolds_append.append(self.reynolds)

                self.pto_bez_append.append(self.pto_bez)

                self.situacao = True
            else:
                self.situacao = False
    


    def gerar_dados_csv(self):
        if self.ler_arquivo_de_dados == True:
            selecao = {'Ponto de Bezier': self.pto_bez_append,'A - Coordenada X': self.a_x_append, 'A - Coordenada Y': self.a_y_append, 'AoA': self.alpha_append, 'Reynolds': self.reynolds_append, 'CL': self.cl_append, 'CD': self.cd_append}

            dados = pd.DataFrame(selecao)

            dados.to_csv("Dados-gerados-xfoil.csv")
        else:
            dados = pd.read_csv("Dados-gerados-xfoil.csv")

            for i in range(len(self.cl_append)):
                dados.append({'Ponto de Bezier': self.pto_bez_append,'A - Coordenada X': self.a_x_append[i], 'A - Coordenada Y': self.a_y_append[i], 'AoA': self.alpha_append[i], 'Reynolds': self.reynolds_append[i], 'CL': self.cl_append[i], 'CD': self.cd_append[i]})

            dados.to_csv("Dados-gerados-xfoil.csv")

teste = gerar_dados()

for _ in range(100000):
    teste.mudar_ptos_bezier()
    teste.inputs_xfoil()
    teste.rodar_xfoil_e_obter_dados()

teste.gerar_dados_csv()