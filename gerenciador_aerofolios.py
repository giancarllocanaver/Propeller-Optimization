import os
import numpy as np
import shutil
import subprocess
import time

class GerenciaAerofolios:
    def __init__(self, aerofolio):
        self.existencia = False

        if aerofolio is not None:
            self.nome_aerof_arq = aerofolio
            self.checar_existencia_aerofolios()
        else:
            self.gerar_nome_aerofolio()
            self.checar_existencia_aerofolios()
            self.gerar_aerofolio()
    
    def gerar_nome_aerofolio(self):
        serie = 4

        if serie == 4:
            primeiros_2_digitos = np.random.randint(14,65)
            ultimos_2_digitos   = np.random.randint(5,21)

            if ultimos_2_digitos < 10:
                ultimos_2_digitos = "0" + str(ultimos_2_digitos)

            self.nome_aerof     = f"naca {primeiros_2_digitos}{ultimos_2_digitos}"
            self.nome_aerof_arq = f"naca_{primeiros_2_digitos}{ultimos_2_digitos}.txt"

        if serie == 5:
            primeiros_2_digitos = np.random.randint(14,65)
            terceiro_digito     = np.random.randint(0,2)
            ultimos_2_digitos   = np.random.randint(5,21)

            self.nome_aerof     = f"naca {primeiros_2_digitos}{terceiro_digito}{ultimos_2_digitos}"
            self.nome_aerof_arq = f"naca_{primeiros_2_digitos}{terceiro_digito}{ultimos_2_digitos}.txt"

    def checar_existencia_aerofolios(self):
        if not os.path.isdir(f"base_aerofolios"):
            os.mkdir(f"base_aerofolios")

        if os.path.isfile(f"base_aerofolios/{self.nome_aerof_arq}"):
            self.existencia = True

    def gerar_aerofolio(self):
        if not self.existencia:
            with open("arquivo_input_geracao_aerofolio.txt", "w") as writer:
                writer.write("PLOP\n")
                writer.write("G\n")
                writer.write(f"\n")
                writer.write(f"{self.nome_aerof}\n")
                writer.write(f"\n")
                writer.write(f"PPAR\n")
                writer.write(f"n\n")
                writer.write(f"5\n")
                writer.write(f"\n")
                writer.write(f"\n")
                writer.write(f"save\n")
                writer.write(f"{self.nome_aerof_arq}\n")
                writer.write(f"\n")
                writer.write(f"quit\n\n")

            subprocess.Popen(
                "xfoil.exe < " + "arquivo_input_geracao_aerofolio.txt", shell=True
            )

            time.sleep(0.5)
            print(f"{self.nome_aerof_arq}")
            shutil.move(self.nome_aerof_arq, f"base_aerofolios/{self.nome_aerof_arq}")
            os.remove("arquivo_input_geracao_aerofolio.txt")

    def gerar_pontos_P(self):
        pontos = np.loadtxt(f"base_aerofolios/{self.nome_aerof_arq}", skiprows=1)
        pontos_p = np.array([pontos[:,0], pontos[:,1]])

        return pontos_p
