import sys
from datetime import datetime
from scapy.all import sniff





class SnifferSujeito:
    
    def __init__(self):
        self._observadores = []

    def assinar(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar_assinatura(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar_todos(self, pacote):
        for obs in self._observadores:
            obs.atualizar(pacote)

    def iniciar(self, ):
        print("Monitorando tráfego TCP... (Ctrl+C para parar)")
        
        try:
            sniff(iface=["wlo1","lo"], prn=self.notificar_todos, store=0)
        except PermissionError:
            print(" ERRO: Você precisa rodar este script com 'sudo'.")
            sys.exit(1)
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            
            

# ==========================================
# EXECUÇÃO DO PROJETO
# ==========================================
if __name__ == "__main__":
    sniffer = SnifferSujeito()


    sniffer.iniciar()