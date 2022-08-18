import pandas as pd
import numpy as np
from PSO import OtimizacaoHelice

if __name__ == '__main__':
    qde_iteracoes = 20
    qde_particulas = 40

    condicao_de_voo = {
        "Velocidade": 3,
        "Viscosidade": 1.789e-5,
        "Temperatura": 288.2,
        "Densidade do Ar": 1.225,
        "Diametro da Helice": 96*0.0254,
        "Numero de pas": 2,
        "Rotacao do Motor": 1000.
    }

    id = np.random.randint(
        low=0,
        high=1000
    )

    otimization_controller = OtimizacaoHelice(
        qde_iteracoes=qde_iteracoes,
        qde_de_particulas=qde_particulas,
        condicao_de_voo=condicao_de_voo,
        id=id
    )

    for _ in range(qde_iteracoes):
        otimization_controller.iterar()

    otimization_controller.gerar_grafico()