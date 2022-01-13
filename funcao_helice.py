#%%
import numpy as np
from scipy.interpolate import interp2d
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import funcoes_tcc.funcoes_de_bezier as bezier
import funcoes_tcc.xfoil_funcao as xfoil
import time
import os

class helice():
    def __init__(self, Aerofolios,Velocidade_da_aeronave,Viscosidade_dinamica,Temperatura,Densidade_do_ar,Diametro_helice,Numero_de_pas,Array_raio_da_secao,Array_tamanho_de_corda_da_secao,Array_angulo_beta_da_secao,Rotacao_motor):
        self.aerof = Aerofolios
        self.v = Velocidade_da_aeronave 
        self.mi = Viscosidade_dinamica 
        self.T = Temperatura 
        self.rho = Densidade_do_ar
        self.D = Diametro_helice 
        self.n = Numero_de_pas 
        self.r = Array_raio_da_secao 
        self.c = Array_tamanho_de_corda_da_secao
        self.beta = Array_angulo_beta_da_secao 
        self.rpm = Rotacao_motor 


    def rodar_helice(self):        
        def rodar_xfoil(aerofolio, re, alpha, Ma):
            if Ma < 1:
                xfoil.rodar_xfoil(aerofolio, str(alpha), str(alpha), "0", str(re), str(Ma), "9", "100", "arquivo_dados_v.txt",mudar_paineis=True,
                    mostrar_grafico=False, ler_arquivo_coord=True, compressibilidade=False, solucao_viscosa=True)
                
                # xfoil.rodar_xfoil(aerofolio, str(alpha), str(alpha), "0", str(re), str(Ma), "9", "100", "arquivo_dados_c.txt",mudar_paineis=True,
                #     mostrar_grafico=False, ler_arquivo_coord=True, compressibilidade=True, solucao_viscosa=False)

                dados_v = np.loadtxt("arquivo_dados_v.txt", skiprows=12)
                # dados_c = np.loadtxt("arquivo_dados_c.txt", skiprows=12)

                os.remove("arquivo_dados_v.txt")
                # os.remove("arquivo_dados_c.txt")

                # if dados_v.size != 0 and dados_c.size != 0:
                #     cdp = dados_c[3]
                #     cd0 = dados_v[2] - dados_v[3]

                #     cd = cdp + cd0
                #     cl = min(dados_c[1], dados_v[1])                
                
                if dados_v.size != 0: #and dados_c.size == 0:
                    cl = dados_v[1]
                    cd = dados_v[2]
                    
                    cl = cl/(np.sqrt(1 - Ma**2))
                    cd = cd/(np.sqrt(1 - Ma**2))
                
                # if dados_v.size == 0 and dados_c.size != 0:
                #     cl = dados_c[1]
                #     cd = dados_c[3]           
                
                if dados_v.size == 0: #and dados_c.size == 0:
                    cl = 0
                    cd = 0
            else:
                cl = 0
                cd = 0

            # print(dados_c.size, '\t', dados_v.size, '\t', cl, '\t',cd)

            return cl, cd

        
        def integracao(f,x):
            
            I = 0.
            
            for i in range(1,len(x)):
                I += (x[i]-x[i-1])*(f[i]+f[i-1])/2.
            
            return I


        q = 0.5*self.rho*self.v**2 # Pressão Dinâmica

        vt = 2.*np.pi/60.*self.rpm*self.r # Velocidade Tangencial

        phi = np.arctan(self.v/vt)
        phi[-1] = 0.

        vr = vt/np.cos(phi) # Velocidade Resultante

        alpha = (self.beta - phi)*180/np.pi 
        alpha[-1] = 0.
        
        dT = []
        dQ = []
        r_new = []

        for i in range(len(self.aerof) - 1):
            reynolds = self.rho*vr[i]*self.c[i]/self.mi
            Ma = vr[i]/(np.sqrt(1.4*287*self.T))
            
            if vr[i] != 0: 
                coef_l, coef_d = rodar_xfoil(self.aerof[i], round(reynolds, 0), alpha[i], Ma)

            if coef_l != 0 and coef_d !=0:
                gamma = np.arctan(coef_d/coef_l)

                dt = q*coef_l*self.c[i]*(np.cos(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                dq = q*coef_l*self.c[i]*self.r[i]*(np.sin(phi[i] + gamma))/(np.cos(gamma)*np.sin(phi[i])**2)
                
                dT.append(dt)
                dQ.append(dq)

                r_new.append(self.r[i])
            
        dT.append(0)
        dQ.append(0)

        r_new.append(self.r[-1])

        dT = np.array(dT)
        dQ = np.array(dQ)

        T = integracao(dT,r_new)*self.n
        Q = integracao(dQ,r_new)*self.n    

        eta = T*self.v/(Q*2*np.pi*self.rpm/60) # Eficiência da hélice

        vel_rot = self.rpm/60

        Ct = T/(self.rho*vel_rot**2*self.D**4)
        Cq = Q/(self.rho*vel_rot**2*self.D**5)
        Cp = 2*np.pi*Cq

        J = self.v/(vel_rot*self.D)
        Cs = J/(Cp**(1/5))

        eta_2 = J*Ct/Cp

        saida = [T,Q,dT,dQ,eta,vr,r_new,Ct,Cq,Cp,J,Cs,eta_2]

        return saida


