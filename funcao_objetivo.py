import os
import numpy as np
from funcoes_de_bezier import Bezier
from funcao_helice import helice
from utilidades import (
    rodar_helice_inidividual,
    criar_txt_pontos_aerofolio_para_rodar_xfoil
)

class FuncaoObjetivo:
    def __init__(self, qde_particulas: int, condicoes_de_voo:dict, inicial:bool=False):
        self.qde_particulas                    = qde_particulas
        self.condicoes_de_voo                  = condicoes_de_voo
        self.matriz                            = None
        self.pontos_p                          = []
        self.curvas_aerofolios                 = []
        self.eficiencia_invertida_helice_total = []
        self.resultados                        = []

        if inicial:
            self.criar_matriz_inicial()
            self.rodar_helice_total()
            self.computar_eficiencia()
        else:
            self.rodar_bezier()
            self.rodar_helice_total()
            self.computar_eficiencia()

    def criar_parametros_iniciais(self):
        matriz = [round(np.random.uniform(19.5, 46.3), 2) for _ in range(7)]
        
        bezier_controller = Bezier()
        pontos_p = bezier_controller.gerar_aerofolio_aleatorio()
        linhas, a0, _, _ = bezier_controller.gerar_pontos_de_bezier(retornar=True)

        for ax in a0[0]:
            matriz.append(ax[0])

        for ay in a0[1]:
            matriz.append(ay[0])

        self.pontos_p.append(pontos_p)
        self.curvas_aerofolios.append(linhas)

    def criar_matriz_inicial(self):
        self.matriz = np.array([self.criar_parametros_iniciais() for _ in range(self.qde_particulas)])        
    
    def rodar_bezier(self):
        particulas             = self.matriz.copy()
        pontos_p               = self.pontos_p.copy()
        self.curvas_aerofolios = []

        ponto_p_escolhido = 0
        for particula in particulas:
            ponto_p = pontos_p[ponto_p_escolhido]
            ponto_p_escolhido = ponto_p_escolhido + 1
            
            ax = particula[8:12]
            ay = particula[12:]

            bezier_controller = Bezier()
            linhas, _, _, pontos_p = bezier_controller.atualizar_aerofolio(
                pontos_x=ax,
                pontos_y=ay,
                pontos_p=ponto_p
            )

            self.curvas_aerofolios.append(linhas)
    
    def rodar_helice_total(self):
        matriz            = self.matriz.copy()
        curvas_aerofolios = self.curvas_aerofolios.copy()
        condicoes_de_voo  = self.condicoes_de_voo

        raio = np.array([10, 12, 18, 24, 30, 36, 42, 48])*0.0254
        c = np.array([4.82, 5.48, 6.86, 7.29, 7.06, 6.35, 5.06, 0])*0.0254

        for particula in range(len(matriz)):
            beta = matriz[particula][:8]
            beta = np.append(beta, 0) * np.pi/180.

            nome_arq_aerofolio = criar_txt_pontos_aerofolio_para_rodar_xfoil(
                curvas_aerofolios[particula]
            )
            aerofolios = [nome_arq_aerofolio for _ in range(8)]

            resultados_individuais = rodar_helice_inidividual(
                condicoes_voo=condicoes_de_voo,
                aerofolios=aerofolios,
                raio=raio,
                c=c,
                beta=beta
            )
            
            self.resultados.append(resultados_individuais)
            os.remove(nome_arq_aerofolio)
    
    def computar_eficiencia(self):
        resultados = self.resultados.copy()

        for resultado in resultados:
            eficiencia_particula = resultado["eta"]
            eficiencia_invertida = 1 / eficiencia_particula

            self.eficiencia_invertida_helice_total.append(eficiencia_invertida)

    def tratar_eficiencia(self):
        eficiencias = np.array(
            self.eficiencia_invertida_helice_total.copy()
        )

        mean = np.random.randint(
            low=2,
            high=10,
            dtype=int
        )
        eficiencias[np.isnan(eficiencias)] = mean

        self.self.eficiencia_invertida_helice_total = eficiencias.copy()

    def retornar_eficiencia(self):
        return self.eficiencia_invertida_helice_total

    def retornar_resultados(self):
        return self.resultados

    def retornar_pontos_p(self):
        return self.pontos_p

    def retornar_matriz(self):
        return self.matriz