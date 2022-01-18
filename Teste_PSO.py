#%%
import numpy as np
import matplotlib.pyplot as plt

class avanco:
    def __init__(self, qde_iteracoes):
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
    

    def start(self):
        def f(x,y):
            "Função a ser minimizada"
            return (x-3.14)**2 + (y-2.72)**2 + np.sin(3*x+1.41) + np.sin(4*y-1.73)

        n_particles = 20
        self.x = np.random.rand(2, n_particles) * 5
        self.v = np.random.randn(2, n_particles) * 0.1
        
        self.objetivo = f(self.x[0],self.x[1])

        self.p_best = self.x
        self.g_best = self.p_best[:,self.objetivo.argmin()].reshape(-1,1)

        self.c1 = 2.05
        self.c2 = 2.05
        self.w = 0.72984
        
        self.r = np.random.rand(2)


    def next(self):        
        def f(x,y):
            "Função a ser minimizada"
            return (x-3.14)**2 + (y-2.72)**2 + np.sin(3*x+1.41) + np.sin(4*y-1.73)

        plt.plot(self.x[0], self.x[1], 'o')
        plt.plot(self.g_best[0], self.g_best[1], 'x')
        plt.xlim((0,10))
        plt.ylim((0,10))
        plt.grid()
        plt.show()

        self.v = self.w * self.v + self.c1*self.r[0]*(self.p_best - self.x) + self.c2*self.r[1]*(self.g_best - self.x)
        self.x = self.x + self.v

        objetivo_2 = f(self.x[0],self.x[1])

        self.p_best[:, (objetivo_2 <= self.objetivo)] = self.x[:, (objetivo_2 <= self.objetivo)]

        argumento_min = np.array([self.objetivo, objetivo_2]).min(axis=0).argmin()
        self.g_best = self.p_best[:,argumento_min].reshape(-1,1)

        self.objetivo = objetivo_2

        self.t += 1
        self.w = 0.4*(self.t - self.N)/self.N**2 + 0.4
        self.c1 = -3*self.t/self.N + 3.5
        self.c2 = 3*self.t/self.N + 0.5

teste = avanco(qde_iteracoes=100)
teste.start()

for _ in range(100):
    teste.next()