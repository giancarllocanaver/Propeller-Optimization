import numpy as np
import os
import subprocess
import psutil
import time

class Xfoil:
    def __init__(
        self,
        curvas_aerofolio,
        alpha_inicial,
        alpha_final,
        alpha_step,
        Reynolds,
        Mach,
        N_crit,
        iteracoes,
        nome_do_arquivo_de_output,
        mudar_paineis=False,
        mostrar_grafico = False,
        ler_arquivo_coord = False,
        compressibilidade = False,
        solucao_viscosa = False,
        solucao_com_interpolacao = False,
        solucoes_NACA = False,
    ):
        self.curvas_aerofolio          = curvas_aerofolio
        self.alpha_inicial             = alpha_inicial
        self.alpha_final               = alpha_final
        self.alpha_step                = alpha_step
        self.Reynolds                  = Reynolds
        self.Mach                      = Mach
        self.N_crit                    = N_crit
        self.iteracoes                 = iteracoes
        self.nome_do_arquivo_de_output = nome_do_arquivo_de_output
        self.mudar_paineis             = mudar_paineis
        self.mostrar_grafico           = mostrar_grafico
        self.ler_arquivo_coord         = ler_arquivo_coord
        self.compressibilidade         = compressibilidade
        self.solucao_viscosa           = solucao_viscosa
        self.solucao_com_interpolacao  = solucao_com_interpolacao
        self.solucoes_NACA             = solucoes_NACA


    def rodar_xfoil(self):
        """ "
        Com esta função, é possível de se obter os resultados do XFOIL para dado aerofólio.

        inputs:
            curvas_aerofolio: coordenadas do aerofólio, numpy array
            alpha_inicial: ângulo de ataque inicial, 'string'
            alpha_final: ângulo de ataque final, 'string'
            alpha_step: delta de ângulo de ataque, 'string'
            Reynolds: número de Reynolds inicial, 'string'
            iteracoes: número máximo de iterações por ângulo de ataque, 'string'
            nome_do_arquivo_de_output: nome do arquivo de saída, 'string'
            mudar_paineis: aumentar a quantidade de painéis, é Falso por definição
            mostrar_gráfico: mostrar gráfico de Cp enquanto estiver realizando os cálculos, é Falso por definição

        output:
            Gera arquivo de texto com os dados gerados, porém, não retorna nada.
        """
        if self.ler_arquivo_coord:
            nome_arq_coord = self.curvas_aerofolio
        
        nome_do_arquivo_de_input_do_xfoil = "arquivo_de_input.txt"

        if os.path.exists(nome_do_arquivo_de_input_do_xfoil):
            os.remove(nome_do_arquivo_de_input_do_xfoil)

        if os.path.exists(self.nome_do_arquivo_de_output):
            os.remove(self.nome_do_arquivo_de_output)

        arquivo_de_input = open(nome_do_arquivo_de_input_do_xfoil, "w")

        if self.mostrar_grafico == False:
            arquivo_de_input.write("PLOP" + "\n")
            arquivo_de_input.write("G" + "\n")
            arquivo_de_input.write("\n")

        if not self.solucoes_NACA:
            arquivo_de_input.write("LOAD" + "\n")
            arquivo_de_input.write(nome_arq_coord + "\n")
        else:
            arquivo_de_input.write(self.curvas_aerofolio + "\n")

        if self.mudar_paineis == True:
            arquivo_de_input.write("PPAR" + "\n")
            arquivo_de_input.write("N" + "\n")
            arquivo_de_input.write("200" + "\n")
            arquivo_de_input.write("\n")
            arquivo_de_input.write("\n")

        arquivo_de_input.write("oper" + "\n")

        if self.solucao_viscosa == True:
            arquivo_de_input.write("visc " + self.Reynolds + "\n")

        if self.compressibilidade == True and self.solucao_viscosa == False:
            arquivo_de_input.write("mach" + self.Mach + "\n")

        if self.solucao_viscosa == True:
            arquivo_de_input.write("vpar" + "\n")
            arquivo_de_input.write("N" + "\n")
            arquivo_de_input.write(self.N_crit + "\n")
            arquivo_de_input.write("\n")

        arquivo_de_input.write("iter " + self.iteracoes + "\n")
        arquivo_de_input.write("pacc" + "\n")
        arquivo_de_input.write(self.nome_do_arquivo_de_output + "\n")
        arquivo_de_input.write("\n")
        arquivo_de_input.write(
            "aseq " + self.alpha_inicial + " " + self.alpha_final + " " + self.alpha_step + "\n"
        )
        arquivo_de_input.write("\n")
        arquivo_de_input.write("quit")
        arquivo_de_input.write("\n")
        arquivo_de_input.write("quit")
        arquivo_de_input.close()

        def kill(proc_pid):
            try:
                process = psutil.Process(proc_pid)
                for proc in process.children(recursive=True):
                    proc.kill()
            
                process.kill()
            except psutil.NoSuchProcess:
                return

        try:
            p = subprocess.Popen(
                "xfoil.exe < " + nome_do_arquivo_de_input_do_xfoil, shell=True
            )

            if not self.solucao_com_interpolacao:
                p.wait(timeout=1)
            else:
                p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            kill(p.pid)
            time.sleep(1)

        try:
            os.remove(nome_do_arquivo_de_input_do_xfoil)
        except PermissionError:
            pass
