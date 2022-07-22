import numpy as np
from funcoes_de_bezier import Bezier
from funcao_helice import helice

class FuncaoObjetivo:
    def __init__(self, matriz, otimizar, pontos_p=None, inicial=False):
        self.matriz = matriz
        self.otimizar = otimizar
        self.inicial = inicial
        
        if not 'bezier' in otimizar:
            resultados = self.rodar_helice(aerofolios="NACA 4412", beta=True)
            mean = np.nanmean(resultados)
            resultados[np.isnan(resultados)] = mean

            self.resultados = resultados
        else:
            self.rodar_bezier(pontos_p=pontos_p)
        
    
    def rodar_bezier(self, pontos_p):
        particulas = self.matriz
        self.contorno_aerofolio = []
        self.novos_p = []

        for particula in particulas:
            ax = particula[8:12]
            ay = particula[12:15]           
            a = np.array([ax, ay])

            bezier_controller = Bezier()

            if self.inicial:
                linhas, _, _, _ = bezier_controller.mudar_pontos_de_bezier(
                    pontos_p=pontos_p,
                    a=a
                )

                self.contorno_aerofolio.append(linhas)
            else:
                linhas, a, _, pontos_p = bezier_controller.atualizar_aerofolio(
                    pontos_x=a[0],
                    pontos_y=a[1],
                    pontos_p=pontos_p
                )

                self.contorno_aerofolio.append(linhas)
                self.novos_p.append(pontos_p)       

    def rodar_helice(self, aerofolios=None, beta=None):
        raio = np.array([10,12,18,24,30,36,42,48])*0.0254

        if not aerofolios: 
            aerofolios = [self.linhas for _ in range(8)]
        else:
            aerofolios = [aerofolios[0] for _ in range(8)]
        
        c = np.array([4.82, 5.48,6.86,7.29, 7.06,6.35, 5.06, 0] )*0.0254

        if not beta:
            beta = np.array([46.3, 43.25, 38.1, 31.65, 26.3, 22.4, 19.5, 0]) * np.pi / 180.0

        result_gerais = []

        for pos in self.matriz:
            beta = np.append(pos, 0)*np.pi/180.

            result_indv = helice(
                Aerofolios=aerofolios,
                Velocidade_da_aeronave=3,
                Viscosidade_dinamica=1.789e-5,
                Temperatura=288.2,
                Densidade_do_ar=1.225,
                Diametro_helice=96*0.0254,
                Numero_de_pas=2,
                Array_raio_da_secao=raio,
                Array_tamanho_de_corda_da_secao=c,
                Array_angulo_beta_da_secao=beta,
                Rotacao_motor=1000.,
                Solucoes_ligadas=['solucao_1'],
                ligar_solucao_aerof_naca=True,
                ligar_interpolacao_2a_ordem=True
            ).rodar_helice()
            result_gerais.append(1/result_indv)
        
        return np.array(result_gerais)
    
    def retornar_resultados(self):
        return self.resultados
        

