import pandas as pd
import matplotlib.pyplot as plt

arquivo = "resultados/resultados_id_2022-08-25T18h26/resultados_aerodinamicos_helice_id_2022-08-25T18h26.csv"
df1 = pd.read_csv(arquivo, sep=';')

resultado = df1.groupby(["Iteracao"])["eta"].max().to_list()
iteracao = df1["Iteracao"].unique().tolist()

plt.plot(iteracao, resultado, 'x')
plt.grid()
plt.xlabel("Iteração")
plt.ylabel("Eficiência")
plt.show()