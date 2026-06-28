import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from collections import deque
from scapy.all import TCP, IP
import time


dados_trafego = deque(maxlen=250000)
ip_acumulado = {}


LIMITE_ALERTA = 2500 

class DashboardObserver:
    def __init__(self, lista_bloqueados_referencia=None):
        self.acumulado_segundo = 0
        self.ultimo_segundo = time.strftime("%H:%M:%S")
        self.ultimo_segundo_pizza = time.time()
        self.ips_bloqueados = lista_bloqueados_referencia if lista_bloqueados_referencia is not None else set()

    def atualizar(self, pacote):
        
        tempo_atual = time.strftime("%H:%M:%S")
        tempo_numero = time.time()
        
        if tempo_atual != self.ultimo_segundo:
            info = {
                "tempo": self.ultimo_segundo,
                "tamanho": self.acumulado_segundo
            }
            dados_trafego.append(info)
            
            
            self.ultimo_segundo = tempo_atual
            self.acumulado_segundo = 0
        
        if pacote.haslayer(IP):
            origem = pacote[IP].src
            if origem in self.ips_bloqueados:
                return
        
        self.acumulado_segundo += 1
        
        if pacote.haslayer(IP) and pacote.haslayer(TCP) and pacote[TCP].flags == "S":
            origem = pacote[IP].src
            
            if origem == "127.0.0.1":
                return
            
            if origem not in ip_acumulado:
                ip_acumulado[origem] = set()
                
            porta = pacote[TCP].dport
            ip_acumulado[origem].add(porta)
           
            
        if  tempo_numero  - self.ultimo_segundo_pizza >= 200:
            ip_acumulado.clear()
            self.ultimo_segundo_pizza = tempo_numero
            
        
        


app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.H1("MONITOR DE REDE - LAB REDES UFF", 
            style={'textAlign': 'center', 'color': '#00FF41', 'paddingTop': '20px', 'fontFamily': 'monospace'}),
    
    html.Button(
        "MOSTRAR ATAQUES", 
        id="btn-mostrar",
        style={
            'backgroundColor': '#0a0a0a',     
            'color': '#00FF41',              
            'border': '2px solid #00FF41',   
            'padding': '8px 10px',           
            'fontSize': '12px',               
            'fontWeight': 'bold',            
            'fontFamily': 'monospace',        
            'cursor': 'pointer',              
            'borderRadius': '5px',            
            'boxShadow': '0px 0px 12px rgba(0, 255, 65, 0.4)',
            'marginLeft': '45%',    
            'display': 'block',               
            'transition': '0.3s'              
        }
    ),
    html.Div(id="lista-ataques", style={'textAlign': 'center', 'color': '#00FF41', 'paddingTop': '20px', 'fontFamily': 'monospace'}),
    html.Div([
        
        html.Div(id='status-banner-line', style={
        'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px', 
        'fontSize': '20px', 'fontWeight': 'bold', 'borderRadius': '10px', 
        'width': '10%', 'margin': 'auto', 'color': 'white'
        }),
        
    
        html.Div(id='status-banner-pie', style={
            'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px', 
            'fontSize': '20px', 'fontWeight': 'bold', 'borderRadius': '10px', 
            'width': '10%', 'margin': 'auto', 'color': 'white'
            }),
    
    ], style={'display':'flex', 'justifyContent': 'space-between'}),

    html.Div([
        
        dcc.Graph(id='live-graph', animate=False, style={'width': '50%'} ),
    
        dcc.Graph(id='ip-graph', animate=False, style={'width': '50%'} ),
        
        ], style={'display':'flex'}),
    
    
    dcc.Store(id='store-ataques', data={
            "key": 0,
            "atual": {},
            "historico": []
        }),

   
    dcc.Interval(id='graph-update', interval=500)

], style={'backgroundColor': '#0a0a0a', 'minHeight': '100vh', })



@app.callback(
    Output('live-graph', 'figure'),
    Output('status-banner-line', 'children'),
    Output('status-banner-line', 'style'),
    Output('status-banner-pie', 'children'),
    Output('status-banner-pie', 'style'),
    Output('store-ataques', 'data'),
    Input('graph-update', 'n_intervals'),
    State('store-ataques', 'data')
)
def update_dashboard(n, memoria):
    if not dados_trafego:
        fig_vazia = go.Figure().update_layout(
            paper_bgcolor='#0a0a0a', 
            plot_bgcolor='#0a0a0a',
            xaxis=dict(visible=False),
            yaxis=dict(range=[0, 2500], visible=True, color='white')
        )
        return (
            fig_vazia, 
            "Aguardando Tráfego DOS...", {'color': 'white', 'textAlign': 'center'}, 
            "Aguardando Tráfego Nmap...", {'color': 'white', 'textAlign': 'center'}, 
            memoria
        )
    dados_recentes = list(dados_trafego)[-100:]
    
    X = [item['tempo'] for item in dados_recentes]
    Y = [item['tamanho'] for item in dados_recentes]

    key = memoria["key"]
    atual = memoria["atual"]
    historico = memoria["historico"]
    
    if len(dados_trafego) >= 3:
        media_recente = sum(Y[-3:])/3
        sob_ataque_line = media_recente > LIMITE_ALERTA
    else:
        if len(Y) > 0:
            sob_ataque_line = Y[-1] > LIMITE_ALERTA
        else:
            sob_ataque_line = False
            
    if sob_ataque_line and key == 0:
        atual = {
            "Inicio": dados_trafego[-1]["tempo"]
        }
        key = 1

    elif not sob_ataque_line and key == 1:
        atual["Fim"] = dados_trafego[-1]["tempo"]
        historico.append(atual)
        atual = {}
        key = 0
    
          
    cor_alerta_line = '#FF0000' if sob_ataque_line else "#2F00FF"
    status_texto_line = "🚨 ATAQUE DOS DETECTADO 🚨" if sob_ataque_line else "✅ SISTEMA OPERACIONAL - ESTÁVEL"
    border_status_line = "#410202" if sob_ataque_line else "#2F00FF"
    
    estilo_banner_line = {
        'backgroundColor': '#FF0000' if sob_ataque_line else '#1a1a1a',
        'color': 'white' if sob_ataque_line else '#00FF41',
        'border': f'5px solid {border_status_line}',
        'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px', 'fontSize': '20px',
        'fontWeight': 'bold', 'borderRadius': '10px', 'width': '40%', 'marginLeft': '10px', 
    }
    
    values = [len(item) for item in ip_acumulado.values()]
    
    sob_ataque_pie = False
    for portas in ip_acumulado.values():
        if len(portas) > 100:
            sob_ataque_pie = True
            break
    
    status_texto_pie = "🚨 ATAQUE PORT SCAN DETECTADO 🚨" if sob_ataque_pie else "✅ SISTEMA OPERACIONAL - ESTÁVEL"
    border_status_pie = "#000000" if sob_ataque_pie else "#2F00FF"

    
    estilo_banner_pie = {
        'backgroundColor': '#FF0000' if sob_ataque_pie else '#1a1a1a',
        'color': 'white' if sob_ataque_pie else '#00FF41',
        'border': f'5px solid {border_status_pie}',
        'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px', 'fontSize': '20px',
        'fontWeight': 'bold', 'borderRadius': '10px', 'width': '40%',  
    }
    
    

    data = go.Scatter(
        x=list(X),
        y=list(Y),
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color=cor_alerta_line, width=2),
        marker=dict(size=4, color=cor_alerta_line),
    )

    janela = 15
    x_range = [X[-janela], X[-1]] if len(X) > janela else [X[0], X[-1]]

    layout = go.Layout(
        xaxis=dict( range=x_range, nticks=15,color='white',type='category', showgrid=False, fixedrange=False),
        yaxis=dict(range=[0, 10000], color='white', gridcolor='#222', fixedrange=True),
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#0a0a0a',
        uirevision='constant', 
        showlegend=False,
        margin=dict(l=50, r=50, t=20, b=50),
        height=500,
        
    )

    return (
    {'data': [data], 'layout': layout},
    status_texto_line,
    estilo_banner_line,
    status_texto_pie,
    estilo_banner_pie,
        {
        "key": key,
        "atual": atual,
        "historico": historico
    })
    
    


@app.callback(
    Output('ip-graph', 'figure'),
    Input('graph-update', 'n_intervals'),
)
def update_grafico_ip(n):
    if not ip_acumulado:
        fig_vazia = go.Figure().update_layout(
            paper_bgcolor='#0a0a0a', 
            plot_bgcolor='#0a0a0a',
            showlegend=True,
            margin=dict(l=50, r=50, t=20, b=50)
        )
        return fig_vazia
    
    
    
    data = go.Pie(
        labels = list(ip_acumulado.keys()),
        values = [len(portas) for portas in ip_acumulado.values()]
        
        
    )
    
    layout = go.Layout(
        paper_bgcolor = '#0a0a0a',
        font=dict(color='#00FF41'),
        showlegend=True,
        margin=dict(l=50, r=50, t=20, b=50)
        
    )
    
    return  {'data': [data], 'layout': layout}
    


@app.callback(
    Output("lista-ataques", "children"),
    Input("btn-mostrar", "n_clicks"),
    State("store-ataques", "data"),
    prevent_initial_call=True
)
def mostrar_ataques(n, memoria):

    historico = memoria["historico"]

    if not historico:
        return "Nenhum ataque registrado."

    return [
        html.Div(
            f'Início: {item["Inicio"]} | Fim: {item["Fim"]}'
        )
        for item in historico[-10:]
    ]