import pandas as pd
import numpy as np
from PSO import OtimizacaoHelice

if __name__ == '__main__':
    qde_iteracoes = 5
    qde_particulas = 10

    teste = OtimizacaoHelice(
        qde_iteracoes=qde_iteracoes,
        qde_de_particulas=qde_particulas,
        otimizar=['beta']
    )
    teste.start()

    for _ in range(qde_iteracoes):
        teste.next()

    teste.gerar_grafico()