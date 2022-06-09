import numpy as np
from funcoes_de_bezier import Bezier
from funcao_helice import helice

class FuncaoObjetivo:
    def __init__(self, x, aerof_inicial, otimizar):
        self.x = x
        self.aerof_inicial = aerof_inicial
        self.otimizar = otimizar
        
        if not 'bezier' in otimizar:
            rodar_helice(aerofolios=aerof_inicial, beta=True)
    
    def rodar_bezier(self, aerof_base):
        bezier = Bezier()
        self.linhas,_,_ = bezier.gerar_bezier(tamanho_entre_pontos=10, retornar=True)

        bezier.mudar_A(ponto=2, mudanca_x=0, mudanca_y=0, mudanca_adicional=True)

        self.linhas,_,_,_ = bezier.bezier_mudar_A(tamanho=10)

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

        for pos in self.x:
            beta = np.append(pos, 0)*np.pi/180.

            result_indv, _, _ = helice(
                Aerofolios=aerofolios,
                Velocidade_da_aeronave=50,
                Viscosidade_dinamica=1.789e-5,
                Temperatura=288.2,
                Densidade_do_ar=1.225,
                Diametro_helice=96*0.0254,
                Numero_de_pas=2,
                Array_raio_da_secao=raio,
                Array_tamanho_de_corda_da_secao=c,
                Array_angulo_beta_da_secao=beta,
                Rotacao_motor=3600.,
                Solucoes_ligadas=['solucao_3'],
                ligar_solucao_aerof_naca=True
            ).rodar_helice()
            result_gerais.append(1/result_indv)
        
        return np.array(result_gerais)
        

