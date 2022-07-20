import numpy as np


class Bezier:
    """
    -----------------
    FUNCOES DE BEZIER
    -----------------

    Classe com objetivo de execultar diversas funcionalidades de Bezier
    """
    def __init__(self, aerofolio_base=True, arquivo_base="", linhas_a_pular=None, arquivo=None):
        self.linhas = None
        self.A_out = None
        self.B_out = None
                
        if aerofolio_base:
            x = np.array([1, 0.32957, 0, 0.32957, 1])
            y = np.array([0, 0.04497, 0, -0.04497, 0])

            self.arquivo_coord_aerof = np.array((x, y))

        if not aerofolio_base:
            self.arquivo_coord_aerof = np.loadtxt(
                arquivo_base, skiprows=linhas_a_pular
            )

            x = arquivo[:, 0]
            y = arquivo[:, 1]
            y[0] = 0
            y[-1] = 0

            self.arquivo_coord_aerof = np.array((x, y))

    def gerar_bezier(self, tamanho_entre_pontos, retornar=False):
        """
        Gera os coeficientes de Bezier (A,B) e interpola linhas

        inputs:
            tamanho_entre_pontos: quantidade de pontos entre os pontos P, 'int'

            retornar: retorna os parâmetros de Bezier, por definição, False

        output:
            linhas,A_out,B_out


            linhas: contorno das linhas geradas pela interpolação, numpy array
                - Linha 0: pontos x
                - Linha 1: ponstos y


            A: pontos A, numpy array
                - Linha 0: pontos x
                - Linha 1: ponstos y


            B: pontos B, , numpy array
                - Linha 0: pontos x
                - Linha 1: ponstos y
        """

        pontos_p = self.arquivo_coord_aerof.copy()

        def interseccao(curvas):
            def intersection(x1, x2, x3, x4, y1, y2, y3, y4):
                d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if d:
                    xs = (
                        (x1 * y2 - y1 * x2) * (x3 - x4)
                        - (x1 - x2) * (x3 * y4 - y3 * x4)
                    ) / d
                    ys = (
                        (x1 * y2 - y1 * x2) * (y3 - y4)
                        - (y1 - y2) * (x3 * y4 - y3 * x4)
                    ) / d
                    if (
                        xs >= min(x1, x2)
                        and xs <= max(x1, x2)
                        and xs >= min(x3, x4)
                        and xs <= max(x3, x4)
                    ):
                        return xs, ys

            xs, ys = [], []

            for i in range(len(curvas[0]) - 1):
                for j in range(i - 1):
                    if xs_ys := intersection(
                        curvas[0, i],
                        curvas[0, i + 1],
                        curvas[0, j],
                        curvas[0, j + 1],
                        curvas[1, i],
                        curvas[1, i + 1],
                        curvas[1, j],
                        curvas[1, j + 1],
                    ):
                        xs.append(xs_ys[0])
                        ys.append(xs_ys[1])

            if len(xs) > 1:
                return 1
            else:
                return 0

        def coeficientes_de_bezier(pontos_p):
            n = len(pontos_p) - 1

            M = np.zeros((n, n))

            M[0, 0] = 2.0
            M[-1, -1] = 7.0

            np.fill_diagonal(M[1:], 1.0)
            np.fill_diagonal(M[0:-1, 1:], 1.0)
            np.fill_diagonal(M[1:-1, 1:-1], 4.0)

            M[-1, -2] = 2.0

            u = np.zeros((n, 1))

            for i in range(n):
                u[i] = 2 * (2 * pontos_p[i] + pontos_p[i + 1])

            u[0, 0] = pontos_p[0] + 2 * pontos_p[1]
            u[-1, 0] = 8 * pontos_p[-2] + pontos_p[-1]

            a = np.linalg.solve(M, u)
            b = np.zeros(n)

            for i in range(n - 1):
                b[i] = 2 * pontos_p[i + 1] - a[i + 1]

            b[n - 1] = (a[n - 1] + pontos_p[n]) / 2

            return a, b

        def curva(i, j, a, b):
            return (
                lambda t: (1 - t) ** 3 * i
                + 3 * t * (1 - t) ** 2 * a
                + 3 * t**2 * (1 - t) * b
                + t**3 * j
            )

        n = len(pontos_p[0]) - 1

        for j in range(2):
            a, b = coeficientes_de_bezier(pontos_p[j])
            curvas = [
                curva(pontos_p[j, i], pontos_p[j, i + 1], a[i], b[i]) for i in range(n)
            ]

            curva_de_bezier = [
                h(t)
                for h in curvas
                for t in np.linspace(0, 1, num=tamanho_entre_pontos)
            ]

            if j == 0:
                linhas_1 = curva_de_bezier
                A_out_1 = a
                B_out_1 = b
            else:
                linhas_2 = curva_de_bezier
                A_out_2 = a
                B_out_2 = b

            curvas = []
            curva_de_bezier = []

        linhas = np.array((linhas_1, linhas_2))
        A_out = np.array((A_out_1, A_out_2))
        B_out = np.array((B_out_1, B_out_2))

        self.linhas = np.reshape(
            linhas, (linhas.shape[0], linhas.shape[1])
        )
        self.A_out = np.reshape(A_out, (A_out.shape[0], A_out.shape[1]))
        self.B_out = B_out.copy()

        if retornar == True:
            return linhas, A_out, B_out

    def mudar_A(
        self, ponto, mudanca_x, mudanca_y, mudanca_adicional=True, retornar=False
    ):
        """
        Esta função realiza a mudança nos pontos A de Bezier!

        inputs:
            ponto: número do ponto a ser modificado (começa em 1)

            mudanca_x: alteração da coordenada em x

            mudanca_y: alteração da coordenada em y

            mudanca_adicional: realiza uma substituição nos pontos A, por definição, False

            retornar: retorna os novos valores de A
        """
        a = self.A_out.copy()
        if mudanca_adicional == True:
            a[0, (ponto - 1)] += mudanca_x
            a[1, (ponto - 1)] += mudanca_y
        else:
            a[0, (ponto - 1)] = mudanca_x
            a[1, (ponto - 1)] = mudanca_y

        self.A_out = a.copy()

        if retornar == True:
            return a

    def bezier_mudar_A(self, tamanho):
        """
        Esta definição consegue gerar novas curvas a partir da mudança dos pontos A de Bezier

        inputs:
            tamanho: quantidade de pontos entre os pontos P, 'int'

        output:
            linhas, A_out, B_out, novos_pontos_P

            linhas: curvas geradas, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y


            A_out: pontos B gerados, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y


            B_out: pontos B gerados, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y


            novos_pontos_P: novos pontos P gerados, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y
        """

        pontos = self.arquivo_coord_aerof.copy()
        a = self.A_out.copy()

        def escala(novas_curvas):
            theta_1 = np.min(novas_curvas[0])
            theta_2 = np.max(novas_curvas[0])

            x = np.array([])
            y = np.array([])

            for i in novas_curvas[0]:
                x_novo = -1 / (theta_1 - theta_2) * (i - theta_2) + 1

                # if x_novo < 1e-05:
                #     x_novo = 0

                x = np.append(x, x_novo)

            for i in range(len(x)):
                if x[i] == np.min(x):
                    x[i] = 0

            for i in novas_curvas[1]:
                y_novo = i / (theta_2 - theta_1)

                y = np.append(y, y_novo)

            new_scale = [x, y]

            return np.array(new_scale)

        def interseccao(curvas):
            def intersection(x1, x2, x3, x4, y1, y2, y3, y4):
                d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if d:
                    xs = (
                        (x1 * y2 - y1 * x2) * (x3 - x4)
                        - (x1 - x2) * (x3 * y4 - y3 * x4)
                    ) / d
                    ys = (
                        (x1 * y2 - y1 * x2) * (y3 - y4)
                        - (y1 - y2) * (x3 * y4 - y3 * x4)
                    ) / d
                    if (
                        xs >= min(x1, x2)
                        and xs <= max(x1, x2)
                        and xs >= min(x3, x4)
                        and xs <= max(x3, x4)
                    ):
                        return xs, ys

            xs, ys = [], []

            for i in range(0, (len(curvas[0]) - 1), 1):
                for j in range(0, (i - 1), 1):
                    if xs_ys := intersection(
                        curvas[0, i],
                        curvas[0, i + 1],
                        curvas[0, j],
                        curvas[0, j + 1],
                        curvas[1, i],
                        curvas[1, i + 1],
                        curvas[1, j],
                        curvas[1, j + 1],
                    ):
                        xs.append(xs_ys[0])
                        ys.append(xs_ys[1])

            if len(xs) > 1:
                return 1
            else:
                return 0

        def novos_pontos_p(a, pontos, n):
            p_1 = (2 * a[0] + a[1] - pontos[0]) / 2

            p_n_menos_1 = (2 * a[-2] + 7 * a[-1] - pontos[-1]) / 8

            pontos_intermediarios = np.array([])

            pontos_intermediarios = np.append(pontos_intermediarios, pontos[0])
            pontos_intermediarios = np.append(pontos_intermediarios, p_1)

            # Pontos_intermediarios.append(pontos[0])
            # Pontos_intermediarios.append(P_1)

            for i in range(1, n - 2):
                p_i_mais_1 = (
                    a[i - 1] + 4 * a[i] + a[i + 1]
                ) / 2 - 2 * pontos_intermediarios[i]

                pontos_intermediarios = np.append(pontos_intermediarios, p_i_mais_1)
                # pontos_intermediarios.append(p_i_mais_1)

            pontos_intermediarios = np.append(pontos_intermediarios, p_n_menos_1)
            pontos_intermediarios = np.append(pontos_intermediarios, pontos[-1])
            # Pontos_intermediarios.append(P_n_menos_1)
            # Pontos_intermediarios.append(pontos[-1])

            return pontos_intermediarios

        def B_a_partir_da_mudanca_de_A(a, pontos, n):
            b = np.array([])

            for i in range(0, n - 1):
                b_add = 2 * pontos[i + 1] - a[i + 1]

                b = np.append(b, b_add)

            b = np.append(b, (a[n - 1] + pontos[n]) / 2)

            return b

        def curva(p_i, p_i_mais_1, a, b):
            return (
                lambda t: (1 - t) ** 3 * p_i
                + 3 * t * (1 - t) ** 2 * a
                + 3 * t**2 * (1 - t) * b
                + t**3 * p_i_mais_1
            )

        n = len(pontos[0]) - 1

        for j in range(2):
            new_points = novos_pontos_p(a[j], pontos[j], n)

            b = B_a_partir_da_mudanca_de_A(a[j], new_points, n)

            curvas = [
                curva(new_points[i], new_points[i + 1], a[j, i], b[i])
                for i in range(0, n)
            ]

            curva_de_bezier = [
                h(t) for h in curvas for t in np.linspace(0, 1, num=tamanho)
            ]
            if j == 0:
                linhas_1 = curva_de_bezier
                B_out_1 = b
                novos_pontos_1 = new_points
            else:
                linhas_2 = curva_de_bezier
                B_out_2 = b
                novos_pontos_2 = new_points

            curvas = np.array([])
            curva_de_bezier = np.array([])
            new_points = np.array([])

        linhas = np.array((linhas_1, linhas_2))
        B_out = np.array((B_out_1, B_out_2))
        novos_pontos = np.array((novos_pontos_1, novos_pontos_2))

        array_final_um = np.array([])
        array_final_dois = np.array([])

        for i in range(len(linhas[0])):
            if linhas[0, i] not in array_final_um:
                array_final_um = np.append(array_final_um, linhas[0, i])
                array_final_dois = np.append(array_final_dois, linhas[1, i])

        array_final_um = np.append(array_final_um, 1)
        array_final_dois = np.append(array_final_dois, 0)

        linhas = np.array((array_final_um, array_final_dois))

        self.linhas = linhas.copy()
        self.A_out = a.copy()
        self.B_out = B_out.copy()

        if interseccao(linhas) == 1:
            return np.array([[0], [0]]), 0, 0, 0
        else:
            linhas = escala(linhas)
            return linhas, a, B_out, novos_pontos

    def escala(novas_curvas):
        """
        Consegue escalonar um aerofólio entre uma escala de 0 a 1 em x

        input:
            novas_curvas: todos pontos da curva, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y

        output:
            new_scale: pontos para o aerofólio normalizado, numpy array
                - Linha 0: pontos x
                - Linha 1: pontos y
        """
        theta_1 = np.min(novas_curvas[0])
        theta_2 = np.max(novas_curvas[0])

        x = np.array([])
        y = np.array([])

        for i in novas_curvas[0]:
            x_novo = -1 / (theta_1 - theta_2) * (i - theta_2) + 1

            # if x_novo < 1e-05:
            #     x_novo = 0

            x = np.append(x, x_novo)

        for i in range(len(x)):
            if x[i] == np.min(x):
                x[i] = 0

        for i in novas_curvas[1]:
            y_novo = i / (theta_2 - theta_1)

            y = np.append(y, y_novo)

        new_scale = [x, y]

        return np.array(new_scale)
