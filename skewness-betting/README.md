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
  config.py           parâmetros (janela, passo, recorte, paths)
  io.py               carga + limpeza
  returns.py          retornos ex-post (favorito, azarão, Max*, demeaned)
  series.py           série deslizante de skewness + bootstrap
  stats.py            estacionariedade, persistência, variance-ratio, AR(1), quebras
  decompose.py        decomposição por estratégia / faixa de odds / liga
analysis/             scripts finos que importam skewlib (um por bloco)
  00_fetch_data.py    baixa o dataset
  01_baseline.py      série + estatísticas globais
  02_robustness.py    Bloco A — demeaning, overlap, tamanho de janela
  03_decomposition.py Bloco B — FLB, mecanismo da estabilidade
  04_dynamics.py      Bloco C — i.i.d.? variance-ratio, AR(1)
  05_cross_book.py    Bloco D — odd média vs melhor odd
  06_league_hetero.py Bloco E+F — heterogeneidade entre ligas, blip
docs/                 metodologia, achados, rascunho do paper
outputs/              séries e tabelas geradas (não versionado)
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

| Bloco | Resultado |
|---|---|
| A robustez | estacionariedade blindada; persistência aparente era artefato de overlap |
| B decomposição | FLB confirmado; skewness monotônica na improbabilidade; cancelamento de caudas |
| C dinâmica | ruído branco (VR≈1, AR(1) não-significativo) — sem dinâmica temporal |
| D cross-casa | margem é spread entre casas (−4.8%→−0.2%); skewness invariante à casa (corr 0.98) |
| E ligas | skewness = f(competitividade), corr −0.83; cada liga tem seu invariante |
| F forense | única "quebra" em 20 anos = dataset crescendo 21→37 ligas em 2012 |

Detalhes em `docs/FINDINGS.md`.
