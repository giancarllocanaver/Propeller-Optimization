from datetime import datetime
import numpy as np
from funcao_helice import Helice, HeliceGeral
import shutil
import os
import pandas as pd
import json
import logging

def rodar_helice_inidividual(
    condicoes_voo: dict,
    aerofolios: list,
    raio: np.ndarray,
    c: np.ndarray,
    particula_com_interseccao: bool
):
    condicoes_geometricas = {
        "Raio Secao": raio,
        "Corda Secao": c
    }
    classe_helice = Helice(
        aerofolios=aerofolios,
        condicoes_voo=condicoes_voo,
        condicoes_geometricas_helice=condicoes_geometricas,
        particula_com_interseccao=particula_com_interseccao
    )

    return classe_helice.resultados


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
    nome_arquivo = "coordenadas_aerofolios/aerofolio" + str(id) + ".dat"
    
    with open(nome_arquivo, "w") as writer:
        for ponto in range(len(pontos_x)):
            writer.write(
                f"{round(pontos_x[ponto], 4)}    {round(pontos_y[ponto], 4)}\n"
            )
        writer.close()

    # shutil.copy(
    #     src=f"{nome_arquivo}",
    #     dst=f"coordenadas_aerofolios/{nome_arquivo}"
    # )

    return nome_arquivo


def mover_arquivos_coordenadas(
    nome_arquivo
):
    if not os.path.isdir(f"coordenadas_aerofolios"):
        os.mkdir(f"coordenadas_aerofolios")
        
    if os.path.isfile(nome_arquivo):
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

    return df_resultados


def gravar_resultados_matriz_pso(
    resultados,
    id,
    iteracao,
    fo
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
        "escalar 1 Ay3",
        "escalar 2 Ay3",
        "escalar 3 Ay3",
        "escalar 4 Ay3",
        "escalar 5 Ay3",
        "escalar 6 Ay3",
        "escalar 7 Ay3",
        "particula",
        "iteracao",
        "fo"
    ]

    for particula in range(len(resultados)):
        resultado = resultados[particula].tolist()
        fo_particula = fo[particula]
        resultado.append(particula)
        resultado.append(iteracao)
        resultado.append(fo_particula)

        df_resultado = pd.DataFrame(
            resultado
        ).transpose()

        df_resultado.columns = colunas

        if (particula == 0) and not (existe_output):
            df_resultados = df_resultado.copy()
        else:
            df_resultados = pd.concat([df_resultados, df_resultado], axis=0)

    df_resultados.to_csv(path_output_matriz_pso, sep=';', index=False)

    return path_output_matriz_pso, df_resultados


def salvar_resultados_json(
    matriz_v: np.ndarray,
    matriz_pso: np.ndarray,
    id: str,
    **kwargs
):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")

    arquivo = {
        "eficiencia": kwargs.get("eficiencia").tolist(),
        "matriz_v": matriz_v.tolist(),
        "matriz_pso": matriz_pso.tolist(),
        "p_best": kwargs.get("p_best").tolist(),
        "g_best": kwargs.get("g_best").tolist(),
        "r": kwargs.get("r").tolist(),
        "qde_particulas": kwargs.get("qde_particulas"),
        "condicao_voo": kwargs.get("condicao_voo"),
        "condicoes_geometricas": kwargs.get("condicoes_geometricas"),
        "p_best_obj": kwargs.get("p_best_obj").tolist(),
        "g_best_obj": kwargs.get("g_best_obj").tolist(),
        "w": kwargs.get("w"),
        "c1": kwargs.get("c1"),
        "c2": kwargs.get("c2"),
        "t": kwargs.get("t"),
        "convergencia": kwargs.get("convergencia"),
    }

    nome_arq = f"resultados/resultados_id_{id}/parametros_PSO_id_{id}.json"
    with open(nome_arq, 'w') as file:
        json.dump(arquivo,file)


def criar_pastas(id):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")


def gerar_time_stamp():
    stamp = datetime.now().isoformat(timespec='minutes')
    stamp = stamp.replace(":","h")

    return stamp


def criar_logger(id):
    logger = logging.getLogger("logger_main")
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(f"resultados/resultados_id_{id}/logger_id_{id}.txt", mode='a')
    logger.addHandler(handler)


def limpar_pasta_coordenadas_aerofolios():
    if os.path.isdir("coordenadas_aerofolios"):
        arquivos = os.listdir("coordenadas_aerofolios")

        if len(arquivos) != 0:
            for arquivo in arquivos:
                os.remove(f"coordenadas_aerofolios/{arquivo}")


def montar_array_coordenadas_aerofolios(
    nome_coordenada_aerofolio: str
):
    coordenadas = np.loadtxt(
        f"{nome_coordenada_aerofolio}"
    )

    return coordenadas


def aplicar_rotacao(
    coordenadas: np.ndarray,
    beta: float
):
    coordenadas[:,0] = coordenadas[:,0] - 0.5
    beta = beta * np.pi / 180

    coordenadas[:,0] =  np.cos(beta)*coordenadas[:,0] + np.sin(beta)*coordenadas[:,1]
    coordenadas[:,1] = -np.sin(beta)*coordenadas[:,0] + np.cos(beta)*coordenadas[:,1]
    
    return coordenadas


def montar_array_dT_dr_e_dQ(
    df: pd.DataFrame
):
    selecao_colunas_dT = [f"dT Seção {secao}" for secao in range(7)]
    selecao_colunas_dQ = [f"dQ Seção {secao}" for secao in range(7)]
    selecao_colunas_dr = [f"dr Seção {secao}" for secao in range(7)]

    dT_values = df.loc[:,selecao_colunas_dT].values
    dQ_values = df.loc[:,selecao_colunas_dQ].values
    dr_values = df.loc[:,selecao_colunas_dr].values

    return {
        "dT values": dT_values,
        "dQ_values": dQ_values,
        "dr values": dr_values
    }


def gerar_dados_diveras_velocidades(
    df: pd.DataFrame,
    corda: np.ndarray,
    raio: np.ndarray,
    condicoes_de_voo: dict
):
    nomes_coordenadas_aerofolios = [f"Aerofolio secao {secao}" for secao in range(7)]
    nomes_betas = [f"Beta {secao}" for secao in range(8)]
    aerofolios = df.loc[:, nomes_coordenadas_aerofolios].values.tolist()[0]
    betas = df.loc[:, nomes_betas].values.tolist()[0]
    
    velocidades = [vel for vel in range(1,100, 5)]

    resultados_totais = []
    resultados_ct = []
    resultados_cq = []
    resultados_eta = []
    J_list = []

    condicoes_geometricas = {
        "Raio Secao": raio,
        "Corda Secao": corda,
        "Beta": np.array(betas)
    }

    for velocidade in velocidades:
        condicoes_de_voo["Velocidade"] = velocidade
        helice_contoller = HeliceGeral(
            aerofolios=aerofolios,
            condicoes_geometricas=condicoes_geometricas,
            condicoes_de_voo=condicoes_de_voo
        )
        resultados_individuais = helice_contoller.resultados

        if (resultados_individuais["eficiencia"][0] > 1) or (resultados_individuais["eficiencia"][0] < 0):
            break
        else:
            resultados_totais.append(resultados_individuais)
            J_list.append(resultados_individuais["J"])
            resultados_eta.append(resultados_individuais["eficiencia"][0])
            resultados_ct.append(resultados_individuais["Ct"])
            resultados_cq.append(resultados_individuais["Cq"])

    return {
        "resultados_totais": resultados_totais,
        "resultados Ct": resultados_ct,
        "resultados Cq": resultados_cq,
        "resultados eficiencia": resultados_eta,
        "razão de avanço": J_list
    }


def checar_convergencia(
    valores_fo: np.ndarray,
    matriz: np.ndarray,
    tolerancia: float
):
    melhor_particula = np.argmax(valores_fo)
    soma_convergencias = 0
    media_distancias = np.array([])
    for variavel in range(7):
        valor_variavel_melhor_paticula = np.max(matriz[melhor_particula,variavel])

        distancias_variavel = matriz[:,variavel] - valor_variavel_melhor_paticula
        distancias_abs = np.abs(distancias_variavel)
        media_distancias = np.mean(distancias_abs)

        if media_distancias <= tolerancia:
            soma_convergencias += 1
        media_distancias = np.append(media_distancias, media_distancias)

    media = np.mean(media_distancias)

    if soma_convergencias == 7:
        return True, media
    else:
        return False, media


def ler_dados_para_continuacao():
    arquivos = os.listdir(
        "fila_continuacao"
    )
    nome_arquivo = arquivos[0]

    with open(f"fila_continuacao/{nome_arquivo}", 'rb') as file:
        arquivo_bytes = file.read()
    
    dados = json.loads(arquivo_bytes)
    return dados