# CLAUDE.md — convenções do projeto

Contexto para o Claude Code ao continuar este estudo.

## O que é
Estudo empírico de skewness em mercados de apostas de futebol. Objetivo final:
um paper. Tese: skewness é invariante estrutural (não dinâmico), função da
competitividade da liga. Ver `docs/FINDINGS.md` para o estado atual.

## Arquitetura
- Toda lógica reutilizável vive em `skewlib/`. Scripts em `analysis/` são finos
  e importam de `skewlib` — **não duplicar lógica** nos scripts.
- Adicionar capacidade nova = função em `skewlib`, depois um script fino que a usa.
- Parâmetros (janela, passo, recorte) só em `skewlib/config.py`.

## Dados
- `data/` nunca é commitado. Apontar `config.DATA_PATH` para o dump local.
- Na infra própria, preferir football-data.co.uk como fonte canônica e empilhar
  todas as temporadas/ligas (mais cobertura que o mirror de bootstrap).
- Sempre filtrar odds inválidas (`MIN_ODD`) — o dado tem zeros/valores sujos.

## Rigor estatístico (não regredir)
- Para inferência, usar **janelas não-sobrepostas** (`overlap=False`). A
  sobreposição infla autocorrelação — foi o que mascarou "persistência" na v1.
- Skewness é momento de 3ª ordem → erro-padrão por bootstrap, nunca assumir normal.
- Confirmação dupla de estacionariedade (ADF + KPSS).
- Reportar sensibilidade a tamanho de janela como robustez.

## Próximas frentes (ver fim de docs/FINDINGS.md)
1. Modelar skewness_liga ~ índice de competitividade (HHI/Gini) — formaliza o −0.83.
2. Drift abertura→fechamento (precisa de odds de abertura).
3. Mercado over/under 2.5 (binário) vs 1X2.
4. Generalização externa: repetir em basquete/tênis.

## Estilo
- Português nos comentários e docs. Código limpo, funções pequenas.
- Stack: Python, pandas/numpy/scipy/statsmodels/ruptures.
