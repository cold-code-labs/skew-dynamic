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

## Estado e próximas frentes
Tese central **provada** (W1–W5 + P1–P5, blocos 00–16; ver `docs/FINDINGS.md`).
**Frentes abertas, priorizadas e detalhadas em `docs/RESEARCH-AGENDA.md`** —
destaques: multi-momento + colapso de distribuição (barato, roda no dataset),
tênis (generalização externa), prêmio de skewness/CPT (ângulo econômico), forma
fechada da derivação, robustez adversarial. `docs/LITERATURA.md` ancora tudo.

## Estilo
- Português nos comentários e docs. Código limpo, funções pequenas.
- Stack: Python, pandas/numpy/scipy/statsmodels/ruptures.
