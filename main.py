import pandas as pd
import numpy as np
from PSO import OtimizacaoHelice
from tqdm import tqdm
from datetime import datetime
import time
import logging
from utilidades import (
    gerar_time_stamp,
    criar_logger,
    criar_pastas
)

if __name__ == '__main__':
    qde_iteracoes = 100
    qde_particulas = 20

    condicao_de_voo = {
        "Velocidade": 3,
        "Viscosidade": 1.789e-5,
        "Temperatura": 288.2,
        "Densidade do Ar": 1.225,
        "Diametro da Helice": 96*0.0254,
        "Numero de pas": 2,
        "Rotacao do Motor": 1000.
    }

    id = gerar_time_stamp()
    criar_pastas(id)
    criar_logger(id)
    
    logger = logging.getLogger("logger_main")

    logger.info("\n----------Processamento Iniciado----------\n")
    otimization_controller = OtimizacaoHelice(
        qde_iteracoes=qde_iteracoes,
        qde_de_particulas=qde_particulas,
        condicao_de_voo=condicao_de_voo,
        id=id
    )

    for _ in tqdm(range(qde_iteracoes)):
        time.sleep(5)
        otimization_controller.iterar()

    otimization_controller.gerar_grafico()