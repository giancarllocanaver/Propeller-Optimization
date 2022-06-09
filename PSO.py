import numpy as np
from funcao_objetivo import FuncaoObjetivo
from matplotlib import pyplot as plt
import os
import pandas as pd

class avanco:
    def __init__(self, qde_iteracoes, qde_de_particulas, aerofolio_inicial=['NACA 4412'], otimizar=['bezier', 'beta']):
        self.qde_particulas = qde_de_particulas
        self.x = np.array([])
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
    
    def f(x):
        resultados = funcao_objetivo(x=x, otimizar=self.otimizar)
        
        return resultados

    def start(self):
        # Variáveis de mudança:
        vetor_beta = [round(np.random.uniform(19.5, 46.3), 2) for _ in range(7)]

        # Matriz PSO:
        self.x = np.array([vetor_beta for _ in range(self.qde_particulas)])
        # self.x = np.random.randint(low=4, high=8, size=(self.qde_part, 7))
        self.v = np.zeros((self.qde_particulas, 7), dtype=float)

        self.objetivo = self.f(x=self.x, aerof_inicial=self.aerof_inicial, otimizar=self.var)


        self.p_best = self.x
        self.g_best = self.p_best[self.objetivo.argmin(), :]


        self.c1 = 2.05
        self.c2 = 2.05
        self.w = 0.72984
        
        self.r = np.random.rand(2)

    def next(self):
        self.v = self.w * self.v + self.c1*self.r[0]*(self.p_best - self.x) + self.c2*self.r[1]*(self.g_best - self.x)
        self.x = self.x + self.v

        objetivo_2 = self.f(self.x)


        self.p_best[(objetivo_2 <= self.objetivo), :] = self.x[(objetivo_2 <= self.objetivo), :]

        argumento_min = np.array([self.objetivo, objetivo_2]).min(axis=0).argmin()
        self.g_best = self.p_best[argumento_min, :]

        self.objetivo = objetivo_2

        self.t += 1

        self.convergencia.append(self.objetivo.min())
        self.t_list.append(self.t)

    def to_conv(self):
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


qde_iteracoes = 100
qde_particulas = 20

teste = avanco(qde_iteracoes=qde_iteracoes, qde_de_particulas=qde_particulas, otimizar=['beta'])
teste.start()

for _ in range(qde_iteracoes):
    teste.next()

teste.to_conv()