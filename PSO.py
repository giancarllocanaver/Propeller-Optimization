import numpy as np
from funcao_objetivo import FuncaoObjetivo
from matplotlib import pyplot as plt
import os
import pandas as pd
from funcoes_de_bezier import Bezier

class OtimizacaoHelice:
    def __init__(self, qde_iteracoes, qde_de_particulas, condicao_de_voo):
        self.qde_particulas = qde_de_particulas
        self.N              = qde_iteracoes
        self.condicao_voo   = condicao_de_voo
        self.c1 = 2.05
        self.c2 = 2.05
        self.w = 0.72984
        self.r = np.random.rand(2)

        self.iterar_zero()

    
    def iterar_zero(self):
        fo_controller = FuncaoObjetivo(
            condicoes_de_voo=self.condicao_voo,
            inicial=True
        )
        eficiencia_invertida_inicial = fo_controller.retornar_eficiencia()
        matriz = fo_controller.retornar_matriz()
        
        p_best = matriz
        g_best = p_best[eficiencia_invertida_inicial.argmin(), :]


        self.v = np.zeros((self.qde_particulas, matriz.shape[1]), dtype=float)
        self.p_best = p_best.copy()
        self.g_best = g_best.copy()

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