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
    criar_pastas,
    limpar_pasta_coordenadas_aerofolios,
    checar_convergencia
)
from gerenciador_graficos import GerenciaGraficos

if __name__ == '__main__':
    qde_iteracoes = 3
    qde_particulas = 5
    tolerancia = 0.005
    continuar = False

    condicao_de_voo = {
        "Velocidade": 62,
        "Viscosidade": 1.789e-5,
        "Temperatura": 288.2,
        "Densidade do Ar": 1.225,
        "Diametro da Helice": 96*0.0254,
        "Numero de pas": 2,
        "Rotacao do Motor": 1000.
    }

    condicoes_geometricas = {
        "raio": np.array([10, 12, 18, 24, 30, 36, 42, 48])*0.0254,
        "corda": np.array([4.82, 5.48, 6.86, 7.29, 7.06, 6.35, 5.06, 0])*0.0254,
    }

    id = gerar_time_stamp()
    criar_pastas(id)
    criar_logger(id)
    
    limpar_pasta_coordenadas_aerofolios()

    logger = logging.getLogger("logger_main")

    logger.info("\n----------Processamento Iniciado----------\n")
    otimization_controller = OtimizacaoHelice(
        qde_iteracoes=qde_iteracoes,
        qde_de_particulas=qde_particulas,
        condicao_de_voo=condicao_de_voo,
        id=id,
        condicoes_geometricas=condicoes_geometricas,
        continuar=continuar
    )

    media_distancias = np.array([])
    for _ in tqdm(range(qde_iteracoes)):
        time.sleep(5)
        otimization_controller.iterar()
        convergencia, _ = checar_convergencia(
            valores_fo=otimization_controller.fo,
            matriz=otimization_controller.matriz,
            tolerancia=tolerancia
        )
        # media_distancias = np.append(media_distancias, media)
        if convergencia:
            print(
                "Convergência atingida!"
            )
            break

    GerenciaGraficos(
        dados_pso=otimization_controller.resultados_matriz_pso,
        dados_aerodinamicos=otimization_controller.resultados_aerodinamicos,
        path_local_cenario=otimization_controller.path_pasta_cenario,
        passos_iteracao=otimization_controller.t_list,
        valores_fo=otimization_controller.convergencia,
        condicao_de_voo=condicao_de_voo,
        condicoes_geometricas=condicoes_geometricas
    )