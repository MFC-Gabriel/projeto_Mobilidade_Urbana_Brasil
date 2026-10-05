"""Funções compartilhadas entre as páginas do dashboard.

Carregamento e tratamento da base, filtros da barra lateral, KPIs e helpers
de visualização. Mantido fora do app.py para que todas as páginas usem
exatamente os mesmos dados filtrados.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

CSV_PATH = Path(__file__).parent / "dados" / "simulacao_mobilidade_urbana_brasil.csv"

ORDEM_NIVEL = ["Baixo", "Médio", "Alto", "Crítico"]
NIVEL_NUM = {n: i + 1 for i, n in enumerate(ORDEM_NIVEL)}
CORES_NIVEL = {"Baixo": "#2E9E6B", "Médio": "#E3B341", "Alto": "#E8782A", "Crítico": "#C0392B"}
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

ROTULOS = {
    "passageiros": "Passageiros",
    "tempo_medio_deslocamento": "Tempo médio de deslocamento (min)",
    "lotacao_media": "Lotação média (%)",
    "velocidade_media": "Velocidade média (km/h)",
    "emissao_co2": "Emissão de CO₂ (estimada)",
    "tarifa_media": "Tarifa média (R$)",
    "nivel_num": "Nível de congestionamento (1 a 4)",
    "indice_pressao": "Índice de pressão (0 a 1)",
}
CURTOS = {
    "passageiros": "Passageiros", "tempo_medio_deslocamento": "Tempo desloc.",
    "lotacao_media": "Lotação", "velocidade_media": "Velocidade",
    "emissao_co2": "Emissão CO₂", "tarifa_media": "Tarifa", "nivel_num": "Congestionamento",
}

sns.set_theme(style="whitegrid", context="notebook")


# --------------------------------------------------------------------------- #
# Dados
# --------------------------------------------------------------------------- #
def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza, validação e engenharia de atributos."""
    df = df.copy()
    for c in ["regiao", "uf", "cidade", "meio_transporte", "nivel_congestionamento"]:
        df[c] = df[c].astype(str).str.strip()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.drop_duplicates().dropna()

    # coerência entre ano/mes e a coluna data; valores impossíveis
    df = df[(df["data"].dt.year == df["ano"]) & (df["data"].dt.month == df["mes"])]
    df = df[(df["passageiros"] > 0) & (df["tempo_medio_deslocamento"] > 0)]

    df["nivel_num"] = df["nivel_congestionamento"].map(NIVEL_NUM)
    df = df.dropna(subset=["nivel_num"])
    df["nivel_num"] = df["nivel_num"].astype(int)
    df["nivel_congestionamento"] = pd.Categorical(
        df["nivel_congestionamento"], categories=ORDEM_NIVEL, ordered=True)

    # engenharia de atributos
    df["mes_nome"] = df["mes"].map(MESES)
    df["trimestre"] = df["data"].dt.quarter
    df["superlotacao"] = df["lotacao_media"] > 100
    df["indice_pressao"] = (df["lotacao_media"].clip(upper=120) / 120 + df["nivel_num"] / 4) / 2
    df["co2_por_mil_pass"] = df["emissao_co2"] / (df["passageiros"] / 1000)
    return df.reset_index(drop=True)


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    return tratar_dados(pd.read_csv(CSV_PATH))


def obter_df() -> pd.DataFrame:
    """DataFrame já filtrado pela barra lateral (definido no app.py)."""
    if "df_filtrado" not in st.session_state:
        st.session_state["df_filtrado"] = carregar_dados()
    return st.session_state["df_filtrado"]


def filtros_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Sete filtros múltiplos, com UF e cidade dependentes da seleção anterior."""
    st.sidebar.header("Filtros")
    st.sidebar.caption("Deixe um filtro vazio para incluir todos os valores.")

    anos = st.sidebar.multiselect("Ano", sorted(df["ano"].unique()))
    meses = st.sidebar.multiselect("Mês", list(MESES), format_func=lambda m: MESES[m])
    regioes = st.sidebar.multiselect("Região", sorted(df["regiao"].unique()))

    base = df[df["regiao"].isin(regioes)] if regioes else df
    ufs = st.sidebar.multiselect("Estado (UF)", sorted(base["uf"].unique()))
    base = base[base["uf"].isin(ufs)] if ufs else base
    cidades = st.sidebar.multiselect("Cidade", sorted(base["cidade"].unique()))

    modais = st.sidebar.multiselect("Meio de transporte", sorted(df["meio_transporte"].unique()))
    niveis = st.sidebar.multiselect("Nível de congestionamento", ORDEM_NIVEL)

    mask = pd.Series(True, index=df.index)
    for col, sel in [("ano", anos), ("mes", meses), ("regiao", regioes), ("uf", ufs),
                     ("cidade", cidades), ("meio_transporte", modais),
                     ("nivel_congestionamento", niveis)]:
        if sel:
            mask &= df[col].isin(sel)
    out = df[mask]

    st.sidebar.divider()
    st.sidebar.metric("Registros no recorte", fmt_int(len(out)),
                      delta=f"{len(out) / len(df):.0%} da base", delta_color="off")
    st.sidebar.download_button(
        "Baixar recorte (CSV)",
        out.drop(columns=["mes_nome"]).to_csv(index=False).encode("utf-8"),
        file_name="recorte_mobilidade.csv", mime="text/csv")
    return out


# --------------------------------------------------------------------------- #
# KPIs e formatação
# --------------------------------------------------------------------------- #
def fmt_int(n) -> str:
    return f"{n:,.0f}".replace(",", ".")


def fmt_dec(n, casas=1) -> str:
    return f"{n:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_mi(n) -> str:
    return fmt_dec(n / 1e6, 1) + " mi"


def rotulo_nivel(media: float) -> str:
    return ORDEM_NIVEL[int(np.clip(int(media + 0.5), 1, 4)) - 1]


def calcular_kpis(df: pd.DataFrame) -> dict:
    por_cidade = df.groupby("cidade")["passageiros"].sum()
    por_modal = df.groupby("meio_transporte")["passageiros"].sum()
    nivel = df["nivel_num"].mean()
    return {
        "total": df["passageiros"].sum(),
        "cidade": por_cidade.idxmax(), "cidade_total": por_cidade.max(),
        "modal": por_modal.idxmax(), "modal_pct": por_modal.max() / por_modal.sum(),
        "tempo": df["tempo_medio_deslocamento"].mean(),
        "tarifa": df["tarifa_media"].mean(),
        "nivel": nivel, "nivel_rotulo": rotulo_nivel(nivel),
    }


def exibir_kpis(df: pd.DataFrame) -> dict:
    k = calcular_kpis(df)
    a, b, c = st.columns(3)
    a.metric("Total de passageiros", fmt_mi(k["total"]))
    b.metric("Cidade mais movimentada", k["cidade"], f"{fmt_mi(k['cidade_total'])} passageiros", delta_color="off")
    c.metric("Meio de transporte predominante", k["modal"], f"{k['modal_pct']:.0%} dos passageiros", delta_color="off")
    d, e, f = st.columns(3)
    d.metric("Tempo médio de deslocamento", f"{fmt_dec(k['tempo'])} min")
    e.metric("Tarifa média", f"R$ {fmt_dec(k['tarifa'], 2)}")
    f.metric("Nível médio de congestionamento", k["nivel_rotulo"], f"{fmt_dec(k['nivel'], 2)} em 4", delta_color="off")
    return k


# --------------------------------------------------------------------------- #
# Apresentação
# --------------------------------------------------------------------------- #
def mostrar(fig):
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def interpretacao(texto: str):
    st.info("**Interpretação.** " + texto)


def descrever_variacao(v: float, limite: float = 0.05) -> str:
    if abs(v) < limite:
        return "praticamente estável"
    return "em alta" if v > 0 else "em queda"
