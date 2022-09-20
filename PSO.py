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
import logging

class OtimizacaoHelice:
    def __init__(self, qde_iteracoes, qde_de_particulas, condicao_de_voo, id):
        self.qde_particulas = qde_de_particulas
        self.N              = qde_iteracoes
        self.condicao_voo   = condicao_de_voo
        self.id             = id
        self.logger         = logging.getLogger("logger_main")
        
        self.r              = np.random.rand(2)
        self.t              = 0
        self.convergencia   = []
        self.t_list         = []

        self.logger.info("//Início da Iteração 0//--------------------\n")
        self.iterar_zero()

    
    def iterar_zero(self):
        self.logger.info("- Início da computação da função objetivo")
        fo_controller = FuncaoObjetivo(
            condicoes_de_voo=self.condicao_voo,
            qde_particulas=self.qde_particulas,
            inicial=True
        )
        self.logger.info("- Fim da computação da função objetivo")

        eficiencia_invertida_inicial = fo_controller.retornar_eficiencia()
        matriz = fo_controller.retornar_matriz()
        pontos_p = fo_controller.retornar_pontos_p()
        pontos_a = fo_controller.retornar_pontos_A()
        resultados = fo_controller.retornar_resultados()
        
        p_best = matriz.copy()
        self.p_best_obj = eficiencia_invertida_inicial.copy()

        self.atualizar_g_best(
            fo=eficiencia_invertida_inicial,
            x=matriz
        )

        self.matriz = matriz
        self.v = np.zeros((self.qde_particulas, matriz.shape[1]), dtype=float)
        self.p_best = p_best.copy()
        self.pontos_p = pontos_p
        self.pontos_A = pontos_a
        self.eficiencia_antiga = eficiencia_invertida_inicial.copy()
        self.resultados = resultados.copy()

        self.logger.info("- Início da gravação dos resultados")
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

        self.convergencia.append(self.g_best_obj)
        self.t_list.append(self.t)

        self.c1 = 2.05
        self.c2 = 2.05
        self.w  = 0.72984
        self.t  = 1

    def iterar(self):
        eficiencia_antiga = self.eficiencia_antiga
        eficiencia_nova   = None

        self.v      = self.w * self.v + self.c1*self.r[0]*(self.p_best - self.matriz) + self.c2*self.r[1]*(self.g_best - self.matriz)
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

        self.logger.info("- Fim da gravação dos resultados\n\n")
        self.logger.info(f"//Início da iteração {self.t}//--------------------\n")
        self.logger.info("- Início da computação da função objetivo")

        fo_controller = FuncaoObjetivo(
            qde_particulas=self.qde_particulas,
            condicoes_de_voo=self.condicao_voo,
            inicial=False
        )
        fo_controller.inserir_parametros(
            matriz=self.matriz,
            pontos_p=self.pontos_p,
            pontos_A=self.pontos_A
        )
        self.logger.info("- Fim da computação da função objetivo")

        eficiencia_nova = fo_controller.retornar_eficiencia()
        resultados = fo_controller.retornar_resultados()
        self.matriz = fo_controller.retornar_matriz()

        objetivo_inicial = eficiencia_antiga.copy()
        objetivo_novo    = eficiencia_nova.copy()

        self.atualizar_p_best_e_g_best(
            fo=objetivo_novo,
            p_best=self.p_best,
            g_best=self.g_best,
            p_best_obj=self.p_best_obj,
            g_best_obj=self.g_best_obj,
            x=self.matriz
        )

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

        self.convergencia.append(self.g_best_obj)
        self.t_list.append(self.t)
        
        self.t += 1
        # self.w = 0.4*(self.t - self.N)/self.N**2 + 0.4
        # self.c1 = -3*self.t/self.N + 3.5
        # self.c2 = 3*self.t/self.N + 0.5


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


    def atualizar_g_best(
        self,
        fo: np.ndarray,
        x: np.ndarray
    ):
        selecao = ((fo <= 1) & (fo > 0))
        fo_maximo = fo[selecao].max()

        for particula in range(self.qde_particulas):
            fo_particula = fo[particula]

            if fo_particula == fo_maximo:
                g_best = x[particula]
                g_best_obj = fo_particula

        self.g_best = g_best.copy()
        self.g_best_obj = g_best_obj.copy()


    def atualizar_p_best_e_g_best(
        self,
        fo: np.ndarray,
        p_best: np.ndarray,
        g_best: np.ndarray,
        p_best_obj: np.ndarray,
        g_best_obj: np.ndarray,
        x: np.ndarray
    ):
        for particula in range(self.qde_particulas):
            p_best_obj_part = p_best_obj[particula]
            fo_particula = fo[particula]
            
            condicao_alpha = (
                (x[particula][0:7] >= -20).all() & (x[particula][0:7] <= 20).all()
            )

            condicao_fo_nova = (
                (fo_particula < 1) & (fo_particula > 0)
            )

            if (
                (fo_particula > p_best_obj_part) &
                (condicao_alpha) &
                (condicao_fo_nova)
            ):
                p_best[particula] = x[particula]
                p_best_obj[particula] = fo_particula
        
        p_best_obj_max = p_best_obj.max()
        
        for particula in range(self.qde_particulas):
            p_best_obj_part = p_best_obj[particula]            
            if (
                p_best_obj_part == p_best_obj_max # TODO: rever
            ):
                g_best = x[particula]
                g_best_obj = p_best_obj_part

        self.p_best = p_best.copy()
        self.g_best = g_best.copy()

        self.p_best_obj = p_best_obj.copy()
        self.g_best_obj = g_best_obj.copy()        