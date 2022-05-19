import numpy as np
from funcao_helice import helice
from funcoes_de_bezier import Bezier
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

"""
-----------------
VALIDACOES
-----------------

Script com objetivo de testar as funções para alguns valores específicos
"""

# Geração do aerofólio pelas funções de Bezier
dados = pd.read_excel('helice-dados.xlsx')

diametro_helice = 3.0
numero_pas = 2
raio = dados["r"].to_numpy()
beta = dados["beta"].to_numpy()
c = dados["b"].to_numpy()

# Inputs da simulação
# v_list = [i for i in np.arange(20.32, 52.832, 1.0837)]
v_list = [i for i in np.arange(20, 30, 1)]
rpm = 1000

# Geração de um DataFrame para validação
df_resultados_helice = pd.DataFrame({"Velocidade": [], "RPM": [], "Eficiencia": []})
df_resultados_aerof = pd.DataFrame(
    {"Velocidade": [], "RPM": [], "Alpha": [], "Re": [], "Cl": [], "Cd": [], "Tipo": []}
)

aerofolios = ['clarky.txt' for _ in range(len(c))]

for v in v_list:
    eta, df_aerof = helice(
        aerofolios,
        v,
        1.789e-5,
        288.2,
        1.225,
        96 * 0.0254,
        2,
        raio,
        c,
        beta,
        rpm,
        ler_coord_arq_ext=True,
        validacao=True,
    ).rodar_helice()

    df_resultados_helice = df_resultados_helice.append(
        pd.DataFrame({"Velocidade": [v], "RPM": [rpm], "Eficiencia": [eta]}),
        ignore_index=True,
    )

    df_resultados_aerof = pd.concat([df_resultados_aerof,df_aerof], axis=0, ignore_index=True)

df_resultados_helice["J"] = df_resultados_helice["Velocidade"]/(1000/60)/diametro_helice

# Geração do arquivo em Excel
now = datetime.now()
with pd.ExcelWriter("Resultados-validacao-" + now.strftime("%d-%m-%Y %H-%M") +".xlsx") as writer:
    df_resultados_helice.to_excel(writer, sheet_name="Resultados Helice")
    df_resultados_aerof.to_excel(writer, sheet_name="Resultados Aerofolio")
    writer.save()
