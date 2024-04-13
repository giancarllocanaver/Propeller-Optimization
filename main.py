import argparse
import os
from PSO import OtimizacaoHelice
from tqdm import tqdm
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

from propeller_optmization.pipelines import PipelineMethods


def define_parser() -> dict:
    """
    Method responsible to create the parser arguments
    for the main function.

    :return: argument parser
    """
    parser = ArgumentParser(
        prog="main.py",
        description="Propeller Optimization input and output arguments",
        usage="%(prog)s [-f] <file> [-o]",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Complete '.json' file directory containing the parameters of the optimizer in the processing folder ('processing/inputs')",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="output directory for the output files",
        required=False,
        default=os.path.join(os.getcwd(), "processing", "outputs"),
    )

    return parser.parse_args()


def main(arguments_parsed: argparse.Namespace) -> None:
    """
    Main funtion of the propeller optimizer.
    """
    pipeline = PipelineMethods(arguments_parsed)
    logger = pipeline.logger

    try:
        pipeline.read_data()
        pipeline.create_xfoil_instances()
        pipeline.optimize()
        pipeline.obtain_results()
    except Exception as e:
        logger.exception(e, stack_info=True)

        raise e


if __name__ == "__main__":
    arguments_parsed = define_parser()
    main(arguments_parsed)


# if __name__ == '__main__':
#     argumentos_inicializacao = define_parser()
#     cenario_de_voo = ler_input(
#         argumentos_inicializacao.get("cenario"),
#     )
#     id = gerar_time_stamp()
#     pasta_com_id = criar_pastas(id)
#     criar_logger(id)

#     limpar_pasta_coordenadas_aerofolios()

#     logger = logging.getLogger("logger_main")

#     logger.info("\n----------Processamento Iniciado----------\n")
#     otimization_controller = OtimizacaoHelice(
#         qde_iteracoes=argumentos_inicializacao.get("qtde_iteracoes"),
#         qde_de_particulas=argumentos_inicializacao.get("qtde_particulas"),
#         condicao_de_voo=cenario_de_voo.get("condicao_de_voo"),
#         id=id,
#         condicoes_geometricas=cenario_de_voo.get("condicoes_geometricas"),
#         aerofolio_inicial=argumentos_inicializacao.get("aerofolio"),
#         alpha_maxima_eficiencia=argumentos_inicializacao.get("alpha"),
#         opcao_hiperparametros=argumentos_inicializacao.get("hiperparametros_constantes"),
#     )

#     for _ in tqdm(
#         range(argumentos_inicializacao.get("qtde_iteracoes"))
#     ):
#         time.sleep(5)
#         otimization_controller.iterar()
#         convergencia, _ = checar_convergencia(
#             valores_fo=otimization_controller.fo,
#             matriz=otimization_controller.matriz,
#             tolerancia=argumentos_inicializacao.get("tolerancia")
#         )
#         if convergencia:
#             print(
#                 "\n\n\nConvergência atingida!\n\n\n"
#             )
#             with open(f"{otimization_controller.path_pasta_cenario}/convergencia.txt", 'w') as file:
#                 file.write(
#                     f"Convergência atingida!\n"
#                     f"Número de iterações: {max(otimization_controller.t_list)}"
#                 )
#                 file.close()
#             break

#     GerenciaGraficos(
#         dados_pso=otimization_controller.resultados_matriz_pso,
#         dados_aerodinamicos=otimization_controller.resultados_aerodinamicos,
#         path_local_cenario=otimization_controller.path_pasta_cenario,
#         passos_iteracao=otimization_controller.t_list,
#         valores_fo=otimization_controller.convergencia,
#         condicao_de_voo=cenario_de_voo.get("condicao_de_voo"),
#         condicoes_geometricas=cenario_de_voo.get("condicoes_geometricas"),
#         melhor_particula=otimization_controller.id_melhor_particula
#     )

#     print(
#         f"\n\n--- FERRAMENTA DE OTIMIZAÇÃO FINALIZADA ---\n"
#         f"Resultados salvos no diretório: {pasta_com_id}"
#     )
