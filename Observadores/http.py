from scapy.all import *
from scapy.layers.http import HTTPRequest, HTTPResponse
from interfaces.observador import ObservadorRede



class AnalisadorHTTP(ObservadorRede):
    def atualizar(self, pkt):
        try:
            if pkt.haslayer(HTTPRequest):
                metodo = pkt[HTTPRequest].Method
                host = pkt[HTTPRequest].Host
                caminho = pkt[HTTPRequest].Path
                dadosCompleto = pkt[HTTPRequest].show()
                
                m = metodo.decode(errors='ignore') if metodo else "Desconhecido"
                h = host.decode(errors='ignore') if host else "Desconhecido"
                c = caminho.decode(errors='ignore') if caminho else "Desconhecido"
              
                
                print(f"🌐 [HTTP REQ] {m} em {h}{c} {dadosCompleto}")
                
            elif pkt.haslayer(HTTPResponse):
                status = pkt[HTTPResponse].Status_Code
                s = status.decode(errors='ignore') if status else "???"
                print(f"✅ [HTTP RES] Status: {s}")
        
        except Exception as e:
            print(f"⚠️ Erro ao processar HTTP: {e}")