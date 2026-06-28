```markdown
  Monitor de Rede Inteligente (IDS/IPS)

Material de apoio e laboratório prático da disciplina de Redes de Computadores (UFF).

O objetivo deste repositório é demonstrar, de forma visual e interativa, como construir um sistema de monitoramento de tráfego em tempo real (Sniffer) utilizando Python, e como implementar lógicas de detecção e prevenção ativa para ataques de negação de serviço (DoS/SYN Flood) e varreduras de rede (Port Scan/Nmap).

Arquivos do repositório

* `miniServidor.py`: Script principal que levanta o servidor web do painel interativo (Frontend) em uma thread paralela e o sniffer de pacotes (Backend).
* `Observadores/`: Diretório contendo as classes que analisam os pacotes (Padrão de Projeto Observer).
    * `dash.py`: Processa os dados e atualiza o painel visual no navegador.
    * `ipso.py`: Sistema de Prevenção (IPS) que monitora limites e executa bloqueios nativos no firewall (`iptables`).
    * `http.py`: Monitor de terminal que intercepta e exibe requisições de tráfego HTTP em texto claro.
* `assets/style.css`: Arquivo de estilização global para zerar as margens do navegador e manter o visual de terminal/SOC.
* `requirements.txt`: Arquivo contendo as dependências e versões exatas do projeto.
* `Ataques/`: Scripts em Python (`ataqueNmap.py` e `ataqueSFlood.py`) que automatizam o disparo de ataques controlados com duração máxima de 15 segundos, ideais para testar a detecção sem travar o host.

 Pré-requisitos

* **Sistema Operacional (Recomendado):** Linux (Ubuntu/Kali) nativo ou em Máquina Virtual (em modo *Bridge*). Necessário para a manipulação de *Raw Sockets* e para o bloqueio de firewall (`iptables`) funcionar plenamente.
* **Windows (Apenas para rodar o painel):** É obrigatória a instalação do driver **Npcap** (pode ser obtido instalando o Wireshark para Windows). *Nota: O bloqueio ativo via firewall não funcionará nativamente no Windows.*
* **Python 3** instalado na máquina.
* **Permissões:** Terminal com privilégios de Administrador / Root (Sudo).
* **Ferramentas de Rede:** `nmap` e `hping3` instaladas nas máquinas atacantes. No Ubuntu/Debian:
     ```bash
     sudo apt install nmap hping3
     ```

---

Instruções de Instalação

1. Clone este repositório para a sua máquina local:
   ```bash
   git clone [https://github.com/davitf-skr/ProjetoRedesObserver.git](https://github.com/davitf-skr/ProjetoRedesObserver.git)
   cd ProjetoRedesObserver

```

2. Crie o ambiente virtual e instale as dependências:
** No Linux:**
```bash
python3 -m venv venv
pip install -r requirements.txt

```


** No Windows (Terminal como Administrador):**

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
```



---

 Como executar os testes do Laboratório

> **Aviso Importante:** O código possui uma "Whitelist" que ignora pacotes vindos do próprio *localhost* (`127.0.0.1`) para evitar falsos positivos. Portanto, **certifique-se de alterar o IP alvo nos scripts de ataque para o IP real da máquina na rede local** (ex: `192.168.1.78`).

**Passo 1: Iniciar o Servidor/Monitor (Na máquina Alvo)**

Como o Scapy exige permissões de root, utilize o executável do Python diretamente do seu `venv`:

**Linux:**

```bash
sudo ./venv/bin/python miniServidor.py
```

**Windows:**

```powershell
.\venv\Scripts\python.exe miniServidor.py

```

*Acesse o painel no seu navegador pelo endereço: `http://127.0.0.1:8050*`

**Passo 2: Disparar os Ataques Controlados (Na máquina Atacante)**

Em vez de usar comandos soltos no terminal, você pode usar os scripts da pasta `Ataques/`, que iniciam e encerram a investida automaticamente após 15 segundos de forma segura.

Para simular um Port Scan furtivo (Nmap):

```bash
sudo python3 Ataques/ataqueNmap.py
```

Para simular Negação de Serviço Volumétrico - DoS (Hping3):

```bash
sudo python3 Ataques/ataqueSFlood.py
``` 

**Resultados esperados:**

1. O gráfico de pizza será preenchido exibindo o IP do atacante e a quantidade de portas escaneadas.
2. Os banners mudarão para vermelho acusando **Alerta de Ataque** no topo da tela.
3. No terminal do servidor, o `AnalisadorHTTP` imprimirá os logs de rede e o IPS executará um comando `iptables -A INPUT -s <IP_ATACANTE> -j DROP`, bloqueando a máquina ofensora instantaneamente.

---

### Visão geral da Arquitetura e Fluxo

No nosso modelo, o sistema atua como um ouvinte na rede utilizando o **Padrão de Projeto Observer**. A captura de pacotes foi separada da análise lógica:

1. O Sujeito (`scapy`) captura um pacote passando pela interface de rede.
2. O pacote é repassado simultaneamente para todos os observadores inscritos:
* O `AnalisadorHTTP` extrai métodos e caminhos de requisições web, exibindo-os no terminal.
* O `IPSObserver` gerencia um histórico interno. Se detectar anomalias severas (> 1000 SYNs ou > 200 Portas), executa chamadas no sistema operacional para banir o IP.
* O `DashboardObserver` atualiza seus dicionários de estado.


3. O painel web feito em `Dash` é atualizado a cada 500ms (callbacks assíncronos) lendo o estado atual das variáveis na memória, sem atrasar a captura de pacotes.

Limitações Técnicas e Trade-offs (Ambiente Acadêmico)

Por ser uma aplicação desenvolvida em Python (processando pacotes no *User-space*) e rodando sobre placas Wi-Fi comuns de notebooks, o sistema possui um gargalo natural de *buffer*. Sob um ataque de estresse extremo (SYN Flood massivo), ocorrerá o *Packet Drop* (descarte físico de pacotes pela placa de rede antes da leitura do software).

Assumimos esse trade-off na arquitetura: abrimos mão da captura integral em nível de Kernel (C/C++) para ganhar extrema modularidade, flexibilidade de código e geração de gráficos interativos em tempo real via Dash.

---

Autoria e Contribuições

Este projeto foi desenvolvido como laboratório prático para a disciplina de Redes de Computadores da Universidade Federal Fluminense (UFF).

* **Davi Tavares Fernandes**
* **Camille Vitória**
* **Israel Araujo**
* **Lucas Candido**

```

```
