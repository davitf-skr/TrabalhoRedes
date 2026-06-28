```markdown
# Monitor de Rede Inteligente (IDS/IPS)

Material de apoio e laboratório prático da disciplina de Redes de Computadores.

O objetivo deste repositório é demonstrar, de forma visual e interativa, como construir um sistema de monitoramento de tráfego em tempo real (Sniffer) utilizando Python. Além disso, implementa lógicas de detecção e prevenção ativa para ataques de negação de serviço (DoS/SYN Flood) e varreduras de rede (Port Scan/Nmap).

---

## 🗂 Estrutura do Repositório

```text
.
├── miniServidor.py       # Script principal: levanta o servidor web (Frontend) e o sniffer (Backend)
├── requirements.txt      # Dependências e versões exatas do projeto
├── Observadores/         # Classes de análise de pacotes (Padrão de Projeto Observer)
│   ├── dash.py           # Processa os dados e atualiza o painel visual
│   ├── ipso.py           # IPS: Monitora limites e executa bloqueios nativos no firewall (iptables)
│   └── http.py           # Intercepta e exibe requisições de tráfego HTTP em texto claro
├── Ataques/              # Scripts de automação de ataques controlados (máx. 15 segundos)
│   ├── ataqueNmap.py
│   └── ataqueSFlood.py
└── assets/
    └── style.css         # Estilização global do painel web

```

---

## Pré-requisitos

* **Sistema Operacional (Recomendado):** Linux (Ubuntu/Kali) nativo ou em Máquina Virtual (em modo *Bridge*). Necessário para a manipulação de *Raw Sockets* e para o bloqueio de firewall (`iptables`) funcionar plenamente.
* **Windows (Apenas para rodar o painel):** É obrigatória a instalação do driver **Npcap** (obtido via instalação do Wireshark). *Nota: O bloqueio ativo via firewall não funcionará nativamente no Windows.*
* **Ambiente:** Python 3 instalado e terminal com privilégios de Administrador/Root (`sudo`).
* **Ferramentas de Rede:** `nmap` e `hping3` instaladas nas máquinas atacantes. No Ubuntu/Debian:
```bash
sudo apt install nmap hping3

```



---

## Instalação

**1. Clone o repositório**

```bash
git clone [https://github.com/davitf-skr/ProjetoRedesObserver.git](https://github.com/davitf-skr/ProjetoRedesObserver.git)
cd ProjetoRedesObserver

```

**2. Crie o ambiente virtual e instale as dependências**

*No Linux:*

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

*No Windows (Terminal como Administrador):*

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

```

---

## Como Executar o Laboratório

> **Aviso Importante:** O código possui uma *Whitelist* que ignora pacotes vindos do próprio *localhost* (`127.0.0.1`) para evitar falsos positivos. Certifique-se de alterar o IP alvo nos scripts de ataque para o IP real da máquina na rede local (ex: `192.168.1.78`).

### Passo 1: Iniciar o Servidor/Monitor (Máquina Alvo)

Como o Scapy exige permissões de root para captura de pacotes, utilize o executável do Python diretamente do seu ambiente virtual:

*Linux:*

```bash
sudo ./venv/bin/python miniServidor.py

```

*Windows:*

```powershell
.\venv\Scripts\python.exe miniServidor.py

```

Acesse o painel no navegador via: `http://127.0.0.1:8050`

### Passo 2: Disparar os Ataques Controlados (Máquina Atacante)

Utilize os scripts da pasta `Ataques/`, que iniciam e encerram a investida automaticamente após 15 segundos de forma segura, sem travar o host.

*Para simular um Port Scan furtivo (Nmap):*

```bash
sudo python3 Ataques/ataqueNmap.py

```

*Para simular Negação de Serviço Volumétrico - DoS (Hping3):*

```bash
sudo python3 Ataques/ataqueSFlood.py

```

### Resultados Esperados

1. O gráfico do painel será preenchido exibindo o IP do atacante e a quantidade de portas escaneadas.
2. Os *banners* mudarão para vermelho acusando **Alerta de Ataque** no topo da tela.
3. No terminal do servidor, o `AnalisadorHTTP` imprimirá os logs de rede e o IPS executará um comando `iptables -A INPUT -s <IP_ATACANTE> -j DROP`, bloqueando a máquina ofensora instantaneamente.

---

## Arquitetura e Fluxo

No nosso modelo, o sistema atua como um ouvinte na rede utilizando o **Padrão de Projeto Observer**. A captura de pacotes foi separada da análise lógica para garantir performance e escalabilidade:

1. **Captura:** O Sujeito (`scapy`) captura um pacote passando pela interface de rede.
2. **Distribuição:** O pacote é repassado simultaneamente para todos os observadores inscritos:
* O `AnalisadorHTTP` extrai métodos e caminhos de requisições web.
* O `IPSObserver` gerencia um histórico interno. Ao detectar anomalias severas (> 1000 SYNs ou > 200 Portas), executa chamadas no S.O. para banir o IP.
* O `DashboardObserver` atualiza seus dicionários de estado.


3. **Apresentação:** O painel web (Dash) é atualizado a cada 500ms via *callbacks* assíncronos, lendo o estado atual das variáveis na memória sem atrasar a captura de pacotes.

---

## Limitações Técnicas e Trade-offs

Por ser uma aplicação desenvolvida em Python (processando pacotes no *User-space*) e rodando sobre placas Wi-Fi comuns, o sistema possui um gargalo natural de *buffer*. Sob um ataque de estresse extremo (SYN Flood massivo), ocorrerá o *Packet Drop* (descarte físico de pacotes pela placa de rede antes da leitura do software).

Assumimos esse *trade-off* na arquitetura: abrimos mão da captura integral em nível de Kernel (C/C++) para ganhar extrema modularidade, flexibilidade de código e geração de gráficos interativos em tempo real via Dash.

---

## Autoria

Projeto desenvolvido como laboratório prático para a Universidade Federal Fluminense (UFF).

* **Davi Tavares Fernandes**
* **Camille Vitória**
* **Israel Araujo**
* **Lucas Candido**

```

```
