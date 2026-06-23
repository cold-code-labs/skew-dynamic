# Agenda de Pesquisa — frentes abertas da tese

> Handoff técnico para sessões futuras. A tese central já está **provada e
> reproduzível** (ver `FINDINGS.md`, blocos 00–16). Este doc lista as frentes
> **não exploradas** que aprofundam/atacam a tese, priorizadas por payoff×custo.
> Marcado `[dataset]` = roda no dado congelado atual; `[novo dado]` = precisa de
> fonte externa.

## Estado provado (não re-derivar)
- **Núcleo mecânico (W1):** skewness de mercado = E[m₃] da mistura de apostas de
  dois pontos; decomposição por cumulantes totais dá **within-match ≈ 100%**,
  between ≈ 0. Identidade por jogo: `(1−2p)/√(p(1−p))`. Código: `exante.py`.
- **Lei estrutural (W2/P2/P3):** skew_liga = f(competitividade), sobrevive a
  proxies odds-free (Elo `elo.py`, índices de classificação `balance.py`) e é
  **derivada** por ordered-probit (`model.py`, prevê 3º momento do 1º, r=0.90).
- **Invariância (W3/P1):** painel liga×temporada sem tendência (β≈0), ICC 0.70,
  1 quebra em 38 ligas (COVID). `panel.py`.
- **Ortogonalidade da margem (W4)** + **mercado binário O/U (W5)** + **FLB
  estável no tempo (P4)**.

## Dados disponíveis no arquivo congelado
1X2 (`Odd*` médio, `Max*` melhor), **O/U 2.5** (`Over25/Under25/Max*`),
**handicap asiático** (`HandiSize/HandiHome/HandiAway`), gols (`FTHome/FTAway`,
`HT*`), times, **Elo pré-computado** (`HomeElo/AwayElo`), forma, chutes/cantos/
cartões, colunas `C_*` (features derivadas). **Não tem odds de abertura** nem
outros esportes — essas frentes precisam de fonte nova.

---

## Frente A — Validade externa / generalização  ⭐ maior payoff
**Hipótese:** a lei skewness=f(competitividade) e a invariância valem em QUALQUER
esporte; o nível é função dos parâmetros (h, c, σ_L) do gerador esportivo.

- **A1 [novo dado] Tênis** — mercado binário limpo (sem empate), Elo maduro, odds
  Pinnacle. Teste mais nítido da identidade `(1−2p)/√(p(1−p))` e da invariância.
  Prever a "constante" do tênis a priori pelo `model.py` (h≈0, c=0) e validar.
- **A2 [novo dado] Basquete** — quase 50/50, point spread; a skewness deve ser
  ~0 e pouco variável → teste de falsificação (competitividade alta ⇒ skew↑?).
- **A3 [dataset+novo] Meta-lei cross-esporte** — colapsar todos os esportes numa
  ÚNICA curva S(σ_L) reparametrizada. Se colarem, a lei é universal, não-futebol.
- **Construir:** adaptador de I/O por esporte (`io_<sport>.py`), reusar
  `exante/elo/model` intactos (são agnósticos a esporte). Fonte: tennis-data.co.uk,
  basketball odds (Kaggle), Pinnacle archives.

## Frente B — Estrutura de momentos / distribuição completa  ✅ FEITA (2026-06-23)
**Hipótese:** não só o 3º momento — a forma INTEIRA da distribuição implícita é
invariante após controlar competitividade.
> **Concluída** (Fases B1/B2 em `FINDINGS.md`): B1 multi-momento + B2 colapso.
> within_frac ≈1 em todas as ordens; modelo prevê var/skew/kurtose (r=0.99/0.90/0.89);
> colapso condicional à competitividade (KS 0.47→0.06, −87%). B3 (teorema) no paper.
> Artefatos: `skewlib/{exante,model,collapse}.py`, `analysis/17_moments.py`,
> `analysis/18_collapse.py`. **Pendente em B:** ajuste KS p/ discretização (bootstrap
> de bandas), e colapso do RESÍDUO observado−modelo (não só dos retornos crus).
- **B1** Estender `pooled_skew` → `pooled_moments` (var, skew, **kurtose**, e
  cumulantes 5–6). O ordered-probit (`model.py`) prevê TODOS os momentos; testar
  momentos 2–4 contra a curva derivada (invariância multi-momento > só skew).
- **B2** Colapso de distribuição: padronizar (z-score) os retornos por liga e
  testar se a distribuição padronizada é a MESMA entre ligas (KS/Anderson-Darling
  par-a-par) → "fato estilizado" forte (estilo física estatística).
- **B3** Formalizar o "cancelamento de caudas" (B3 do FINDINGS) como teorema:
  por que within domina e between→0 em misturas de distribuições de dois pontos.

## Frente C — Prêmio de risco / asset-pricing  ✅ C1+C2 FEITAS (2026-06-23) [dataset]
**Hipótese:** existe um prêmio de skewness ALÉM do nível mecânico do FLB, e os
parâmetros de preferência (CPT) são eles próprios invariantes.
> **C1+C2 concluídas** (Fases C1/C2 em `FINDINGS.md`): C1 = retorno = vig + FLB
> mecânico + resíduo; resíduo NÃO correlaciona com skewness (r=+0.11, IC inclui 0) ⇒
> sem prêmio por liga além do mecânico. C2 = ponderação TK γ=0.96 (inverse-S),
> **invariante temporal** (β≈0, Δ20a +0.006) e apertado entre ligas (sd 0.04).
> Artefatos: `skewlib/{premium,cpt}.py`, `analysis/{19_premium,20_cpt}.py`.
> **Pendente em C:** C3 (Kelly/staking ótimo sob a estrutura de skewness/CPT).
- **C1** Decompor retorno esperado em: margem (overround) + nível FLB mecânico +
  resíduo de mispricing. Quanto sobra de "prêmio" puro?
- **C2** Ajustar **Cumulative Prospect Theory** (Barberis-Huang / probability
  weighting) à curva FLB por liga; testar se os params de ponderação de
  probabilidade são invariantes no tempo e entre ligas (preferência estável).
- **C3** ✅ FEITA (2026-06-23, Fase C3): Kelly = 0% EV>0 após margem (sem
  crescimento, ecoa C1); termo de skew do azarão +0.60 vs +0.01 do favorito = o
  canal pelo qual o FLB sobrevive a ser EV-negativo. `analysis/33_kelly_staking.py`,
  `skewlib/staking.py`.

## Frente D — Microestrutura / formação de preço  ✅ D2+D3+D4 FEITAS (2026-06-23)
> **D2+D3+D4 concluídas** (Fases D2/D3/D4 em `FINDINGS.md`): D2 = sharp(Max) vs
> soft(Odd) — skew +0.218→+0.238 (Δ +0.020 uniforme, corr ligas +0.993, lei
> sobrevive −0.876); D3 = z de Shin 3.4% global, ≈margem (corr +0.999) e ortogonal
> à competitividade (−0.04); D4 = handicap asiático (150k jogos) p_fav 0.533 →
> skew −0.104 (ex-post −0.117), na identidade r=+0.80 — 3º mercado independente.
> Artefatos: `skewlib/microstructure.py`, `analysis/{26_sharp_soft,27_shin_z_series,28_asian_handicap}.py`.
- **D1 [novo dado] Drift abertura→fechamento** — FORA (precisa odds de abertura).
- **D2** ✅ Sharp vs soft (Odd* média vs Max* melhor preço).
- **D3** ✅ Shin z como série (liga/ano vs competitividade/overround).
- **D4** ✅ Mercado de handicap asiático como 3º teste da identidade.

## Frente E — Endurecer a derivação (teoria)  ✅ E1+E2 FEITAS (2026-06-23) [dataset]
> **E1+E2 concluídas** (Fases E1/E2 em `FINDINGS.md`): E1 = `S(σ_L)` por QUADRATURA
> do integral gaussiano (forma fechada, max|MC−exato|=0.0015), limite balanceado
> analítico `S₀=(1−2p₀)/√(p₀(1−p₀))` com `p₀=Φ(h−c)`, pico exato σ*=0.123, curva
> não-monótona; honesto sobre a não-analiticidade global (quinas de p_fav ⇒ a forma
> fechada é o integral, não série elementar); prevê 38 ligas r=+0.903 sem ruído.
> E2 = lei robusta à força (t-Student/skew-normal/uniforme): max|ΔS|≤0.032 vs sd-liga
> 0.051; `d=rᵢ−rⱼ` simétrico p/ força iid ⇒ só a cauda (kurtose de d) move, e pouco.
> Artefatos: `skewlib/model.py` (league_*_exact, smallsigma_*, force_diff, curve_*),
> `analysis/{21_closed_form,22_force_robustness}.py`. **Pendente:** E3.
- **E1** ✅ Forma fechada de S(σ_L) via integral gaussiano (quadratura) + expansão
  near-balance. (Era por simulação em `model.league_skew`.)
- **E2** ✅ Robustez da distribuição de força (t-Student / skew-normal / uniforme).
- **E3** ✅ FEITA (2026-06-23, Fase E3): calibração (h,c,σ) POR liga, cutoff de
  empate c endógeno (corr c↔taxa de empate +0.91; σ_L↔competitividade +0.87); a lei
  sobrevive (skew por liga r=+0.90). `model.calibrate_by_league`,
  `analysis/34_per_league_calibration.py`.

## Frente F — Dentro da liga / micro  ✅ F1+F2+F3 FEITAS (2026-06-23) [dataset]
> **F1+F2+F3 concluídas** (Fases F1/F2/F3 em `FINDINGS.md`): F1 = drift
> intra-temporada leve (+0.243→+0.229, shift −0.008 ~3–4× < sd-liga, previsto por
> p_fav subir no fim); F2 = M₃ por faixa de p_fav (favorito fraco +126%, forte −26%;
> skew jogo +0.47→−1.05 na identidade); F3 = clubes dominantes puxam skew negativa
> (Barcelona −1.10), corr(dispersão de Elo da liga, skew) = −0.60. Artefatos:
> `skewlib/intraleague.py`, `analysis/{29_intraseason,30_game_contribution,31_team_decomposition}.py`.
- **F1** ✅ Sazonalidade intra-temporada (controlada por liga).
- **F2** ✅ Contribuição por competitividade do jogo (decomposição do M₃ por p_fav).
  (Nota: "importância" via derby/rebaixamento exigiria classificação ao vivo; feito
  pela competitividade do jogo, que é o canal mecânico direto.)
- **F3** ✅ Decomposição por time (dominância de Elo → assinatura da liga).

## Frente G — Robustez adversarial  ✅ G1+G2+G3 FEITAS (2026-06-23) [dataset]
> **G1+G2+G3 concluídas** (Fases G1/G2/G3 em `FINDINGS.md`): G1 = de-vig de Shin
> calibrado quase perfeito (REL global 0.0000, sd entre ligas 0.0003) + skew
> invariante ao método/casa (∈[+0.224,+0.263], amplitude 0.039); G2 = painel
> balanceado estrito (15 ligas em todas as 21 temporadas) → série global sem
> tendência (β=−0.00013/ano, nível +0.243±0.014, confound de composição morto);
> G3 = block-bootstrap sobre temporadas → skew +0.236 IC95 [+0.232,+0.239], lei
> corr(skew,p_fav)=−0.90 IC95 [−0.922,−0.876]. Artefatos: `skewlib/adversarial.py`,
> `analysis/{23_devig_reliability,24_balanced_panel,25_block_bootstrap}.py`.
- **G1** ✅ De-vig confiável (reliability/Brier por liga/ano) + invariância de método/casa.
- **G2** ✅ Painel BALANCEADO estrito p/ a série GLOBAL (composição morta).
- **G3** ✅ Block-bootstrap sobre temporadas para IC dos números-título.

## Frente H — Experimentos naturais
- **H1** [novo dado] Mudanças de regra como choques de competitividade: adoção de
  3-pontos-por-vitória (datas por liga), VAR, mudança de formato/playoff. FORA (dado).
- **H2** ✅ FEITA (2026-06-23, Fase H2) [dataset]: MLS (USA, fechada) é a mais
  balanceada por Noll-Scully (1/38), skew no extremo balanceado (+0.16 vs +0.22 das
  abertas); resíduo da curva −0.06 (~1 sd). Suporta open-vs-closed; teste pleno pede
  + ligas fechadas (dado externo). `analysis/32_open_vs_closed.py`.

---

# 2ª RODADA — frentes novas no dataset congelado (2026-06-23)

> A 1ª rodada (A–H) está fechada. Estas frentes exploram veias do MESMO dataset
> ainda intocadas (gols `FT*`, intervalo `HT*`, estrutura de portfólio, cauda
> realizada), sem nenhum esporte ou dado externo. Prioridade por payoff×custo.

## Frente I — Validação cruzada do mecanismo (modelo de gols)  ✅ FEITA (2026-06-23)
> **Concluída** (Fase I): um Poisson de GOLS (ataque/defesa+mando por liga-temporada,
> Skellam→resultado) reproduz a lei. Entre 38 ligas: corr(p_fav Poisson, empírico)
> +0.972, corr(skew Poisson, empírico) +0.925; Poisson na curva do ordered-probit
> r=+0.85. Três modelos independentes (margem latente, gols-Poisson, mercado) na
> MESMA curva ⇒ mecanismo independente do modelo. `skewlib/goals.py`,
> `analysis/35_poisson_crossmodel.py`.

## Frente J — Chegada de informação: intervalo → fim (HT→FT)  ✅ FEITA (2026-06-23)
> **Concluída** (Fase J): a skewness do "resto do jogo" é a identidade na prob
> condicional ao placar do HT — favorito atrás q=0.14 skew +2.08, +2 gols q=0.95
> skew −3.91; calibração martingale |p0−q|=0.0035. O núcleo mecânico é DINÂMICO
> (vale a cada estado de info). `skewlib/inplay.py`, `analysis/36_inplay_resolution.py`.

## Frente K — Diversificação / portfólio  [dataset]
A skewness é fenômeno de aposta ÚNICA? Para N apostas (quase) independentes, a
skewness padronizada do retorno médio escala ~1/√N → uma banca diversificada de
favoritos é ~gaussiana, enquanto a variância não some. Implica: o viés/preferência
por skew importa para o apostador RECREATIVO (poucas apostas), não para o sindicato.
Quantificar com os retornos realizados (`ret_fav`).

## Frente L — Vantagem de casa secular vs invariância  [dataset]
A vantagem de casa caiu ao longo das décadas (e no choque COVID, W3). Traçar a HFA
por ano e mostrar que, apesar de a HFA se mover, a skewness fica invariante (depende
da dispersão de p_fav, não do nível do mando) — fecha o confound do lado do mando.

## Frente M — Risco de cauda realizado (VaR/CVaR/drawdown)  [dataset]
Lado prático: momentos realizados de ordem alta, VaR/CVaR e max drawdown das
estratégias (sempre-favorito vs sempre-azarão), conectando a skewness ao risco de
banca de fato. Atrai o leitor quant; usa `ret_fav`/`ret_dog`.

## Frente N — Entropia + estrutura de co-momento entre mercados  [dataset]
Índice alternativo de competitividade (entropia de Shannon da distribuição 1X2) e
sua relação com a skewness; e fator COMUM: a skewness do 1X2 e do O/U compartilham
um latente de competitividade da liga (co-skewness entre mercados)?

---

## Como estender (arquitetura)
Lógica nova → função em `skewlib/`, depois script fino `analysis/NN_*.py` que a
usa (NÃO duplicar lógica em script). Parâmetros só em `config.py`. Rodar:
`cd study && ./run.sh` (ou um bloco isolado com `PYTHONPATH=. python analysis/NN_*.py`).
Após mexer no dado/resultado, rodar `analysis/export_site_data.py` p/ atualizar o
site. Rigor: janelas não-sobrepostas p/ inferência, bootstrap p/ momento de 3ª
ordem, ADF+KPSS dupla, reportar sensibilidade.

## Sugestão de ordem (payoff×custo)
1. ~~**B1+B2** (multi-momento + colapso)~~ ✅ FEITA 2026-06-23 (Fases B1/B2).
2. ~~**C1+C2** (prêmio de skew + CPT invariante)~~ ✅ FEITA 2026-06-23 (Fases C1/C2).
3. ~~**E1+E2** (forma fechada + robustez de força)~~ ✅ FEITA 2026-06-23 (Fases E1/E2).
4. ~~**G1–G3** (robustez adversarial)~~ ✅ FEITA 2026-06-23 (Fases G1/G2/G3).
5. ~~**F1–F3 / D2–D4 / H2 / C3 / E3**~~ ✅ FEITA 2026-06-23 (micro/microestrutura/
   Kelly/calibração-por-liga/aberto-vs-fechado).

> **DATASET EXAURIDO** (2026-06-23): todas as frentes que rodam no arquivo congelado
> estão FEITAS (W·P·B·C·E·D·F·G·H2 — 29 fases; ver `docs/LINEAGE.md`). Restam só as
> que exigem **dado externo**: Frente A (tênis/cross-esporte), D1 (abertura→fechamento),
> H1 (mudanças de regra). Decisão Vitor: futebol no dataset congelado primeiro — cumprido.
