from turtle import color
from funcoes_de_bezier import Bezier
from matplotlib import pyplot as plt
import numpy as np

bezier_controler = Bezier()
pontos_p = bezier_controler.gerar_aerofolio(aerofolio='aerofolioClarkY.txt')
linhas, a0, b0, pontos_p = bezier_controler.gerar_pontos_de_bezier(retornar=True)

x_pt_1 = []
y_pt_1 = []
x_pt_2 = []
y_pt_2 = []
x_pt_3 = []
y_pt_3 = []
x_pt_4 = []
y_pt_4 = []

x_individuais = []
y_individuais = []

for ponto in range(len(linhas[0])):
    if ponto <= 20:
        x_pt_1.append(linhas[0][ponto][0])
        y_pt_1.append(linhas[1][ponto][0])
    if (ponto >= 20) and (ponto <= 40):
        x_pt_2.append(linhas[0][ponto][0])
        y_pt_2.append(linhas[1][ponto][0])
    if (ponto >= 40) and (ponto <= 60):
        x_pt_3.append(linhas[0][ponto][0])
        y_pt_3.append(linhas[1][ponto][0])
    if (ponto >= 60) and (ponto <= 80):
        x_pt_4.append(linhas[0][ponto][0])
        y_pt_4.append(linhas[1][ponto][0])

    if (ponto == 20) or (ponto == 40) or (ponto == 60) or (ponto == 79):
        x_individuais.append(linhas[0][ponto][0])
        y_individuais.append(linhas[1][ponto][0])

plt.plot(x_pt_1, y_pt_1, '--', color='b')
plt.plot(x_pt_2, y_pt_2, '--', color='y')
plt.plot(x_pt_3, y_pt_3, '--', color='r')
plt.plot(x_pt_4, y_pt_4, '--', color='g')
plt.legend(("k: 0","k: 1","k: 2","k: 3",))
plt.plot(a0[0][0],a0[1][0], 'o', color='b')
plt.plot(b0[0][0],b0[1][0], 'o', color='b')
plt.plot(a0[0][1],a0[1][1], 'o', color='y')
plt.plot(b0[0][1],b0[1][1], 'o', color='y')
plt.plot(a0[0][2],a0[1][2], 'o', color='r')
plt.plot(b0[0][2],b0[1][2], 'o', color='r')
plt.plot(a0[0][3],a0[1][3], 'o', color='g')
plt.plot(b0[0][3],b0[1][3], 'o', color='g')
plt.plot(x_individuais,y_individuais, 'o', color='black')
plt.text(x_individuais[0],y_individuais[0],r"$ (P_{4,0},P_{1,1}) $",verticalalignment="bottom")
plt.text(x_individuais[1],y_individuais[1],r"$ (P_{4,1},P_{1,2}) $")
plt.text(x_individuais[2],y_individuais[2],r"$ (P_{4,2},P_{1,3}) $",verticalalignment="top")
plt.text(x_individuais[3],y_individuais[3],r"$ (P_{1,0},P_{4,3}) $")
plt.grid()
plt.ylim((-0.2,0.2))
plt.xlabel("x")
plt.ylabel("y")
plt.savefig("resultados_relatorio/figurasRelatorioAteMetodologia/exemplo-segmentacao-bezier-aerofolio.jpeg")
plt.show()