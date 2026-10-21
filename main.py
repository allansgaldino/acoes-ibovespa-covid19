import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

st.set_page_config(layout='wide')

@st.cache_data
def carregar_dados(empresas):
    texto_tickers = ' '.join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(start='2019-01-01', end='2023-12-31')
    precos_acao = cotacoes_acao['Close']
    precos_acao = precos_acao.fillna(0)
    return precos_acao

# Importar todas ações:

@st.cache_data
def carregar_base_acoes():
    base_acoes = pd.read_csv('IBOV.csv', sep=';')
    tickers = list(base_acoes['Código'])
    tickers = [ticker + '.SA' for ticker in tickers]

    indisponiveis = {
        'JBSS3.SA', 'RRRP3.SA', 'MRFG3.SA', 'TRPL4.SA',
        'ELET6.SA', 'CIEL3.SA', 'EMBR3.SA', 'CRFB3.SA',
        'NTCO3.SA', 'CPLE6.SA', 'ELET3.SA', 'ARZZ3.SA',
        'AZUL4.SA', 'PETZ3.SA', 'BRFS3.SA', 'CCRO3.SA',
        'SOMA3.SA'
    }

    tickers = [ticker for ticker in tickers if ticker not in indisponiveis]
    return tickers

acoes = carregar_base_acoes()
dados = carregar_dados(acoes)

st.write('''
# Histórico de Cotações das Ações do IBOVESPA

Análise a partir de 2019 apresentando o efeito do período da pandemia de COVID-19 (Fonte: Yahoo Finance)
''')

st.sidebar.header('Filtros')

lista_acoes = st.sidebar.multiselect('Selecione as ações desejadas:', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica:'Close'})

data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider('Arraste para selecionar o período desejado:',
                                   min_value= data_inicial,
                                   max_value=data_final,
                                   value=(data_inicial, data_final),
                                   step=timedelta(days=1))

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

st.line_chart(dados)

texto_performance_ativos = ''

# Correções para 0 ou 1 ações selecionadas
if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes)==1:
    dados = dados.rename(columns={'Close': acao_unica})

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

# Calculo da performance do ativo
for i, acao in enumerate(lista_acoes):
    if dados[acao].iloc[i] != 0:
        performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
        performance_ativo = float(performance_ativo)
    else:
        performance_ativo = 0

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: :green[{performance_ativo:.1%}]'
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: :red[{performance_ativo:.1%}]'
    else:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: {performance_ativo:.0%}'

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f'Performance Total da Carteira: :green[{performance_carteira:.1%}]'
elif performance_carteira < 0:
    texto_performance_carteira = f'Performance Total da Carteira: :red[{performance_carteira:.1%}]'
else:
    texto_performance_carteira = f'Performance Total da Carteira: {performance_carteira:.1%}'

st.write(f'''
### Performance:

{texto_performance_ativos}

{texto_performance_carteira}

''')

st.sidebar.write('Desenvolvido por Allan Galdino')
