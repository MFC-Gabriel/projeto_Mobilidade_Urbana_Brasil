import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from utils import (CORES_NIVEL, MESES, ORDEM_NIVEL, ROTULOS, fmt_dec, interpretacao, mostrar, obter_df)
import pandas as pd

df = obter_df()
st.title("Congestionamento e sazonalidade")
st.write("Distribuição dos níveis de congestionamento e padrões por mês e ano.")

st.subheader("Distribuição dos níveis")
c1, c2 = st.columns(2)
with c1:
    cont = df["nivel_congestionamento"].value_counts(normalize=True).reindex(ORDEM_NIVEL).fillna(0) * 100
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sns.barplot(x=cont.index, y=cont.values, hue=cont.index, palette=CORES_NIVEL, legend=False, ax=ax)
    ax.set(title="% de registros por nível de congestionamento", xlabel="", ylabel="% dos registros")
    mostrar(fig)
with c2:
    ct = (pd.crosstab(df["regiao"], df["nivel_congestionamento"], normalize="index") * 100
          ).reindex(columns=ORDEM_NIVEL, fill_value=0)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ct.plot(kind="barh", stacked=True, color=[CORES_NIVEL[n] for n in ORDEM_NIVEL], ax=ax, width=0.7)
    ax.set(title="Níveis por região (% dos registros)", xlabel="%", ylabel="")
    ax.legend(title="Nível", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    mostrar(fig)

crit = cont["Crítico"]
interpretacao(
    f"**{crit:.0f}%** dos registros estão em nível crítico e {cont['Alto']:.0f}% em nível alto. "
    f"Região com maior fatia crítica: **{ct['Crítico'].idxmax()}** ({ct['Crítico'].max():.0f}%). "
    f"Os quatro níveis têm pesos muito parecidos, e isso vale para todas as regiões.")

st.subheader("Evolução do congestionamento")
ev = (df.assign(critico=df["nivel_congestionamento"].eq("Crítico"))
        .groupby("ano").agg(nivel=("nivel_num", "mean"), critico=("critico", "mean")).reset_index())
ev["critico"] *= 100
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
sns.lineplot(data=ev, x="ano", y="nivel", marker="o", ax=axes[0], color="#E8782A")
axes[0].set(title="Nível médio (1 = baixo, 4 = crítico)", xlabel="Ano", ylabel="Nível médio")
sns.lineplot(data=ev, x="ano", y="critico", marker="o", ax=axes[1], color="#C0392B")
axes[1].set(title="% de registros em nível crítico", xlabel="Ano", ylabel="%")
for ax in axes:
    ax.set_xticks(ev["ano"])
    ax.tick_params(axis="x", labelsize=8)
fig.tight_layout()
mostrar(fig)

st.subheader("Sazonalidade: mês × ano")
st.caption("A base é mensal e não possui coluna de horário. Por isso os horários de pico não podem ser "
           "medidos, e o mapa de calor abaixo mostra a variação por mês e ano.")
metricas = {v: k for k, v in ROTULOS.items() if k not in ("indice_pressao",)}
m = st.selectbox("Métrica (média por registro)", list(metricas), index=1)
col = metricas[m]
hm = df.pivot_table(index="mes", columns="ano", values=col, aggfunc="mean")
esc = 1e6 if col == "passageiros" else 1
hm = (hm / esc).rename(index=MESES)
fig, ax = plt.subplots(figsize=(11, 4.6))
sns.heatmap(hm, annot=True, fmt=".2f" if col in ("passageiros", "nivel_num", "tarifa_media") else ".1f",
            cmap="YlOrRd", annot_kws={"size": 7}, cbar_kws={"label": m + (" (mi)" if esc > 1 else "")}, ax=ax)
ax.set(title=f"{m}: média por mês e ano", xlabel="Ano", ylabel="")
ax.tick_params(axis="y", rotation=0)
mostrar(fig)
mm = hm.mean(axis=1)
interpretacao(
    f"Na média dos anos, o mês com maior valor é **{mm.idxmax()}** e o menor é **{mm.idxmin()}**. "
    f"A variação entre meses é pequena e não forma um padrão sazonal estável de um ano para o outro: "
    f"o mapa não mostra faixas de cor consistentes, o que é típico de dados gerados aleatoriamente.")

st.subheader("O congestionamento acompanha tempo e velocidade?")
tb = df.groupby("nivel_congestionamento", observed=True)[
    ["tempo_medio_deslocamento", "velocidade_media", "lotacao_media"]].mean().round(1)
tb.columns = ["Tempo médio (min)", "Velocidade média (km/h)", "Lotação média (%)"]
st.dataframe(tb, width="stretch")
if {"Baixo", "Crítico"} <= set(tb.index):
    dif = tb.loc["Crítico", "Tempo médio (min)"] - tb.loc["Baixo", "Tempo médio (min)"]
    interpretacao(
        f"Em um sistema real, trechos críticos teriam deslocamentos mais longos e velocidades menores. Aqui a diferença "
        f"de tempo entre os níveis crítico e baixo é de apenas {dif:+.1f} min, ou seja, o nível de congestionamento "
        f"não se relaciona com as demais medidas.")
