import os
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
    checar_convergencia,
    ler_input,
)
from gerenciador_graficos import GerenciaGraficos
from argparse import ArgumentParser


def definir_parser() -> dict:
    """
    Método responsável por definir o parser para o script
    'main.py'.

    :return: dicionário contendo as informações obtidas pelo
        parser
    """
    os.makedirs("fila_de_cenarios/antigos", exist_ok=True)
    arquivos_fila = os.listdir("fila_de_cenarios")
    arquivos_fila.remove("antigos")
    if not len(arquivos_fila):
        raise FileNotFoundError("Não existem cenários na pasta 'fila_de_cenarios'")

    parser = ArgumentParser(
        prog="python main.py"
    )

    parser.add_argument(
        "-c",
        "--cenario",
        default=arquivos_fila[0],
        type=str,
        help="nome do cenário presente na fila de cenários",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--particulas",
        default=20,
        type=int,
        help="quantidade de partículas",
        required=False,
    )
    parser.add_argument(
        "-i",
        "--iteracoes",
        type=int,
        default=15,
        help="quantidade de iterações máxima",
        required=False,
    )
    parser.add_argument(
        "-t",
        "--tolerancia",
        default=0.0001,
        type=float,
        help="tolerância de convergência da otimização",
        required=False,
    )
    parser.add_argument(
        "-af",
        "--aerofolio",
        default="naca 0020",
        type=str,
        help="aerofólio utilizado na otimização",
        required=False,
    )
    parser.add_argument(
        "-a",
        "--alpha",
        default=5.0,
        type=float,
        help="ângulo de ataque de eficiência máxima",
        required=False,
    )
    parser.add_argument(
        "-hc",
        "--hiperparametros_constantes",
        default=False,
        type=bool,
        help="setar hiperparâmetros constantes ao longo da iteração",
        required=False,
    )

    argumentos_parser = parser.parse_args()

    return {
        "cenario": argumentos_parser.cenario,
        "qtde_particulas": argumentos_parser.particulas,
        "qtde_iteracoes": argumentos_parser.iteracoes,
        "tolerancia": argumentos_parser.tolerancia,
        "aerofolio": argumentos_parser.aerofolio,
        "alpha": argumentos_parser.alpha,
        "hiperparametros_constantes": argumentos_parser.hiperparametros_constantes,
    }



if __name__ == '__main__':
    argumentos_inicializacao = definir_parser()
    cenario_de_voo = ler_input(
        argumentos_inicializacao.get("cenario"),
    )
    id = gerar_time_stamp()
    pasta_com_id = criar_pastas(id)
    criar_logger(id)
    
    limpar_pasta_coordenadas_aerofolios()

    logger = logging.getLogger("logger_main")

    logger.info("\n----------Processamento Iniciado----------\n")
    otimization_controller = OtimizacaoHelice(
        qde_iteracoes=argumentos_inicializacao.get("qtde_iteracoes"),
        qde_de_particulas=argumentos_inicializacao.get("qtde_particulas"),
        condicao_de_voo=cenario_de_voo.get("condicao_de_voo"),
        id=id,
        condicoes_geometricas=cenario_de_voo.get("condicoes_geometricas"),
        aerofolio_inicial=argumentos_inicializacao.get("aerofolio"),
        alpha_maxima_eficiencia=argumentos_inicializacao.get("alpha"),
        opcao_hiperparametros=argumentos_inicializacao.get("hiperparametros_constantes"),
    )

    for _ in tqdm(
        range(argumentos_inicializacao.get("qtde_iteracoes"))
    ):
        time.sleep(5)
        otimization_controller.iterar()
        convergencia, _ = checar_convergencia(
            valores_fo=otimization_controller.fo,
            matriz=otimization_controller.matriz,
            tolerancia=argumentos_inicializacao.get("tolerancia")
        )
        if convergencia:
            print(
                "\n\n\nConvergência atingida!\n\n\n"
            )
            with open(f"{otimization_controller.path_pasta_cenario}/convergencia.txt", 'w') as file:
                file.write(
                    f"Convergência atingida!\n"
                    f"Número de iterações: {max(otimization_controller.t_list)}"
                )
                file.close()
            break

    GerenciaGraficos(
        dados_pso=otimization_controller.resultados_matriz_pso,
        dados_aerodinamicos=otimization_controller.resultados_aerodinamicos,
        path_local_cenario=otimization_controller.path_pasta_cenario,
        passos_iteracao=otimization_controller.t_list,
        valores_fo=otimization_controller.convergencia,
        condicao_de_voo=cenario_de_voo.get("condicao_de_voo"),
        condicoes_geometricas=cenario_de_voo.get("condicoes_geometricas"),
        melhor_particula=otimization_controller.id_melhor_particula
    )

    print(
        f"\n\n--- FERRAMENTA DE OTIMIZAÇÃO FINALIZADA ---\n"
        f"Resultados salvos no diretório: {pasta_com_id}"
    )