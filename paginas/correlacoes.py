import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
from scipy import stats

from utils import CURTOS, ROTULOS, fmt_dec, interpretacao, mostrar, obter_df

df = obter_df()
st.title("Correlações estatísticas")
st.write("Existe relação entre passageiros, tempo de deslocamento e as demais medidas do sistema?")

cols = list(CURTOS)
if len(df) < 10:
    st.warning("Poucos registros no recorte para calcular correlações. Amplie os filtros.")
    st.stop()


def forca(r: float) -> str:
    a = abs(r)
    for lim, nome in [(0.1, "desprezível"), (0.3, "fraca"), (0.5, "moderada"), (0.7, "forte")]:
        if a < lim:
            return nome
    return "muito forte"


st.subheader("Matriz de correlação")
metodo = st.radio("Método", ["Pearson", "Spearman"], horizontal=True,
                  help="Pearson mede relação linear; Spearman mede relação monotônica (por postos).")
corr = df[cols].corr(method=metodo.lower())
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.heatmap(corr.rename(index=CURTOS, columns=CURTOS), mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, center=0, linewidths=0.5, ax=ax)
ax.set_title(f"Correlação de {metodo} entre as variáveis")
mostrar(fig)

pares = (corr.where(~mask & ~np.eye(len(cols), dtype=bool)).stack().rename("r").reset_index())
pares.columns = ["Variável A", "Variável B", "r"]
pares["Variável A"] = pares["Variável A"].map(CURTOS)
pares["Variável B"] = pares["Variável B"].map(CURTOS)
pares["|r|"] = pares["r"].abs()
pares["Força"] = pares["r"].map(forca)
pares = pares.sort_values("|r|", ascending=False)
mais = pares.iloc[0]
interpretacao(
    f"O par com maior correlação é **{mais['Variável A']} × {mais['Variável B']}** (r = {fmt_dec(mais['r'], 2)}), "
    f"classificada como **{mais['Força']}**. Quando todos os coeficientes ficam abaixo de 0,10, "
    f"as variáveis são praticamente independentes: saber uma delas não ajuda a prever a outra.")
with st.expander("Ver todos os pares ordenados"):
    st.dataframe(pares.drop(columns="|r|").round(3), width="stretch", hide_index=True)

st.subheader("Dispersão entre duas variáveis")
rot = {CURTOS[c]: c for c in cols}
a, b = st.columns(2)
xl = a.selectbox("Eixo X", list(rot), index=0)
yl = b.selectbox("Eixo Y", list(rot), index=1)
x, y = rot[xl], rot[yl]
if x == y:
    st.warning("Escolha variáveis diferentes para os eixos X e Y.")
    st.stop()

r, p = stats.pearsonr(df[x], df[y])
rho, p_s = stats.spearmanr(df[x], df[y])
fig, ax = plt.subplots(figsize=(9, 4.8))
sns.regplot(data=df, x=x, y=y, scatter_kws={"alpha": 0.25, "s": 12, "color": "#1E63D6"},
            line_kws={"color": "#C0392B", "lw": 2}, ax=ax)
ax.set(title=f"{CURTOS[x]} × {CURTOS[y]}", xlabel=ROTULOS[x], ylabel=ROTULOS[y])
mostrar(fig)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Pearson (r)", fmt_dec(r, 3))
m2.metric("Spearman (ρ)", fmt_dec(rho, 3))
m3.metric("R² da reta", fmt_dec(r ** 2, 4))
m4.metric("Valor-p (Pearson)", "< 0,001" if p < 0.001 else fmt_dec(p, 3))

direcao = "positiva" if r > 0 else "negativa"
if p >= 0.05:
    sig = (f"O valor-p ({fmt_dec(p, 3)}) é maior que 0,05, portanto **não há evidência estatística** de relação entre as variáveis.")
elif abs(r) < 0.1:
    sig = "O resultado é estatisticamente significativo, mas a força é desprezível, então o efeito prático é irrelevante."
else:
    sig = "O resultado é estatisticamente significativo e a relação tem relevância prática."
interpretacao(
    f"A correlação entre {CURTOS[x].lower()} e {CURTOS[y].lower()} é **{forca(r)}** e {direcao} "
    f"(r = {fmt_dec(r, 3)}; ρ = {fmt_dec(rho, 3)}). A reta explica {r ** 2:.2%} da variação. {sig} "
    f"Lembre que correlação não implica causalidade, mesmo quando ela é forte.")

st.subheader("Conclusão da análise de correlação")
st.success(
    "- Na base fornecida, as medidas de mobilidade variam de forma independente. Isso é coerente com dados simulados "
    "por sorteio, em que cada coluna é gerada separadamente.\n"
    "- Em dados reais, esperaríamos correlação positiva entre congestionamento e tempo de deslocamento, e negativa "
    "com velocidade. Sua ausência aqui é um sinal de que a base não reproduz a dinâmica real.\n"
    "- A pergunta *população × fluxo* não pode ser respondida: a base não tem população. Para respondê-la, seria "
    "preciso cruzar com dados do IBGE por cidade."
)
