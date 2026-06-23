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
- **Multi-esporte:** o núcleo (`skewlib/canonical.py` + `skewmeter`) é sport-agnóstico
  e consome a tabela canônica (`docs/DATA-SCHEMA.md`). Adicionar um esporte/mercado =
  um adaptador em `skewlib/adapters/` (mapeia bruto→canônico + taxonomia), registrado
  em `adapters/__init__.py`. **Não** ramificar o núcleo por esporte. O futebol delega
  a de-vig ao caminho congelado → números bit-idênticos (asserção em `47_canonical.py`).

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
Tese central **provada** (W1–W5 + P1–P5 + B + C + E, blocos 00–22; ver
`docs/FINDINGS.md`). **Frentes abertas, priorizadas e detalhadas em
`docs/RESEARCH-AGENDA.md`** — restantes no dataset: G (robustez adversarial,
próxima), F (micro), D2–D4 (microestrutura), H2 (aberto×fechado), C3 (Kelly), E3
(calibração por liga). `docs/LITERATURA.md` ancora tudo.

## Lineage / proveniência / versionamento (NÃO pular)
Cada achado é pinado à versão exata que o produziu. Disciplina ao fechar uma frente:
1. **Carimbar** — todo bloco novo termina com
   `prov.write_stamp("NN_nome", metrics={...})` (números-título), gravando git
   sha + hash do dataset + libs em `outputs/_provenance/` (regenerável).
2. **Timeline** — adicionar a fase ao `docs/FINDINGS.md` (Fase X) **e** ao
   `site/src/components/Timeline.astro` (uma entrada por sub-achado).
3. **Ledger** — registrar a fase em `analysis/build_lineage.py:PHASES` (blocos,
   figuras, números, commit, tag), rodar `python analysis/build_lineage.py` p/
   regenerar `lineage.json` + `docs/LINEAGE.md`.
4. **Versionar** — commit; depois `git tag -a evidence/<frente> <sha> -m "..."`
   no commit que estabeleceu os números (`--tags` sugere os comandos).
5. **Auditar** — `python analysis/build_lineage.py --check` compara os carimbos de
   execução com o ledger e acusa **DRIFT** (script mudou ⇒ número mudou). O
   `run.sh` já roda isso no fim da pipeline. Se houver drift legítimo, atualizar o
   ledger + nova tag — o git guarda o histórico do número antigo.
`git checkout evidence/frente-E` recupera o código exato de qualquer evidência.

## Estilo
- Português nos comentários e docs. Código limpo, funções pequenas.
- Stack: Python, pandas/numpy/scipy/statsmodels/ruptures.
