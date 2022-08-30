from funcoes_de_bezier import Bezier
from matplotlib import pyplot as plt
import numpy as np

bezier_controler = Bezier()
pontos_p = bezier_controler.gerar_aerofolio_base()
linhas, a0, b0, pontos_p = bezier_controler.gerar_pontos_de_bezier(retornar=True)

novos_A = a0.copy()
novos_A[0,0] = novos_A[0,0] - 0.05
novos_A[0,1] = novos_A[0,1] - 0.05
novos_A[0,2] = novos_A[0,2] + 0.05
novos_A[0,3] = novos_A[0,3] - 0.05

novos_A[1,0] = novos_A[1,0] - 0.005
novos_A[1,1] = novos_A[1,1] + 0.005
novos_A[1,2] = novos_A[1,2] - 0.005
novos_A[1,3] = novos_A[1,3] + 0.005

novas_linhas, a1, b1, novos_pontos_p = bezier_controler.atualizar_aerofolio(
    pontos_x=novos_A[0],
    pontos_y=novos_A[1],
    pontos_p=pontos_p
)


plt.plot(linhas[0], linhas[1])
plt.plot(novas_linhas[0], novas_linhas[1])
plt.plot(a0[0], a0[1], 'x')
plt.plot(a1[0], a1[1], 'x')
plt.grid()
plt.ylim((-0.1,0.1))
plt.show()