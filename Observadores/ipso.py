import subprocess
from interfaces.observador import ObservadorRede
from scapy.all import TCP, IP
import time



class IPSObserver(ObservadorRede): 
    def __init__(self, limite_syn= 1000):
        self.historico_syn = {}
        self.limite_syn = limite_syn
        self.historico_porta = {}
        self.ultimo_segundo_porta = time.time()
        self.ips_bloqueados = set()
        self.ultimo_segundo = time.time()


    def bloquear_ip(self, ip):
        
        if ip == "127.0.0.1": 
            return

        print(f"🛡️ [IPS] BLOQUEANDO IP {ip} NO FIREWALL...")
        comando = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        
        try:
            subprocess.run(comando, check=True)
            self.ips_bloqueados.add(ip)
            print(f"IP {ip} banido com sucesso.")
        except Exception as e:
            print(f"Falha ao bloquear IP: {e}")

    def atualizar(self, pkt):
        
        if pkt.haslayer(TCP) and pkt.haslayer(IP):
            origem = pkt[IP].src
            
            
            tempo_atual = time.time()
            
            if origem in self.ips_bloqueados:
                return
            
            #Teste para detectar flag "S" e bloquear IP em caso de ataque.
            if "S" in str(pkt[TCP].flags):
                self.historico_syn[origem] = self.historico_syn.get(origem, 0) + 1

                if self.historico_syn[origem] > self.limite_syn:
                    print(f"\n [ALERTA] LIMITE ATINGIDO PARA {origem}!")
                    self.bloquear_ip(origem)
                    self.historico_syn[origem] = 0
            
            
                
            
            if "S" in str(pkt[TCP].flags):
                if origem not in self.historico_porta:
                    self.historico_porta[origem] = set()
                
                porta = pkt[TCP].dport
                self.historico_porta[origem].add(porta)
                
                if len(self.historico_porta[origem]) > 200:
                    print(f"\n [ALERTA] PORT SCAN DETECTADO DA ORIGEM {origem}!")
                    self.bloquear_ip(origem)

                
                
            if tempo_atual - self.ultimo_segundo_porta >= 5:
                    self.historico_porta = {}
                    self.ultimo_segundo_porta = tempo_atual    
                
            
            
            if tempo_atual - self.ultimo_segundo >=30:
                self.historico_syn = {}
                self.ultimo_segundo = tempo_atual
                
            
