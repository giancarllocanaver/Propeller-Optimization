import numpy as np
from funcao_helice import helice
import shutil
import os
import pandas as pd
import json

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
    if not os.path.isdir(f"coordenadas_aerofolios"):
        os.mkdir(f"coordenadas_aerofolios")
        
    shutil.move(nome_arquivo, f"coordenadas_aerofolios/{nome_arquivo}")


def gravar_resultados_aerodinamicos(
    resultados,
    id,
    iteracao
):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")

    nome_arq_output = f"resultados_aerodinamicos_helice_id_{id}.csv"
    path_output_aerodinamico = f"resultados/resultados_id_{id}/{nome_arq_output}"

    existe_output = 0

    if os.path.isfile(path_output_aerodinamico):
        df_resultados = pd.read_csv(path_output_aerodinamico, sep=';')
        existe_output = 1
    
    for particula in range(len(resultados)):
        resultado = resultados[particula]
        resultado["Particula"] = particula
        resultado["Iteracao"] = iteracao
        
        df_resultado = pd.DataFrame(resultado)

        if (particula == 0) and not (existe_output):
            df_resultados = df_resultado.copy()
        else:
            df_resultados = pd.concat([df_resultados, df_resultado], axis=0)

    df_resultados.to_csv(path_output_aerodinamico, sep=';', index=False)


def gravar_resultados_matriz_pso(
    resultados,
    id,
    iteracao
):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")

    nome_arq_output = f"resultados_matriz_pso_id_{id}.csv"
    path_output_matriz_pso = f"resultados/resultados_id_{id}/{nome_arq_output}"

    existe_output = 0

    if os.path.isfile(path_output_matriz_pso):
        df_resultados = pd.read_csv(path_output_matriz_pso, sep=';')
        existe_output = 1

    colunas = [
        "beta 1",
        "beta 2",
        "beta 3",
        "beta 4",
        "beta 5",
        "beta 6",
        "beta 7",
        "Ax 1",
        "Ax 2",
        "Ax 3",
        "Ax 4",
        "Ay 1",
        "Ay 2",
        "Ay 3",
        "Ay 4",
        "Particula",
        "Iteracao"
    ]

    for particula in range(len(resultados)):
        resultado = resultados[particula].tolist()
        resultado.append(particula)
        resultado.append(iteracao)

        df_resultado = pd.DataFrame(
            resultado
        ).transpose()

        df_resultado.columns = colunas

        if (particula == 0) and not (existe_output):
            df_resultados = df_resultado.copy()
        else:
            df_resultados = pd.concat([df_resultados, df_resultado], axis=0)

    df_resultados.to_csv(path_output_matriz_pso, sep=';', index=False)


def salvar_resultados_json(
    eficiencia,
    matriz_v,
    matriz_pso,
    p_best,
    g_best,
    r,
    id
):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")

    arquivo = {
        "eficiencia": eficiencia.tolist(),
        "matriz_v": matriz_v.tolist(),
        "matriz_pso": matriz_pso.tolist(),
        "p_best": p_best.tolist(),
        "g_best": g_best.tolist(),
        "r": r.tolist()
    }

    nome_arq = f"resultados/resultados_id_{id}/parametros_PSO_id_{id}.json"
    with open(nome_arq, 'w') as file:
        json.dump(arquivo,file)