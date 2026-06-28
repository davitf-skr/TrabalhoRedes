import subprocess
import time

def disparar_nmap_controlado(segundos=15):
    comando = ["sudo", "nmap", "-sS", "-T4", "-p-", "198.168.1.78"] #Ip da maquina alvo
    
    print(f"🚀 Iniciando varredura Nmap por {segundos} segundos...")
    
    # 1. Iniciamos o processo em segundo plano
    processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 2. Esperamos o tempo passar
    time.sleep(segundos)
    
    # 3. Encerramos o processo
    print("🛑 Tempo esgotado! Parando o Nmap...")
    processo.terminate() # Envia o sinal SIGTERM
    
    # Garante que o processo realmente morreu
    processo.wait() 
    print("✅ Varredura interrompida/finalizada com sucesso.")

if __name__ == "__main__":
    disparar_nmap_controlado()