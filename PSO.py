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
    def __init__(self, qde_iteracoes, qde_de_particulas, condicao_de_voo, **kwargs):
        self.qde_particulas = qde_de_particulas
        self.N              = qde_iteracoes
        self.condicao_voo   = condicao_de_voo
        self.id             = kwargs.get("id")
        self.condicoes_geometricas = kwargs.get("condicoes_geometricas")
        self.logger         = logging.getLogger("logger_main")        
        self.r              = np.random.rand(2)
        self.t              = 0
        self.convergencia   = []
        self.t_list         = []

        self.resultados_aerodinamicos = None
        self.resultados_matriz_pso = None
        self.path_pasta_cenario = f"resultados/resultados_id_{self.id}"

        self.logger.info("//Início da Iteração 0//--------------------\n")
        self.iterar_zero()

    
    def iterar_zero(self):
        self.logger.info("- Início da computação da função objetivo")
        fo_controller = FuncaoObjetivo(
            condicoes_de_voo=self.condicao_voo,
            qde_particulas=self.qde_particulas,
            inicial=True,
            condicoes_geometricas=self.condicoes_geometricas
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
        self.fo = eficiencia_invertida_inicial.copy()
        self.resultados = resultados.copy()

        self.logger.info("- Início da gravação dos resultados")
        self.resultados_aerodinamicos = gravar_resultados_aerodinamicos(
            resultados=resultados,
            id=self.id,
            iteracao=0
        )

        _, self.resultados_matriz_pso = gravar_resultados_matriz_pso(
            resultados=matriz,
            id=self.id,
            iteracao=self.t,
            fo=eficiencia_invertida_inicial
        )

        self.t_list.append(self.t)

        self.c1 = 2.05
        self.c2 = 2.05
        self.w  = 0.72984
        self.t  = 1

    def iterar(self):
        salvar_resultados_json(
            eficiencia=self.fo,
            matriz_v=self.v,
            matriz_pso=self.matriz,
            p_best=self.p_best,
            g_best=self.g_best,
            r=self.r,
            id=self.id
        )
        
        self.atualizar_v_e_x(
            v=self.v,
            x=self.matriz,
            p_best=self.p_best,
            g_best=self.g_best
        )

        self.logger.info("- Fim da gravação dos resultados\n\n")
        self.logger.info(f"//Início da iteração {self.t}//--------------------\n")
        self.logger.info("- Início da computação da função objetivo")

        fo_controller = FuncaoObjetivo(
            qde_particulas=self.qde_particulas,
            condicoes_de_voo=self.condicao_voo,
            inicial=False,
            condicoes_geometricas=self.condicoes_geometricas
        )
        fo_controller.inserir_parametros(
            matriz=self.matriz,
            pontos_p=self.pontos_p,
            pontos_A=self.pontos_A
        )
        self.logger.info("- Fim da computação da função objetivo")

        self.fo = fo_controller.retornar_eficiencia()
        resultados = fo_controller.retornar_resultados()
        self.matriz = fo_controller.retornar_matriz()

        self.atualizar_p_best_e_g_best(
            fo=self.fo,
            p_best=self.p_best,
            g_best=self.g_best,
            p_best_obj=self.p_best_obj,
            g_best_obj=self.g_best_obj,
            x=self.matriz
        )

        self.resultados_aerodinamicos = gravar_resultados_aerodinamicos(
            resultados=resultados,
            id=self.id,
            iteracao=self.t
        )

        _, self.resultados_matriz_pso = gravar_resultados_matriz_pso(
            resultados=self.matriz,
            id=self.id,
            iteracao=self.t,
            fo=self.fo
        )

        self.t_list.append(self.t)
        
        self.t += 1
        self.w = 0.4*(self.t - self.N)/self.N**2 + 0.4
        self.c1 = -3*self.t/self.N + 3.5
        self.c2 = 3*self.t/self.N + 0.5


    def atualizar_g_best(
        self,
        fo: np.ndarray,
        x: np.ndarray
    ):
        selecao = ((fo <= 1) & (fo > 0))
        fo_maximo = fo[selecao].max()

        if fo_maximo > 1:
            raise Exception(
                "O valor de fo_maximo não pode ser maior do que 1"
                "Rever seleção"
            )

        for particula in range(self.qde_particulas):
            fo_particula = fo[particula]

            if fo_particula == fo_maximo:
                g_best = x[particula]
                g_best_obj = fo_particula

                self.convergencia.append(fo_particula)

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

            condicao_fo_nova = (
                (fo_particula < 1) & (fo_particula >= 0)
            )

            if (
                (fo_particula > p_best_obj_part) &
                (condicao_fo_nova)
            ):
                p_best[particula] = x[particula]
                p_best_obj[particula] = fo_particula

                if fo_particula > 1:
                    raise Exception(
                        "O valor de fo_maximo não pode ser maior do que 1"
                        "Rever seleção"
                    )
        
        selecao = ((p_best_obj > 0) & (p_best_obj <= 1))
        p_best_obj_max = p_best_obj[selecao].max()
        self.convergencia.append(p_best_obj_max)
        
        for particula in range(self.qde_particulas):
            p_best_obj_part = p_best_obj[particula]            
            if (
                p_best_obj_part == p_best_obj_max # TODO: rever
            ):
                g_best = x[particula]
                g_best_obj = p_best_obj_part

                if p_best_obj_part > 1:
                    raise Exception(
                        "O valor de fo_maximo não pode ser maior do que 1"
                        "Rever seleção"
                    )

        self.p_best = p_best.copy()
        self.g_best = g_best.copy()

        self.p_best_obj = p_best_obj.copy()
        self.g_best_obj = g_best_obj.copy()        


    def atualizar_v_e_x(
        self,
        v: np.ndarray,
        x: np.ndarray,
        p_best: np.ndarray,
        g_best: np.ndarray
    ):
        for particula in range(self.qde_particulas):
            p_best_part = p_best[particula]
            
            if (x[particula] == g_best).all():
                v[particula] = self.c1*self.r[0]*(p_best_part - x[particula]) + self.c2*self.r[1]*(g_best - x[particula])                
            else:
                v[particula] = self.w * v[particula] + self.c1*self.r[0]*(p_best_part - x[particula]) + self.c2*self.r[1]*(g_best - x[particula])
            
            x[particula] = x[particula] + v[particula]

        self.v = v.copy()
        self.matriz = x.copy()