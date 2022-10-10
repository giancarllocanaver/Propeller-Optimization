import pandas as pd
from matplotlib import pyplot as plt

df_eta_j = pd.read_csv("eta_j_naca.csv", sep=';').replace(",", ".", regex=True).astype("float")
df_ct_j = pd.read_csv("ct_j_naca.csv", sep=';').replace(",", ".", regex=True).astype("float")

df_resultados = pd.read_csv("Resultados-validacao-helice.csv", sep=';')[["J", "eta", "Ct"]]

df_resultados_para_ct = df_resultados[df_resultados["J"] >= 0.4]

plt.plot(
    df_ct_j["J"].values, df_ct_j["Ct"].values, '--'
)
plt.plot(
    df_resultados_para_ct["J"].values, df_resultados_para_ct["Ct"].values, '--'
)
plt.xlabel(r"Razão de Avanço ( $J$ )")
plt.ylabel(r"Coeficiente de Tração ( $C_T$ )")
plt.legend(("NACA Report", "Obtido via TEP"))
plt.grid()
plt.savefig("Resultados-validacao-helice-J-Ct.jpg")

print('ok')