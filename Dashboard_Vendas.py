###############################################################
# +=========================================================+ #
# |     Python Web Interface Using Streamlit Library        | #
# +=========================================================+ #
# | Author   : JOSE TEOTONIO DA SILVA NETO [TEO]            | #
# | Objective: Build a example of streamlit web app         | #
# | Version  : 1.0.0.0                                      | #
# +=========================================================+ #
# | Name   | Changed At | Description                       | #
# +=========================================================+ #
# | Teo    | 10/09/2023 | Build Starter Version             | #
# +=========================================================+ #
# | Libraries Necessaries To be Installed                   | #
# +=========================================================+ #
# | pip install streamlit                                   | #
# | pip install requests                                    | #
# | pip install pandas                                      | #
# | pip install plotly                                      | #
# +=========================================================+ #
# | Libraries Extras To Solve Encoding Issues               | #
# +=========================================================+ #
# | pip install chardet                                     | #
# | conda install -c conda-forge charset-normalizer         | #
# +=========================================================+ #
###############################################################

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

###############################################################
# +=========================================================+ #
# | Setup os Page Layout to Wide                            | #
# +=========================================================+ #
###############################################################
st.set_page_config(layout='wide')

###############################################################
# +=========================================================+ #
# | Function to format Values                               | #
# +=========================================================+ #
###############################################################


def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


st.title(':shopping_trolley: DASHBOARD DE VENDAS')
url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'], format='%d/%m/%Y')

###############################################################
# +=========================================================+ #
# | Rename Some Columns For a Short Name                    | #
# +=========================================================+ #
###############################################################
dados.rename(columns={
    'Categoria do Produto': 'Categoria',
    'Local da compra': 'Estado',
    'Avaliação da compra': 'Avaliação',
    'Quantidade de parcelas': 'Parcelas',
}, inplace=True)

###############################################################
# +=========================================================+ #
# | Tables Data Content                                     | #
# +=========================================================+ #
###############################################################
receita_por_estado = dados.groupby('Estado')[['Preço']].sum()
receita_por_estado = dados.drop_duplicates(subset='Estado')[['Estado',
                                                             'lat',
                                                             'lon']].merge(receita_por_estado,
                                                                           left_on='Estado',
                                                                           right_index=True).sort_values('Preço',
                                                                                                         ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(
    pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby(
    'Categoria')[['Preço']].sum().sort_values('Preço', ascending=False)

###############################################################
# +=========================================================+ #
# | Charts Using Geo Location and Line Model                | #
# +=========================================================+ #
###############################################################
mapa_local_receita = px.scatter_geo(receita_por_estado,
                                    lat='lat',
                                    lon='lon',
                                    scope='south america',
                                    size='Preço',
                                    template='seaborn',
                                    hover_name='Estado',
                                    hover_data={'lat': False, 'lon': False},
                                    title='Receita Por Estado')

mapa_local_receita_mensal = px.line(receita_mensal,
                                    x='Mes',
                                    y='Preço',
                                    markers=True,
                                    range_y=(0, receita_mensal.max()),
                                    color='Ano',
                                    line_dash='Ano',
                                    title='Receita Mensal')

mapa_local_receita.update_layout(yaxis_title='Receita')

graph_estados = px.bar(receita_por_estado.head(),
                       x='Estado',
                       y='Preço',
                       text_auto=True,
                       title='Estados Com Maior Receita')

graph_estados.update_layout(yaxis_title='Receita')

graph_categorias = px.bar(receita_categorias,
                          text_auto=True,
                          title='Receita Por Categoria')

graph_categorias.update_layout(yaxis_title='Receita')

###############################################################
# +=========================================================+ #
# | View in Header Amount of Quantity, Revenue and Charts   | #
# | Parameter st.columns([1,2] where the number represent   | #
# | of size of ocupate in teh screen                        | #
# +=========================================================+ #
###############################################################
# Visualizacao no Streamlit os parametros [1,2] indica que a 2a é 2 vezes maior que o 1o
colunaReceita, colunaQuantidade = st.columns([1, 2])
with colunaReceita:
    st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(mapa_local_receita, use_container_width=True)
    st.plotly_chart(graph_estados, use_container_width=True)
with colunaQuantidade:
    st.metric('Quantidade de Venda', formata_numero(dados.shape[0]))
    st.plotly_chart(mapa_local_receita_mensal, use_container_width=True)
    st.plotly_chart(graph_categorias, use_container_width=True)

st.dataframe(dados)
