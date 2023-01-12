import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

class avanco:
    def __init__(self, qde_iteracoes, qde_particulas):
        self.x = np.array([])
        self.v = np.array([])
        self.objetivo = np.array([])
        self.p_best = np.array([])
        self.g_best = np.array([])
        self.c1 = 0
        self.c2 = 0
        self.w = 0
        self.r = 0
        self.N = qde_iteracoes
        self.t = 0

        self.x_append = []
        self.y_append = []
        self.iteracao_append = []
        self.fo_append = []

        self.convergencia = []
        self.qde_particulas = qde_particulas
    

    def start(self):
        def f(x,y):
            "Função a ser minimizada"
            fo = -1*((x-3.14)**2 + (y-2.72)**2 + np.sin(3*x+1.41) + np.sin(4*y-1.73))
            self.fo_append.append(fo)

            return fo

        n_particles = self.qde_particulas
        self.x = np.random.uniform(low=-4.5, high=4.5, size=(2,n_particles))
        self.v = np.random.rand(2, n_particles) * 0

        self.x_append.append(self.x[0])
        self.y_append.append(self.x[1])
        self.iteracao_append.append(0)
        
        self.objetivo = f(self.x[0],self.x[1])

        self.p_best = self.x.copy()
        self.p_best_obj = self.objetivo.copy()
        self.atualizar_g_best(
            fo=self.objetivo,
            x=self.x
        )

        self.c1 = 2.05
        self.c2 = 2.05
        self.w = 0.72984
        
        self.r = np.random.rand(2)

    
    def atualizar_g_best(
        self, fo, x
    ):
        fo_maximo = fo.max()

        for particula in range(self.qde_particulas):
            fo_particula = fo[particula]

            if fo_particula == fo_maximo:
                g_best = x[:,particula]
                g_best_obj = fo_particula

                self.convergencia.append(fo_particula)

        self.g_best = g_best.copy()
        self.g_best_obj = g_best_obj.copy()

    def atualizar_p_best_e_g_best(
        self,
        fo: np.ndarray,
        p_best: np.ndarray,
        g_best: np.ndarray,
        p_best_obj: np.ndarray,
        g_best_obj: np.ndarray,
        x: np.ndarray
    ):
        for particula in range(self.qde_particulas):
            p_best_obj_part = p_best_obj[particula]
            fo_particula = fo[particula]

            if (
                (fo_particula > p_best_obj_part)
            ):
                p_best[:,particula] = x[:,particula]
                p_best_obj[particula] = fo_particula
        
        p_best_obj_max = p_best_obj.max()
        self.convergencia.append(p_best_obj_max)
        
        for particula in range(self.qde_particulas):
            p_best_obj_part = p_best_obj[particula]            
            if (
                p_best_obj_part == p_best_obj_max # TODO: rever
            ):
                g_best = x[:,particula]
                g_best_obj = p_best_obj_part

        self.p_best = p_best.copy()
        self.g_best = g_best.copy()

        self.p_best_obj = p_best_obj.copy()
        self.g_best_obj = g_best_obj.copy()        

    def atualizar_v_e_x(
        self,
        v: np.ndarray,
        x: np.ndarray,
        p_best: np.ndarray,
        g_best: np.ndarray
    ):
        for particula in range(self.qde_particulas):
            p_best_part = p_best[:,particula]
            
            if (x[:,particula] == g_best).all():
                v[:,particula] = self.c1*self.r[0]*(p_best_part - x[:,particula]) + self.c2*self.r[1]*(g_best - x[:,particula])                
            else:
                v[:,particula] = self.w * v[:,particula] + self.c1*self.r[0]*(p_best_part - x[:,particula]) + self.c2*self.r[1]*(g_best - x[:,particula])
            
            x[:,particula] = x[:,particula] + v[:,particula]

        self.v = v.copy()
        self.x = x.copy()


    def next(self):        
        def f(x,y):
            "Função a ser minimizada"
            fo = -1*((x-3.14)**2 + (y-2.72)**2 + np.sin(3*x+1.41) + np.sin(4*y-1.73))
            self.fo_append.append(fo)
            return fo

        self.atualizar_v_e_x(
            v=self.v,
            x=self.x,
            p_best=self.p_best,
            g_best=self.g_best
        )

        self.objetivo = f(self.x[0],self.x[1])

        self.atualizar_p_best_e_g_best(
            fo=self.objetivo,
            p_best=self.p_best,
            g_best=self.g_best,
            p_best_obj=self.p_best_obj,
            g_best_obj=self.g_best_obj,
            x=self.x
        )

        self.t += 1
        self.w = 0.4*(self.t - self.N)/self.N**2 + 0.4
        self.c1 = -3*self.t/self.N + 3.5
        self.c2 = 3*self.t/self.N + 0.5

        self.x_append.append(self.x[0])
        self.y_append.append(self.x[1])
        self.iteracao_append.append(self.t)

if __name__ == "__main__":
    qde_iteracoes = 20
    teste = avanco(qde_iteracoes=qde_iteracoes, qde_particulas=50)
    teste.start()

    for _ in range(qde_iteracoes):
        teste.next()


    df_final = pd.DataFrame(columns=["X","Y","iteracao"])
    for iteracao in range(len(teste.x_append)):
        dados = {
            "X": teste.x_append[iteracao],
            "Y": teste.y_append[iteracao],
            "fo": teste.fo_append[iteracao],
            "Iteracao": [iteracao for _ in range(len(teste.x_append[iteracao]))]
        }
        df_parcial = pd.DataFrame(dados)
        df_final = pd.concat([df_final,df_parcial], ignore_index=True)

    fig = px.scatter(
        data_frame=df_final,
        x="X",
        y="Y",
        color="Iteracao",
        color_continuous_scale=px.colors.diverging.Spectral
    )
    fig.write_image(
        f"resultado-validacao-pso.jpeg"
    )

    plt.plot(teste.iteracao_append,teste.convergencia,'--o')
    plt.xlabel("Iteração")
    plt.ylabel("Função Objetivo")
    plt.grid()
    plt.savefig("fo-por-iteracao.jpeg")