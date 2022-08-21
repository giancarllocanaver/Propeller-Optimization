import numpy as np
from funcao_objetivo import FuncaoObjetivo
from matplotlib import pyplot as plt
import os
import pandas as pd
from utilidades import (
    gravar_resultados_aerodinamicos,
    gravar_resultados_matriz_pso,
    salvar_resultados_json
)

class OtimizacaoHelice:
    def __init__(self, qde_iteracoes, qde_de_particulas, condicao_de_voo, id):
        self.qde_particulas = qde_de_particulas
        self.N              = qde_iteracoes
        self.condicao_voo   = condicao_de_voo
        self.id             = id
        self.r              = np.random.rand(2)
        self.t              = 0
        self.convergencia   = []
        self.t_list         = []

        self.iterar_zero()

    
    def iterar_zero(self):
        fo_controller = FuncaoObjetivo(
            condicoes_de_voo=self.condicao_voo,
            qde_particulas=self.qde_particulas,
            inicial=True
        )
        eficiencia_invertida_inicial = fo_controller.retornar_eficiencia()
        matriz = fo_controller.retornar_matriz()
        pontos_p = fo_controller.retornar_pontos_p()
        resultados = fo_controller.retornar_resultados()
        
        p_best = matriz.copy()

        selecao = eficiencia_invertida_inicial >= 0
        argumento_g_best = eficiencia_invertida_inicial[selecao].argmin()
        g_best = p_best[argumento_g_best, :]

        self.matriz = matriz
        self.v = np.zeros((self.qde_particulas, matriz.shape[1]), dtype=float)
        self.p_best = p_best.copy()
        self.g_best = g_best.copy()
        self.pontos_p = pontos_p
        self.eficiencia_antiga = eficiencia_invertida_inicial.copy()
        self.resultados = resultados.copy()

        gravar_resultados_aerodinamicos(
            resultados=resultados,
            id=self.id,
            iteracao=0
        )

        gravar_resultados_matriz_pso(
            resultados=matriz,
            id=self.id,
            iteracao=self.t
        )

    def iterar(self):
        eficiencia_antiga = self.eficiencia_antiga
        eficiencia_nova   = None
        c1                = 2.05
        c2                = 2.05
        w                 = 0.72984

        self.v      = w * self.v + c1*self.r[0]*(self.p_best - self.matriz) + c2*self.r[1]*(self.g_best - self.matriz)
        self.matriz = self.matriz + self.v

        salvar_resultados_json(
            eficiencia=eficiencia_antiga,
            matriz_v=self.v,
            matriz_pso=self.matriz,
            p_best=self.p_best,
            g_best=self.g_best,
            r=self.r,
            id=self.id
        )        
        
        fo_controller = FuncaoObjetivo(
            qde_particulas=self.qde_particulas,
            condicoes_de_voo=self.condicao_voo,
            inicial=False
        )
        fo_controller.inserir_parametros(
            matriz=self.matriz,
            pontos_p=self.pontos_p
        )

        eficiencia_nova = fo_controller.retornar_eficiencia()
        self.pontos_p = fo_controller.retornar_pontos_p().copy()
        resultados = fo_controller.retornar_resultados()
        self.matriz = fo_controller.retornar_matriz()

        objetivo_inicial = eficiencia_antiga.copy()
        objetivo_novo    = eficiencia_nova.copy()

        argumento_p_best = (objetivo_novo <= objetivo_inicial) & (objetivo_novo >= 0)
        argumento_g_best = self.descobrir_argumento_minimo(
            obj_inicial=objetivo_inicial,
            obj_novo=objetivo_novo
        )

        self.p_best[argumento_p_best, :] = self.matriz[argumento_p_best, :]
        self.g_best = self.p_best[argumento_g_best, :]

        self.eficiencia_antiga = eficiencia_nova.copy()

        gravar_resultados_aerodinamicos(
            resultados=resultados,
            id=self.id,
            iteracao=self.t
        )

        gravar_resultados_matriz_pso(
            resultados=self.matriz,
            id=self.id,
            iteracao=self.t
        )

        self.t += 1

        self.convergencia.append(objetivo_novo.min())
        self.t_list.append(self.t)

    def descobrir_argumento_minimo(self, obj_inicial, obj_novo):
        novo_obj_1 = []
        novo_obj_2 = []
        obj_join = []

        for particula in range(len(obj_inicial)):
            obj_part = [obj_inicial[particula], particula]
            novo_obj_1.append(obj_part)

        for particula in range(len(obj_novo)):
            obj_part = [obj_novo[particula], particula]
            novo_obj_2.append(obj_part)

        for obj in novo_obj_1:
            obj_join.append(obj)

        for obj in novo_obj_2:
            obj_join.append(obj)

        array = np.array(obj_join)
        selecao = array[:,0].argmin(axis=0)
        array_selecao = array[selecao]

        argumento = int(array_selecao[1])

        return argumento

    def gerar_grafico(self):
        df = pd.DataFrame({'t': [], 'Objetivo min': []})

        for i in range(len(self.convergencia)):
            df = df.append({'t': [self.t_list[i]], 'Objetivo min': [self.convergencia[i]]}, ignore_index=True)
        
        with pd.ExcelWriter(f'resultados/resultados_id_{self.id}/Resultados-convergencia-otimizacao.xlsx') as writer:
            df.to_excel(writer, sheet_name='Convergencia')
            writer.save()

        plt.plot(self.t_list, self.convergencia, 'x')
        plt.xlabel('iteração')
        plt.ylabel('objetivo')
        plt.savefig(f'resultados/resultados_id_{self.id}/Grafico-convergencia-otimizacao.jpg', dpi=300)
        plt.show()