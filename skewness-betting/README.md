# Estabilidade da Skewness em Mercados de Apostas de Futebol

Estudo empírico sobre a **estabilidade temporal da assimetria (skewness)** da
distribuição de retornos implícitos em mercados de apostas de futebol.

**Tese:** a skewness do mercado não é um processo dinâmico — é um **invariante
estrutural**. Cada liga tem um nível de skewness próprio, fixo no tempo,
determinado pela sua competitividade. A flutuação observada é ruído amostral
puro. A assimetria é propriedade do gerador esportivo, exógena ao apreçamento
das casas.

## Dados

Dataset multi-liga 2000–2025 (~230k jogos, 38 ligas) com odds 1X2 médias e
máximas de mercado. Recorte do estudo: ≥2005 (cobertura de odds ~100%),
205.435 jogos. Ver `analysis/00_fetch_data.py`. A fonte canônica é
football-data.co.uk — na sua infra, empilhe todas as temporadas/ligas.

> `data/` não é versionado (ver `.gitignore`). Rode o fetcher ou aponte
> `skewlib/config.py:DATA_PATH` para o seu dump.

## Estrutura

```
skewlib/              módulo reutilizável
  config.py           parâmetros (janela, passo, recorte, de-vig, paths)
  io.py               carga + limpeza
  returns.py          retornos ex-post (favorito, azarão, Max*, demeaned)
  series.py           série deslizante de skewness + bootstrap
  stats.py            estacionariedade, i.i.d., quebras, bootstrap_corr, ols
  decompose.py        decomposição por estratégia / faixa de odds / liga
  devig.py            de-vigging 1X2 (multiplicative / Shin / power)
  exante.py           skewness ex-ante (implícita) + cumulantes totais [objeto primário]
  elo.py              Elo só de resultados → competitividade odds-free
  panel.py            painel liga×temporada, tendência, variância, COVID
  overunder.py        mercado binário over/under 2.5
analysis/             scripts finos que importam skewlib (um por bloco)
  00_fetch_data.py    baixa o dataset
  01..06              Blocos A–F originais (ver docs/FINDINGS.md)
  07_devig_exante.py  W1 — skewness ex-ante + decomposição mecânica
  08_mechanism_elo.py W2 — lei skewness~competitividade ODDS-FREE
  09_panel_temporal.py W3 — invariância temporal (painel, COVID)
  10_overunder.py     W5 — mercado binário over/under 2.5
  11_margin_robustness.py W4 — margem ortogonal + robustez de-vig
  12_figures.py       figuras do paper (F1–F4)
docs/                 metodologia, achados (log de fases), outline + abstract
outputs/              séries, tabelas, figuras geradas (não versionado)
data/PROVENANCE.json  hash + recorte do dataset congelado (versionado)
```

## Como rodar

Pipeline completa num comando (cria venv, instala deps, baixa o dado e roda
os blocos 00→06 em ordem):

```bash
./run.sh                # tudo; --no-fetch pula o download, --no-venv usa o python atual
```

Ou passo a passo:

```bash
pip install -r requirements.txt
python analysis/00_fetch_data.py            # baixa data/matches.csv
PYTHONPATH=. python analysis/01_baseline.py # ou qualquer 0X_*
```

## Achados (resumo)

| Frente | Resultado |
|---|---|
| A–F (originais) | estacionariedade blindada; FLB; ruído branco; margem=spread; skew=f(liga) |
| W1 mecânico | skewness ex-ante ≈ ex-post (+0.236/+0.230); M₃ **+102.6% intra-jogo** (= imagem do FLB) |
| W2 odds-free | lei sobrevive: skew~zebra +0.83, ~entropia +0.72; corr(Elo,odds)=0.91 |
| W3 temporal | painel sem tendência (β=+0.0002/ano, p=0.73); ICC 0.70; COVID corrobora a causa |
| W4 margem | overround 1.067→1.009, skewness +0.236→+0.254 (ortogonal); robusto ao de-vig |
| W5 binário | over/under 2.5: identidade vale fora do 1X2 (within 99.6%) |

Detalhes e log de fases em `docs/FINDINGS.md`; metodologia em `docs/METHODOLOGY.md`.
