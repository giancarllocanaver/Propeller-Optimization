from matplotlib import pyplot as plt

pontos_x_reta_1 = [0.8,0.4]
pontos_x_reta_2 = [0.3,0.9]

pontos_y_reta_1 = [0.05,0.1]
pontos_y_reta_2 = [0.04,0.12]

plt.plot(pontos_x_reta_1,pontos_y_reta_1, color='skyblue')
plt.plot(pontos_x_reta_2,pontos_y_reta_2, color='skyblue')
plt.plot([0.8],[0.05], 'o', color='orange')
plt.plot([0.4],[0.1], 'o', color='orange')
plt.plot([0.3],[0.04], 'o', color='orange')
plt.plot([0.9],[0.12], 'o', color='orange')
plt.plot([0.58],[0.0776], 'o', color='black')
plt.text(0.8,0.05,r"$  (p_{x_1},p_{y_1})  $",horizontalalignment='left')
plt.text(0.4,0.1,r"$  (p_{x_2},p_{y_2})  $",horizontalalignment='right')
plt.text(0.3,0.04,r"$  (p_{x_3},p_{y_3})  $",horizontalalignment='right')
plt.text(0.9,0.12,r"$  (p_{x_4},p_{y_4})  $",horizontalalignment='left')
plt.text(0.58,0.0776,r"$  (p_{ix},p_{iy})  $")
plt.xlim((0.2,1))
plt.ylim((0,0.15))
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.savefig("resultados_relatorio/figurasRelatorioAteMetodologia/exemplo-interseccao-retas.jpeg")
plt.show()