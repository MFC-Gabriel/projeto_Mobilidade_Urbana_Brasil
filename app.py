"""Ponto de entrada do dashboard (multipágina com st.navigation).

Os filtros ficam aqui, na barra lateral, e valem para todas as páginas.
"""
import streamlit as st

from utils import carregar_dados, filtros_sidebar

st.set_page_config(page_title="Mobilidade Urbana no Brasil", page_icon="🚍", layout="wide")

paginas = [
    st.Page("paginas/visao_geral.py", title="Visão geral", icon="🏠", default=True),
    st.Page("paginas/regioes_cidades.py", title="Regiões e cidades", icon="🗺️"),
    st.Page("paginas/meios_transporte.py", title="Meios de transporte", icon="🚌"),
    st.Page("paginas/congestionamento.py", title="Congestionamento e sazonalidade", icon="🚦"),
    st.Page("paginas/correlacoes.py", title="Correlações", icon="📈"),
]
pg = st.navigation(paginas)

df = filtros_sidebar(carregar_dados())
if df.empty:
    st.warning("Nenhum registro atende à combinação de filtros. Remova algum filtro na barra lateral.")
    st.stop()

st.session_state["df_filtrado"] = df
pg.run()
