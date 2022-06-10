import numpy as npy
from matplotlib import pyplot as plt
from scipy.linalg import solve_banded


def EulerImplicito(u,dx,a,dt):

    n = len(u)
    A = npy.ones(n)
    B = npy.zeros(n)
    C = npy.zeros(n)


    # operador de primeira ordem backward
    A  = A+dt*a/dx
    C[:] = -dt*a/dx
    rhs = u*1.0
    

    # condição de contorno para primeira linha
    # u(j=0) = 0
    A[0] = 1.0
    B[0] = 0.0
    B[1] = 0.0

    # condição de contorno para última linha 
    # grad(u) = 0
    rhs[n-1] = 0.0 
    C[n-1] = 0.0
    C[n-2] = -1.0

    # monta o sistema linear
    ab = npy.array([B,A,C])

    # resolve o sistema linear e avança no tempo
    u = solve_banded((1, 1), ab, u)

   
    return u


def CondicaoInicial(x):
    
    u = x*0.0
    u = 1.0/(1.0+1.0*x**2)

    return u-u.min()



# parâmtros de setup da simulação

Lx  = 10     # Tamanho do domínio em x
nx  = 300    # Número de pontos em x
CFL = 50.0    # Número de CFL
a =   1.0    # Velocidade da onda
T = 10.0     # Período de integração

# definindo dx
dx = Lx/float(nx-1)

# número de passos no tempo até T
dt = CFL*dx/a
dt = npy.abs(dt)
step = int(T/dt)+1

# definindo a malha
x = npy.linspace(-Lx/2,Lx/2,nx) 


# aplica a condição inicial
u = CondicaoInicial(x)
u0 = u*1.0 

print(step)
# realiza a marcha no tempo
for n in range(step):
    texto = 'Passo no tempo %s t= %f ' %( n, n*dt)
    print(texto)

    u = EulerImplicito(u,dx,a,dt)
    
    # cria figura
    plt.figure(1)
    plt.clf()
    plt.plot(x,u,label='u(x,t=1)')
    plt.plot(x,u0,label='u(x,t=0)')
    plt.xlim(-4,4)
    plt.ylim(-0.5,1.5)
    plt.xlabel('x',fontsize=15)
    plt.ylabel('u',fontsize=15)
    plt.legend(loc="best", fontsize='small')
    plt.pause(0.01)
plt.show()