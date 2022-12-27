import os
from shutil import ExecError
import numpy as np
from funcoes_de_bezier import Bezier
from utilidades import (
    escolher_escalar,
    rodar_helice_inidividual,
    criar_txt_pontos_aerofolio_para_rodar_xfoil,
    mover_arquivos_coordenadas
)
import logging

class FuncaoObjetivo:
    def __init__(self, qde_particulas: int, condicoes_de_voo:dict, inicial:bool=False, **kwargs):
        self.qde_particulas                    = qde_particulas
        self.condicoes_de_voo                  = condicoes_de_voo
        self.logger                            = logging.getLogger("logger_main")
        self.condicoes_geometricas             = kwargs.get("condicoes_geometricas")
        self.matriz                            = None
        self.particula_escolhida               = None
        self.pontos_p                          = None
        self.pontos_A                          = None
        self.particulas_com_interseccao        = []
        self.curvas_aerofolios_inicial         = []
        self.curvas_aerofolios_atual           = []
        self.eficiencia_invertida_helice_total = []
        self.resultados                        = []
        self.pontos_A                          = []

        if inicial:
            self.criar_pontos_de_bezier_inicial()
            self.criar_matriz_inicial()
            self.rodar_helice_total()
            self.computar_eficiencia()
            

    def criar_pontos_de_bezier_inicial(self):
        bezier_controller = Bezier()
        pontos_p = bezier_controller.gerar_aerofolio("aerofolioClarkY", naca=True)
        linhas, a0, _, _ = bezier_controller.gerar_pontos_de_bezier(retornar=True)

        self.pontos_p = pontos_p.copy()
        self.pontos_A = a0.copy()
            

    def criar_parametros_iniciais(self):
        pontos_p = self.pontos_p.copy()
        pontos_A_validacao = self.pontos_A.copy()
        self.logger.info(f"Particula {self.particula_escolhida}: Pontos A de Bezier com a seguinte configuração")
        self.logger.info(f"\n\n{self.pontos_A}\n\n")

        self.logger.info(f"Particula {self.particula_escolhida}: Pontos P de Bezier com a seguinte configuração")
        self.logger.info(f"\n\n{pontos_p}\n\n")

        matriz = []
        pontos_aerofolio = []
        for secao in range(7):
            a = self.pontos_A.copy()

            if (self.pontos_A != pontos_A_validacao).any():
                raise Exception(
                    "Os pontos A mudaram!!!"
                )

            verificacao = False
            while verificacao == False:
                escalar = escolher_escalar(secao=secao)
                a[1][3][0] = self.pontos_A[1][3][0] + escalar

                bezier_controller = Bezier()
                linhas, _, _, _ = bezier_controller.atualizar_aerofolio(
                    pontos_x=a[0],
                    pontos_y=a[1],
                    pontos_p=pontos_p
                )

                if type(linhas) != int:
                    verificacao = True

            matriz.append(escalar)
            pontos_aerofolio.append(linhas)

        self.curvas_aerofolios_inicial.append(pontos_aerofolio)

        return matriz


    def criar_matriz_inicial(self):
        self.logger.info("Início da criação da matriz inicial")

        particulas = [self.criar_parametros_iniciais() for self.particula_escolhida in range(self.qde_particulas)]
        self.matriz = np.array(particulas)
        self.curvas_aerofolios_atual = self.curvas_aerofolios_inicial.copy()

        self.logger.info("Matriz formada com a seguinte configuração:")
        self.logger.info(f"\n\n{self.matriz}\n\n")
        self.logger.info("Fim da criação da matriz inicial")


    def inserir_parametros(
        self,
        matriz: np.ndarray,
        pontos_p: np.ndarray,
        pontos_A: np.ndarray
    ):
        self.matriz = matriz
        self.pontos_p = pontos_p
        self.pontos_A = pontos_A

        self.rodar_bezier()
        self.rodar_helice_total()
        self.computar_eficiencia()


    def rodar_bezier(self):
        self.logger.info("Início das rodagens por Bezier")

        particulas                   = self.matriz.copy()
        pontos_p                     = self.pontos_p.copy()
        pontos_A                     = self.pontos_A.copy()
        self.curvas_aerofolios_atual = []
        
        self.logger.info("Matriz com a seguinte configuração:")
        self.logger.info(f"\n\n{particulas}\n\n")
        self.logger.info("Pontos P com a seguinte configuração:")
        self.logger.info(f"\n\n{pontos_p}\n\n")
        self.logger.info("Pontos A com a seguinte configuração:")
        self.logger.info(f"\n\n{pontos_A}\n\n")

        ax = pontos_A[0].copy()
        ay = pontos_A[1].copy()

        for particula in range(len(particulas)):
            self.logger.info(f"Início bezier para partícula {particula}:")          
            
            escalares = particulas[particula]
            pontos_aerofolio = []

            for escalar in escalares:
                ay_conta = ay.copy()
                ay_conta[3][0] = escalar + ay[3][0]

                self.logger.info(f"Escalar:")
                self.logger.info(f"\n\n{escalar}\n\n")
                self.logger.info(f"Ponto AX:")
                self.logger.info(f"\n\n{ax}\n\n")
                self.logger.info(f"Ponto AY:")
                self.logger.info(f"\n\n{ay}\n\n")
                self.logger.info(f"Pontos P da partícula:")
                self.logger.info(f"\n\n{pontos_p}\n\n")

                bezier_controller = Bezier()
                linhas, _, _, _ = bezier_controller.atualizar_aerofolio(
                    pontos_x=ax,
                    pontos_y=ay_conta,
                    pontos_p=pontos_p
                )

                if type(linhas) == int:
                    verificacao = False
                    while verificacao == False:
                        escalar = np.random.uniform(low=-0.05, high=0.05)
                        ay_conta[3][0] = ay[3][0] + escalar

                        bezier_controller = Bezier()
                        linhas, _, _, _ = bezier_controller.atualizar_aerofolio(
                            pontos_x=ax,
                            pontos_y=ay_conta,
                            pontos_p=pontos_p
                        )

                        if type(linhas) != int:
                            verificacao = True
                            self.matriz[particula][-1] = escalar

                if not (self.pontos_A == pontos_A).all():
                    raise Exception(
                        "Pontos A mudaram!!!"
                    )

                pontos_aerofolio.append(linhas)

            self.curvas_aerofolios_atual.append(pontos_aerofolio)

        self.logger.info("Fim das rodagens por Bezier")


    def rodar_helice_total(self):
        self.logger.info("Início das rodagens das Hélices")

        matriz            = self.matriz.copy()
        curvas_aerofolios = self.curvas_aerofolios_atual.copy()
        condicoes_de_voo  = self.condicoes_de_voo

        raio = self.condicoes_geometricas["raio"]
        c = self.condicoes_geometricas["corda"]

        particula_com_interseccao = False
        for particula in range(len(matriz)):
            aerofolios = []
            for secao in range(7):
                nome_arq_aerofolio = criar_txt_pontos_aerofolio_para_rodar_xfoil(
                    curvas_aerofolios[particula][secao]
                )
                aerofolios.append(nome_arq_aerofolio)

            resultados_individuais = rodar_helice_inidividual(
                condicoes_voo=condicoes_de_voo,
                aerofolios=aerofolios,
                raio=raio,
                c=c,
                particula_com_interseccao=particula_com_interseccao
            )
            
            self.resultados.append(resultados_individuais)

        self.logger.info("Fim das rodagens por Bezier")


    def computar_eficiencia(self):
        resultados = self.resultados.copy()

        for resultado in resultados:
            eficiencia_particula = resultado["eficiencia"][0]
            self.eficiencia_invertida_helice_total.append(eficiencia_particula)
        
        self.eficiencia_invertida_helice_total = np.array(self.eficiencia_invertida_helice_total)


    def tratar_eficiencia(self):
        eficiencias = np.array(
            self.eficiencia_invertida_helice_total.copy()
        )

        mean = np.random.randint(
            low=5,
            high=10,
            dtype=int
        )
        eficiencias[np.isnan(eficiencias)] = mean

        self.eficiencia_invertida_helice_total = eficiencias.copy()


    def retornar_eficiencia(self):
        return self.eficiencia_invertida_helice_total

    def retornar_resultados(self):
        return self.resultados

    def retornar_pontos_p(self):
        return self.pontos_p

    def retornar_matriz(self):
        return self.matriz

    def retornar_pontos_A(self):
        return self.pontos_A