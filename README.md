# Mobilidade Urbana e Transporte Público no Brasil (2015–2024)

Projeto da **Avaliação G1** de Linguagem de Programação — Análise e Visualização de Dados com Python (Tema 16).

| Entrega | Link |
|---|---|
| Repositório GitHub | https://github.com/MFC-Gabriel/projeto_Mobilidade_Urbana_Brasil |
| Página do projeto (GitHub Pages) | https://mfc-gabriel.github.io/projeto_Mobilidade_Urbana_Brasil/ |
| Dashboard (Streamlit Cloud) | https://mobilidade-urbana-gabriel.streamlit.app/ |

## Problema
Como se comportam o fluxo de passageiros, o tempo de deslocamento, a lotação e o congestionamento nas cidades brasileiras entre 2015 e 2024? Quais cidades, regiões e meios de transporte concentram mais fluxo e mais pressão sobre o sistema?

## Base de dados
`dados/simulacao_mobilidade_urbana_brasil.csv` — base **simulada**, 4.440 linhas (cidade × mês), 37 cidades, 20 UFs, 5 regiões, 6 meios de transporte, jan/2015 a dez/2024. Sem valores nulos nem duplicatas.

Colunas: `ano, mes, data, regiao, uf, cidade, meio_transporte, passageiros, tempo_medio_deslocamento, lotacao_media, velocidade_media, emissao_co2, tarifa_media, nivel_congestionamento`.

## Tratamento e atributos criados
- conversão de `data` para datetime, remoção de espaços, duplicatas e nulos; checagem de coerência `ano/mes` × `data`;
- `nivel_congestionamento` como categoria ordenada (Baixo < Médio < Alto < Crítico) e `nivel_num` (1 a 4);
- `superlotacao` (lotação > 100%), `indice_pressao` (média entre lotação relativa a 120% e congestionamento relativo a 4), `co2_por_mil_pass`, `mes_nome` e `trimestre`.

## Funcionalidades
**Intermediárias:** filtros múltiplos (7 filtros, com UF e cidade dependentes da região) e KPIs dinâmicos (recalculados sobre os dados filtrados).
**Avançadas:** dashboard multipágina (`st.navigation`, 5 páginas) e correlação estatística (Pearson e Spearman, valor-p, heatmap e dispersão).

## Páginas do dashboard
1. **Visão geral:** descrição do problema, 6 KPIs, evolução temporal, tabela e conclusão executiva.
2. **Regiões e cidades:** comparação regional, ranking de cidades, índice de pressão e tabela.
3. **Meios de transporte:** comparação modal, emissões de CO₂ e tabela dinâmica.
4. **Congestionamento e sazonalidade:** distribuição dos níveis e mapa de calor mês × ano.
5. **Correlações:** matriz, dispersão com r, ρ e valor-p, e interpretação.

Cada página traz interpretação textual calculada sobre o recorte filtrado.

## Principais resultados
- Rio de Janeiro é a cidade mais movimentada (131,1 mi) e o Metrô o modal predominante (17,5%), com margens estreitas.
- O tempo médio de deslocamento (54,3 min) não apresenta tendência entre 2015 e 2024.
- O Sudeste concentra 35% dos passageiros por ter 13 das 37 cidades; por cidade-mês, as regiões são parecidas.
- Todas as correlações entre variáveis ficam abaixo de |0,03|: o congestionamento não se associa a tempo, velocidade ou lotação.

## Limitações
Base simulada (resultados uniformes são esperados); sem coluna de horário (horários de pico não são mensuráveis, a sazonalidade foi analisada por mês × ano); sem população (a relação população × fluxo exigiria dados do IBGE); velocidade, emissão e tarifa sem unidade (adotados km/h e R$).

## Estrutura
```
projeto-mobilidade-urbana/
├── app.py                  # navegação e filtros globais
├── utils.py                # tratamento, filtros, KPIs e helpers
├── paginas/                # 5 páginas do dashboard
├── requirements.txt
├── README.md
├── index.html              # página do GitHub Pages
├── dados/                  # CSV da base
├── notebooks/              # análise completa (.ipynb)
├── database/               # reservada para persistência (SQLite)
└── imagens/                # gráficos exportados pelo notebook
```

## Como executar
```bash
pip install -r requirements.txt
streamlit run app.py
```
Para reproduzir o notebook: `jupyter notebook notebooks/analise_mobilidade_urbana.ipynb`.

## Publicação
1. **GitHub:** suba a pasta para um repositório público.
2. **GitHub Pages:** *Settings → Pages → Deploy from a branch → main / (root)*; o `index.html` da raiz vira a página do projeto.
3. **Streamlit Community Cloud:** *New app* → escolha o repositório, branch `main` e o arquivo `app.py`.


