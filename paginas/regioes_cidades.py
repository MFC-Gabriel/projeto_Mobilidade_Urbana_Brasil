import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from utils import fmt_dec, fmt_mi, interpretacao, mostrar, obter_df

df = obter_df()
st.title("Regiões e cidades")
st.write("Onde está o maior fluxo de passageiros e onde o sistema sofre mais pressão.")

reg = (df.groupby("regiao")
         .agg(total=("passageiros", "sum"), media=("passageiros", "mean"),
              cidades=("cidade", "nunique"), pressao=("indice_pressao", "mean"))
         .sort_values("total", ascending=False).reset_index())

st.subheader("Comparação regional")
c1, c2 = st.columns(2)
with c1:
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sns.barplot(data=reg, y="regiao", x=reg["total"] / 1e6, hue="regiao", legend=False, ax=ax, palette="Blues_r")
    ax.set(title="Total de passageiros (milhões)", xlabel="Passageiros (mi)", ylabel="")
    mostrar(fig)
with c2:
    r2 = reg.sort_values("media", ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sns.barplot(data=r2, y="regiao", x=r2["media"] / 1e3, hue="regiao", legend=False, ax=ax, palette="Greens_r")
    ax.set(title="Média de passageiros por cidade-mês (mil)", xlabel="Passageiros (mil)", ylabel="")
    mostrar(fig)

fig, ax = plt.subplots(figsize=(11, 4))
ra = df.groupby(["ano", "regiao"])["passageiros"].sum().reset_index()
ra["passageiros"] /= 1e6
sns.lineplot(data=ra, x="ano", y="passageiros", hue="regiao", marker="o", ax=ax)
ax.set(title="Passageiros por ano e região (milhões)", xlabel="Ano", ylabel="Passageiros (mi)")
ax.set_xticks(sorted(ra["ano"].unique()))
ax.legend(title="Região", bbox_to_anchor=(1.01, 1), loc="upper left")
mostrar(fig)

maior, maior_media = reg.iloc[0], reg.sort_values("media", ascending=False).iloc[0]
interpretacao(
    f"{maior['regiao']} tem o maior volume total ({fmt_mi(maior['total'])}), mas o total depende de quantas "
    f"cidades cada região tem na base ({int(maior['cidades'])} em {maior['regiao']}). Ao normalizar pela "
    f"média por cidade-mês, a região líder passa a ser **{maior_media['regiao']}** "
    f"({fmt_dec(maior_media['media'] / 1e3, 0)} mil). Na prática, as diferenças regionais por cidade são pequenas.")

st.subheader("Cidades")
n_cid = df["cidade"].nunique()
top_n = st.slider("Quantas cidades exibir no ranking", 3, min(20, n_cid), min(10, n_cid)) if n_cid > 3 else n_cid
cid = (df.groupby(["cidade", "regiao"])
         .agg(passageiros=("passageiros", "sum"), tempo=("tempo_medio_deslocamento", "mean"),
              lotacao=("lotacao_media", "mean"), superlotacao=("superlotacao", "mean"),
              pressao=("indice_pressao", "mean"))
         .reset_index())
c3, c4 = st.columns(2)
with c3:
    t = cid.nlargest(top_n, "passageiros")
    fig, ax = plt.subplots(figsize=(6.5, 0.38 * top_n + 1.6))
    sns.barplot(data=t, y="cidade", x=t["passageiros"] / 1e6, hue="regiao", dodge=False, ax=ax)
    ax.set(title=f"Top {top_n} cidades por passageiros (mi)", xlabel="Passageiros (mi)", ylabel="")
    ax.legend(title="Região", fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    mostrar(fig)
with c4:
    t = cid.nlargest(top_n, "pressao")
    fig, ax = plt.subplots(figsize=(6.5, 0.38 * top_n + 1.6))
    sns.barplot(data=t, y="cidade", x="pressao", hue="regiao", dodge=False, ax=ax)
    ax.set(title=f"Top {top_n} cidades por índice de pressão", xlabel="Índice de pressão (0 a 1)", ylabel="")
    ax.legend(title="Região", fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    mostrar(fig)

top = cid.nlargest(1, "passageiros").iloc[0]
pr = cid.nlargest(1, "pressao").iloc[0]
interpretacao(
    f"**{top['cidade']}** ({top['regiao']}) é a cidade mais movimentada, com {fmt_mi(top['passageiros'])} passageiros. "
    f"Já a maior pressão sobre o sistema está em **{pr['cidade']}**, com índice {fmt_dec(pr['pressao'], 2)} "
    f"(combina lotação média de {fmt_dec(pr['lotacao'], 0)}% e o nível de congestionamento). "
    f"Mais passageiros não significam mais pressão: os dois rankings são diferentes.")

st.subheader("Tabela detalhada por cidade")
tab = cid.sort_values("passageiros", ascending=False).rename(columns={
    "cidade": "Cidade", "regiao": "Região", "passageiros": "Passageiros",
    "tempo": "Tempo médio (min)", "lotacao": "Lotação média (%)",
    "superlotacao": "% registros em superlotação", "pressao": "Índice de pressão"})
tab["% registros em superlotação"] *= 100
st.dataframe(tab.round(2), width="stretch", hide_index=True)
st.caption("Índice de pressão = média entre a lotação (relativa a 120%) e o nível de congestionamento (1 a 4, relativo a 4).")
