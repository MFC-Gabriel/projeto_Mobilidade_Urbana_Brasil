import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import ROTULOS, fmt_dec, fmt_mi, interpretacao, mostrar, obter_df

df = obter_df()
st.title("Meios de transporte")
st.write("Comparação modal: uso, desempenho, tarifa e emissões.")

ordem = df.groupby("meio_transporte")["passageiros"].sum().sort_values(ascending=False)
ordem_idx = list(ordem.index)

st.subheader("Uso por meio de transporte")
fig, ax = plt.subplots(figsize=(10, 3.8))
sns.barplot(x=ordem.index, y=ordem.values / 1e6, hue=ordem.index, legend=False, ax=ax, palette="viridis")
for i, v in enumerate(ordem.values / 1e6):
    ax.text(i, v, fmt_dec(v, 0), ha="center", va="bottom", fontsize=9)
ax.set(title="Total de passageiros por meio de transporte (milhões)", xlabel="", ylabel="Passageiros (mi)")
mostrar(fig)
spread = (ordem.max() - ordem.min()) / ordem.mean()
interpretacao(
    f"**{ordem.index[0]}** é o meio predominante ({fmt_mi(ordem.iloc[0])}) e **{ordem.index[-1]}** o menos usado "
    f"({fmt_mi(ordem.iloc[-1])}). A distância entre o maior e o menor equivale a {spread:.0%} da média dos modais, "
    f"ou seja, o uso está bem distribuído e nenhum meio domina de fato.")

st.subheader("Desempenho médio por meio de transporte")
metricas = ["tempo_medio_deslocamento", "velocidade_media", "lotacao_media", "tarifa_media"]
fig, axes = plt.subplots(2, 2, figsize=(11, 6))
for ax, m in zip(axes.ravel(), metricas):
    sns.barplot(data=df, x="meio_transporte", y=m, order=ordem_idx, hue="meio_transporte",
                hue_order=ordem_idx, legend=False, errorbar=None, ax=ax, palette="mako")
    ax.set(title=ROTULOS[m], xlabel="", ylabel="")
    ax.tick_params(axis="x", labelsize=8)
fig.tight_layout()
mostrar(fig)
med = df.groupby("meio_transporte")[metricas].mean()
interpretacao(
    f"Maior tarifa média: **{med['tarifa_media'].idxmax()}** (R$ {fmt_dec(med['tarifa_media'].max(), 2)}); "
    f"menor: **{med['tarifa_media'].idxmin()}** (R$ {fmt_dec(med['tarifa_media'].min(), 2)}). "
    f"O meio mais rápido é **{med['velocidade_media'].idxmax()}** ({fmt_dec(med['velocidade_media'].max())} km/h) e o mais "
    f"lotado é **{med['lotacao_media'].idxmax()}** ({fmt_dec(med['lotacao_media'].max())}%). "
    f"As diferenças entre os modais são de poucos pontos, o que reforça o caráter simulado da base.")

st.subheader("Análise ambiental: emissões de CO₂")
c1, c2 = st.columns(2)
with c1:
    em = df.groupby("meio_transporte")["co2_por_mil_pass"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sns.barplot(x=em.values, y=em.index, hue=em.index, legend=False, ax=ax, palette="rocket")
    ax.set(title="CO₂ por mil passageiros (média)", xlabel="Emissão estimada por mil passageiros", ylabel="")
    mostrar(fig)
with c2:
    er = df.groupby("regiao")["emissao_co2"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sns.barplot(x=er.values / 1e6, y=er.index, hue=er.index, legend=False, ax=ax, palette="flare")
    ax.set(title="Emissão total de CO₂ por região (milhões)", xlabel="Emissão estimada (mi)", ylabel="")
    mostrar(fig)
interpretacao(
    f"Por passageiro, o meio mais intensivo em emissões é **{em.index[0]}** e o menos intensivo é **{em.index[-1]}**. "
    f"A emissão não tem unidade definida na base, então o valor serve para comparar os grupos entre si. "
    f"A região com maior emissão total é **{er.index[0]}**, o que acompanha seu número de cidades.")

st.subheader("Tabela dinâmica")
dims = {"Região": "regiao", "UF": "uf", "Cidade": "cidade", "Meio de transporte": "meio_transporte",
        "Ano": "ano", "Mês": "mes", "Congestionamento": "nivel_congestionamento"}
vals = {v: k for k, v in ROTULOS.items() if k != "nivel_num"}
funcs = {"Soma": "sum", "Média": "mean", "Mediana": "median", "Contagem": "count"}
a, b, c, d = st.columns(4)
lin = a.selectbox("Linhas", list(dims), index=3)
col = b.selectbox("Colunas", ["(nenhuma)"] + list(dims), index=1)
val = c.selectbox("Valores", list(vals), index=0)
fn = d.selectbox("Função", list(funcs), index=1)
if col != "(nenhuma)" and dims[col] == dims[lin]:
    st.warning("Escolha dimensões diferentes para linhas e colunas.")
else:
    pv = pd.pivot_table(df, index=dims[lin], columns=None if col == "(nenhuma)" else dims[col],
                        values=vals[val], aggfunc=funcs[fn], observed=True)
    st.dataframe(pv.round(2), width="stretch")
