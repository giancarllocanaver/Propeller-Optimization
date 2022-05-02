import numpy as np
from funcoes_helice_2 import helice
from funcoes_de_bezier_2 import Bezier
import matplotlib.pyplot as plt
import pandas as pd

bezier = Bezier()
linhas, _, _ = bezier.gerar_bezier(tamanho_entre_pontos=10, retornar=True)

bezier.mudar_A(ponto=2, mudanca_x=0, mudanca_y=0, mudanca_adicional=True)

linhas, _, _, _ = bezier.bezier_mudar_A(tamanho=10)

aerofolios = [linhas for _ in range(8)]

raio = np.array([10, 12, 18, 24, 30, 36, 42, 48]) * 0.0254
beta = np.array([46.3, 43.25, 38.1, 31.65, 26.3, 22.4, 19.5, 0]) * np.pi / 180.0
c = np.array([4.82, 5.48, 6.86, 7.29, 7.06, 6.35, 5.06, 0]) * 0.0254

v_list = [i for i in range(50, 210, 10)]
rpm_list = [i for i in range(500, 10000, 100)]
eficiencia_list = []

df_resultados_helice = pd.DataFrame({"Velocidade": [], "RPM": [], "Eficiencia": []})
df_resultados_aerof = pd.DataFrame(
    {"Velocidade": [], "RPM": [], "Alpha": [], "Re": [], "Cl": [], "Cd": [], "Tipo": []}
)

for v in v_list:
    for rpm in rpm_list:
        eta, df_resultados_aerof = helice(
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
            solucao_viscosa=False,
            validacao=df_resultados_aerof,
        ).rodar_helice()

        df_resultados_helice = df_resultados_helice.append(
            pd.DataFrame({"Velocidade": [v], "RPM": [rpm], "Eficiencia": [eta]}),
            ignore_index=True,
        )


with pd.ExcelWriter("Resultados-validacao.xlsx") as writer:
    df_resultados_helice.to_excel(writer, sheet_name="Resultados Helice")
    df_resultados_aerof.to_excel(writer, sheet_name="Resultados Aerofolio")
    writer.save()

df_resultados_helice.to_csv("Resultados_helice.csv")
df_resultados_aerof.to_csv("Resultados_aerof.csv")
