from datetime import datetime
import numpy as np
from funcao_helice import Helice, HeliceGeral
import shutil
import os
import pandas as pd
import json
import logging

def executar_TEP(
    condicoes_voo: dict,
    aerofolios: list,
    raio: np.ndarray,
    corda: np.ndarray,
    particula_com_interseccao: bool,
    **kwargs
) -> dict:
    """
    Método responsável por executar a Teoria dos Elementos
    de Pá para a hélice selecionada.
    
    :param condicoes_voo: condições de voo da hélice
    :param aerofolios: lista com os aerofólios ao longo da pá
    :param raio: raio das seções ao longo da pá
    :param corda: corda das seções ao longo da pá
    :param particula_com_interseccao: se True refere-se a uma
        partícula com intersecção
    ...
    :return: resultados obtidos advindos da Teoria dos Elementos
        de Pá
    """
    condicoes_geometricas = {
        "Raio Secao": raio,
        "Corda Secao": corda,
    }
    classe_helice = Helice(
        aerofolios=aerofolios,
        condicoes_voo=condicoes_voo,
        condicoes_geometricas_helice=condicoes_geometricas,
        particula_com_interseccao=particula_com_interseccao,
        alpha=kwargs.get("alpha")
    )
    classe_helice.executar_helice()

    return classe_helice.resultados


def criar_txt_pontos_aerofolio_para_rodar_xfoil(
    pontos: np.ndarray
) -> str:
    """
    Método responsável por criar um arquivo .txt com
    os pontos do aerofólio de uma seção da pá.

    :param pontos: pontos do aerofólio de uma seção da
        pá específica.
    ...
    :return: nome do arquivo do aerofólio criado
    """
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

    return nome_arquivo


def mover_arquivos_coordenadas(
    nome_arquivo: str
):
    """
    Método responsável por mover um arquivo contendo
    as coordenadas de um aerofólio para a pasta
    'coordenadas_aerofolios'.
    """
    if not os.path.isdir(f"coordenadas_aerofolios"):
        os.mkdir(f"coordenadas_aerofolios")
        
    if os.path.isfile(nome_arquivo):
        shutil.move(nome_arquivo, f"coordenadas_aerofolios/{nome_arquivo}")


def gravar_resultados_aerodinamicos(
    resultados: list,
    id: str,
    iteracao: int
) -> pd.DataFrame:
    """
    Método responsável por salvar os resultados relacionados
    à aerodinâmica da hélice em um arquivo '.csv', e retornar
    os resultados.

    :param resultados: resultados aerodinâmicos obtidos.
    :param id: identificador do cenário
    :param iteracao: iteração específica
    ...
    :return: dataframe com os resultados
    """
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


def criar_pastas(id):
    if not os.path.isdir("resultados"):
        os.mkdir("resultados")
    
    if not os.path.isdir(f"resultados/resultados_id_{id}"):
        os.mkdir(f"resultados/resultados_id_{id}")

    return f"resultados/resultados_id_{id}"


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
    beta = -1 * beta * np.pi / 180

    coordenadas_novas = coordenadas.copy()

    coordenadas_novas[:,0] =  np.cos(beta)*coordenadas[:,0] - np.sin(beta)*coordenadas[:,1]
    coordenadas_novas[:,1] =  np.sin(beta)*coordenadas[:,0] + np.cos(beta)*coordenadas[:,1]
    
    return coordenadas_novas


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


def transformar_dados_json_para_objeto(
    local_arquivo_json: str
):
    with open(local_arquivo_json,'rb') as file:
        arquivo_bytes = file.read()
        dados: dict = json.loads(arquivo_bytes)

    dados_array = [
        "eficiencia",
        "matriz_v",
        "matriz_pso",
        "p_best",
        "g_best",
        "p_best_obj",
        "g_best_obj",
    ]

    for dado_array in dados_array:
        dados[dado_array] = np.array(dados[dado_array])

    dados["condicoes_geometricas"]["raio"] = np.array(dados["condicoes_geometricas"]["raio"])
    dados["condicoes_geometricas"]["corda"] = np.array(dados["condicoes_geometricas"]["corda"])

    return dados


def checar_adequacao_espessura_perfil(
    vetor_escalares: np.ndarray
):
    for id_escalar in range(len(vetor_escalares)):
        if (vetor_escalares[0] > vetor_escalares[id_escalar]):
            return False
    
    return True


def escolher_escalar(secao):
    if secao == 0:
        escalar_menor = -0.05
        escalar_maior = -0.036
    
    if secao == 1:
        escalar_menor = -0.035
        escalar_maior = -0.021

    if secao == 2:
        escalar_menor = -0.02
        escalar_maior = -0.006
    
    if secao == 3:
        escalar_menor = -0.005
        escalar_maior = 0.009
    
    if secao == 4:
        escalar_menor = 0.01
        escalar_maior = 0.024

    if secao == 5:
        escalar_menor = 0.025
        escalar_maior = 0.039
    
    if secao == 6:
        escalar_menor = 0.04
        escalar_maior = 0.05

    return np.random.uniform(low=escalar_menor, high=escalar_maior)


def ler_input(cenario: str) -> dict:
    """
    Método responsável por estar lendo o
    arquivo de input na pasta 'fila_de_cenarios'

    :param cenario: nome do cenário a ser lido
        na pasta
    ...
    :return: dicionário contendo o cenário de
        configuração da hélice.
    """
    arquivo_a_ser_lido = f"fila_de_cenarios/{cenario}"
    with open(arquivo_a_ser_lido, 'rb') as file:
        cenario_lido = json.load(file)
        file.close()
    shutil.move(
        arquivo_a_ser_lido,
        f"fila_de_cenarios/antigos/{cenario}",
    )
    cenario_lido["condicoes_geometricas"]["raio"] = np.array(cenario_lido["condicoes_geometricas"]["raio"])
    cenario_lido["condicoes_geometricas"]["corda"] = np.array(cenario_lido["condicoes_geometricas"]["corda"])

    return cenario_lido