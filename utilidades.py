import numpy as np
from funcao_helice import helice
import shutil

def rodar_helice_inidividual(
    condicoes_voo: dict,
    aerofolios: list,
    raio: np.ndarray,
    c: np.ndarray,
    beta: np.ndarray
):
    resultados = helice(
            Aerofolios=aerofolios,
            Velocidade_da_aeronave=condicoes_voo["Velocidade"],
            Viscosidade_dinamica=condicoes_voo["Viscosidade"],
            Temperatura=condicoes_voo["Temperatura"],
            Densidade_do_ar=condicoes_voo["Densidade do Ar"],
            Diametro_helice=condicoes_voo["Diametro da Helice"],
            Numero_de_pas=condicoes_voo["Numero de pas"],
            Array_raio_da_secao=raio,
            Array_tamanho_de_corda_da_secao=c,
            Array_angulo_beta_da_secao=beta,
            Rotacao_motor=condicoes_voo["Rotacao do Motor"],
            Solucoes_ligadas=['solucao_1'],
            ler_coord_arq_ext=True,
            ligar_solucao_aerof_naca=False,
            ligar_interpolacao_2a_ordem=True
        ).rodar_helice()

    return resultados


def criar_txt_pontos_aerofolio_para_rodar_xfoil(
    pontos: np.ndarray
):
    pontos = pontos.reshape((pontos.shape[0], pontos.shape[1]))
    pontos_x = pontos[0]
    pontos_y = pontos[1]

    id = np.random.randint(
        low=0,
        high=1000,
        dtype=int
    )
    nome_arquivo = "aerofolio" + str(id) + ".dat"
    
    with open(nome_arquivo, "w") as writer:
        for ponto in range(len(pontos_x)):
            writer.write(
                f"{round(pontos_x[ponto], 4)}    {round(pontos_y[ponto], 4)}\n"
            )
        writer.close()

    return nome_arquivo


def mover_arquivos_coordenadas(
    nome_arquivo
):
    shutil.move(nome_arquivo, f"coordenadas_aerofolios/{nome_arquivo}")