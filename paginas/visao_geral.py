import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import (descrever_variacao, exibir_kpis, fmt_dec, fmt_mi, interpretacao,
                   mostrar, obter_df)

df = obter_df()

st.title("Mobilidade Urbana e Transporte Público no Brasil")
st.caption(f"Recorte atual: {df['cidade'].nunique()} cidades · {df['regiao'].nunique()} regiões · "
           f"{df['meio_transporte'].nunique()} meios de transporte · "
           f"{df['data'].min():%m/%Y} a {df['data'].max():%m/%Y}")

st.subheader("Descrição do problema")
st.markdown(
    "O crescimento das cidades aumenta a demanda por transporte público e pressiona a infraestrutura: "
    "viagens mais longas, veículos lotados e vias congestionadas afetam a qualidade de vida, a produtividade "
    "e o meio ambiente. Este painel investiga **onde o fluxo de passageiros é maior, como os meios de "
    "transporte se comparam, se o tempo de deslocamento mudou entre 2015 e 2024 e quais regiões sofrem mais "
    "pressão**. Use os filtros da barra lateral: todos os números e gráficos se atualizam."
)
with st.expander("Sobre a base de dados"):
    st.markdown(
        "Base **simulada** (`simulacao_mobilidade_urbana_brasil.csv`) com uma linha por cidade e mês, "
        "de jan/2015 a dez/2024. Cada registro traz passageiros, tempo médio de deslocamento, lotação, "
        "velocidade, emissão de CO₂, tarifa, meio de transporte e nível de congestionamento. "
        "Por ser simulada, os resultados não descrevem a realidade das cidades citadas."
    )

st.subheader("Indicadores-chave")
k = exibir_kpis(df)

st.subheader("Evolução temporal")
mensal = df.groupby("data")["passageiros"].sum().sort_index() / 1e6
c1, c2 = st.columns(2)
with c1:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    sns.lineplot(x=mensal.index, y=mensal.values, ax=ax, color="#9FB4D6", lw=1, label="Mensal")
    if len(mensal) >= 12:
        sns.lineplot(x=mensal.index, y=mensal.rolling(12).mean().values, ax=ax,
                     color="#1E63D6", lw=2.5, label="Média móvel de 12 meses")
    ax.set(title="Passageiros por mês (milhões)", xlabel="", ylabel="Passageiros (mi)")
    mostrar(fig)
with c2:
    anual = df.groupby("ano")["tempo_medio_deslocamento"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7, 3.8))
    sns.lineplot(data=anual, x="ano", y="tempo_medio_deslocamento", marker="o", color="#C2185B", ax=ax)
    ax.set(title="Tempo médio de deslocamento por ano", xlabel="Ano", ylabel="Minutos")
    ax.set_xticks(anual["ano"])
    mostrar(fig)

media_ano = df.groupby("ano")["passageiros"].sum() / df.groupby("ano")["data"].nunique() / 1e6
txt = f"O maior volume mensal do recorte foi em {mensal.idxmax():%m/%Y} ({fmt_dec(mensal.max())} mi de passageiros) e o menor em {mensal.idxmin():%m/%Y} ({fmt_dec(mensal.min())} mi). "
if len(media_ano) >= 2:
    v = media_ano.iloc[-1] / media_ano.iloc[0] - 1
    txt += (f"Comparando {media_ano.index[0]} e {media_ano.index[-1]}, o fluxo mensal médio está "
            f"**{descrever_variacao(v)}** ({v:+.1%}). ")
if len(anual) >= 2:
    dt = anual["tempo_medio_deslocamento"].iloc[-1] - anual["tempo_medio_deslocamento"].iloc[0]
    txt += (f"O tempo médio de deslocamento passou de {fmt_dec(anual['tempo_medio_deslocamento'].iloc[0])} "
            f"para {fmt_dec(anual['tempo_medio_deslocamento'].iloc[-1])} min ({dt:+.1f} min), "
            f"variação pequena diante da dispersão dos dados.")
interpretacao(txt)

st.subheader("Tabela: passageiros (milhões) por ano e região")
tab = df.pivot_table(index="ano", columns="regiao", values="passageiros", aggfunc="sum", margins=True,
                     margins_name="Total") / 1e6
tab.index = tab.index.astype(str)
st.dataframe(tab.round(1), width="stretch")

st.subheader("Conclusão executiva")
reg = df.groupby("regiao")["passageiros"].sum().sort_values(ascending=False)
pressao = df.groupby("regiao")["indice_pressao"].mean().sort_values(ascending=False)
st.success(
    f"- **Fluxo:** {k['cidade']} lidera o recorte, e a região {reg.index[0]} concentra "
    f"{reg.iloc[0] / reg.sum():.0%} dos passageiros (em parte porque tem mais cidades na base).\n"
    f"- **Modais:** {k['modal']} é o predominante, mas com apenas {k['modal_pct']:.0%} do total: "
    f"a diferença entre os meios é pequena.\n"
    f"- **Tempo:** a média é de {fmt_dec(k['tempo'])} min, sem tendência clara de piora ou melhora ao longo dos anos.\n"
    f"- **Pressão:** {pressao.index[0]} tem o maior índice médio de pressão (lotação + congestionamento).\n"
    f"- **Cuidado:** a base é simulada e as variáveis são praticamente independentes entre si "
    f"(veja a página *Correlações*). Os resultados servem para praticar o método, não para decidir política pública."
)
