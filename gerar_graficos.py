import pandas as pd
from gerenciador_graficos import GerenciaGraficos
from utilidades import (
    transformar_dados_json_para_objeto
)

if __name__ == "__main__":
    particula = 15
    iteracao = 49

    id = "2022-11-28T20h33"
    pasta = f"resultados/resultados_id_{id}"
    local_dados_aerodinamicos = f"{pasta}/resultados_aerodinamicos_helice_id_{id}.csv"
    local_dados_pso = f"{pasta}/resultados_matriz_pso_id_{id}.csv"
    path_local_arquivo = f"{pasta}"

    dados_json = transformar_dados_json_para_objeto(
        local_arquivo_json=f"{path_local_arquivo}/parametros_PSO_id_{id}.json"
    )

    dados_aerodinamicos = pd.read_csv(local_dados_aerodinamicos,sep=';')
    dados_pso = pd.read_csv(local_dados_pso,sep=';')

    GerenciaGraficos(
        dados_aerodinamicos=dados_aerodinamicos,
        dados_pso=dados_pso,
        path_local_cenario=path_local_arquivo,
        passos_iteracao=dados_json.get("t"),
        valores_fo=dados_json.get("convergencia"),
        condicao_de_voo=dados_json.get("condicao_voo"),
        condicoes_geometricas=dados_json.get("condicoes_geometricas"),
        graficos_externos=True,
        particula_escolhida=particula,
        iteracao_escolhida=iteracao
    )




    