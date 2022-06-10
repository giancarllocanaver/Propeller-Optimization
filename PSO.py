import numpy as np
from funcao_objetivo import FuncaoObjetivo
from matplotlib import pyplot as plt
import os
import pandas as pd

class OtimizacaoHelice:
    def __init__(self, qde_iteracoes, qde_de_particulas, aerofolio_inicial=['NACA 4412'], otimizar=['bezier', 'beta']):
        self.qde_particulas = qde_de_particulas
        self.v = np.array([])
        self.objetivo = np.array([])
        self.p_best = np.array([])
        self.g_best = np.array([])
        self.c1 = 0
        self.c2 = 0
        self.w = 0
        self.r = 0
        self.N = qde_iteracoes
        self.t = 0
        self.convergencia = []
        self.t_list = []
        self.aerof_inicial = aerofolio_inicial
        self.var = otimizar

    def criar_aleatorios(self, limite_inferior, limite_superior, quantidade):
        aleatorios = [round(np.random.uniform(limite_inferior, limite_superior), 2) for _ in range(quantidade)]

        return aleatorios
    
    def rodar_fo(self, matriz_valores, aerof_inicial, otimizar):
        resultados = FuncaoObjetivo(
            matriz=matriz_valores,
            aerof_inicial=aerof_inicial,
            otimizar=otimizar
        )
        
        return resultados.retornar_resultados()

    def start(self):
        # Matriz PSO:
        self.matriz = np.array([self.criar_aleatorios(limite_inferior=19.5, limite_superior=46.3, quantidade=7) for _ in range(self.qde_particulas)])
        # self.matriz = np.random.randint(low=4, high=8, size=(self.qde_part, 7))
        self.v = np.zeros((self.qde_particulas, 7), dtype=float)

        self.objetivo = self.rodar_fo(
            matriz_valores=self.matriz,
            aerof_inicial=self.aerof_inicial,
            otimizar=self.var
        )

        self.p_best = self.matriz
        self.g_best = self.p_best[self.objetivo.argmin(), :]

        self.c1 = 2.05
        self.c2 = 2.05
        self.w = 0.72984  
        self.r = np.random.rand(2)

    def next(self):
        self.v = self.w * self.v + self.c1*self.r[0]*(self.p_best - self.matriz) + self.c2*self.r[1]*(self.g_best - self.matriz)
        self.matriz = self.matriz + self.v

        objetivo_2 = self.rodar_fo(
            matriz_valores=self.matriz,
            aerof_inicial=self.aerof_inicial,
            otimizar=['beta']
        )

        self.p_best[(objetivo_2 <= self.objetivo), :] = self.matriz[(objetivo_2 <= self.objetivo), :]

        argumento_min = np.array([self.objetivo, objetivo_2]).min(axis=0).argmin()
        self.g_best = self.p_best[argumento_min, :]

        self.objetivo = objetivo_2

        self.t += 1

        self.convergencia.append(self.objetivo.min())
        self.t_list.append(self.t)

    def gerar_grafico(self):
        df = pd.DataFrame({'t': [], 'Objetivo min': []})

        for i in range(len(self.convergencia)):
            df = df.append({'t': [self.t_list[i]], 'Objetivo min': [self.convergencia[i]]}, ignore_index=True)
        
        with pd.ExcelWriter('Resultados-convergencia-otimizacao.xlsx') as writer:
            df.to_excel(writer, sheet_name='Convergencia')
            writer.save()

        plt.plot(self.t_list, self.convergencia, 'x')
        plt.xlabel('iteração')
        plt.ylabel('objetivo')
        plt.savefig('Grafico-convergencia-otimizacao.jpg', dpi=300)
        plt.show()