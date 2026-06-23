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

## Frente B — Estrutura de momentos / distribuição completa  ⭐ [dataset]
**Hipótese:** não só o 3º momento — a forma INTEIRA da distribuição implícita é
invariante após controlar competitividade.
- **B1** Estender `pooled_skew` → `pooled_moments` (var, skew, **kurtose**, e
  cumulantes 5–6). O ordered-probit (`model.py`) prevê TODOS os momentos; testar
  momentos 2–4 contra a curva derivada (invariância multi-momento > só skew).
- **B2** Colapso de distribuição: padronizar (z-score) os retornos por liga e
  testar se a distribuição padronizada é a MESMA entre ligas (KS/Anderson-Darling
  par-a-par) → "fato estilizado" forte (estilo física estatística).
- **B3** Formalizar o "cancelamento de caudas" (B3 do FINDINGS) como teorema:
  por que within domina e between→0 em misturas de distribuições de dois pontos.

## Frente C — Prêmio de risco / asset-pricing  ⭐ o "so what" econômico [dataset]
**Hipótese:** existe um prêmio de skewness ALÉM do nível mecânico do FLB, e os
parâmetros de preferência (CPT) são eles próprios invariantes.
- **C1** Decompor retorno esperado em: margem (overround) + nível FLB mecânico +
  resíduo de mispricing. Quanto sobra de "prêmio" puro?
- **C2** Ajustar **Cumulative Prospect Theory** (Barberis-Huang / probability
  weighting) à curva FLB por liga; testar se os params de ponderação de
  probabilidade são invariantes no tempo e entre ligas (preferência estável).
- **C3** Ligação com Kelly/staking ótimo: o que a estrutura de skewness implica
  para o crescimento ótimo de banca? (resultado prático, atrai quants.)

## Frente D — Microestrutura / formação de preço
- **D1 [novo dado] Drift abertura→fechamento** — a skewness implícita CONVERGE
  para o valor eficiente conforme a info chega? "Descoberta de preço" da
  assimetria. Precisa de odds de abertura (oddsportal/B365 opening).
- **D2 [dataset] Sharp vs soft** — usar `Odd*` (média do mercado, mais soft) vs
  `Max*` (melhor preço, ~sharp/arb) como proxies; a skewness diverge por tipo de
  casa? (W4 tocou; aprofundar com a estrutura de momentos).
- **D3 [dataset] Shin z como série** — `devig.shin` já dá z (fração de dinheiro
  informado). z por liga/ano/mercado correlaciona com competitividade? overround?
- **D4 [dataset] Mercado de handicap asiático** — `Handi*` permite um 3º mercado
  (além de 1X2 e O/U) para testar a identidade. AH é quase-binário com linha
  móvel → de-vig e skewness próprios.

## Frente E — Endurecer a derivação (teoria)  [dataset]
- **E1** Forma fechada de S(σ_L): hoje `model.league_skew` é por simulação.
  Derivar E[m₃(p)]/E[σ²(p)]^{3/2} analiticamente via integrais gaussianas em d.
- **E2** Robustez da distribuição de força: trocar N(0,σ²) por t-Student / força
  assimétrica; a lei sobrevive? (modelo hoje assume forças gaussianas).
- **E3** Cutoff de empate c endógeno por liga (ligas mais "empatadeiras"); refit
  e ver se a invariância muda. Calibrar (h,c,σ) POR liga, não só global.

## Frente F — Dentro da liga / micro  [dataset]
- **F1** Sazonalidade intra-temporada controlada por liga (início vs fim, conforme
  a classificação cristaliza). A skewness se move dentro da temporada?
- **F2** Contribuição por importância do jogo (derby, briga de rebaixamento, jogo
  morto) — competitividade no nível do JOGO prevê a contribuição de skew do jogo?
- **F3** Decomposição por time: clubes dominantes "puxam" a assinatura da liga?

## Frente G — Robustez adversarial  [dataset]
- **G1** De-vig não-paramétrico / consenso multi-casa (Nash 2018): o resíduo de
  Shin é estável? Reliability diagram + decomposição de Brier por liga/ano.
- **G2** Painel BALANCEADO estrito (só ligas presentes em todos os anos) para a
  série GLOBAL — mata 100% o confound de composição (P1 fez por-liga).
- **G3** Block-bootstrap sobre temporadas para IC de TODOS os números-título.

## Frente H — Experimentos naturais  [novo dado]
- **H1** Mudanças de regra como choques de competitividade: adoção de 3-pontos-
  por-vitória (datas por liga), VAR, mudança de formato/playoff → a skewness move?
- **H2** Liga aberta vs fechada: MLS (salary cap, sem rebaixamento — já apareceu
  com Noll-Scully/skew baixos) vs europeias abertas. Formalizar open-vs-closed.

---

## Como estender (arquitetura)
Lógica nova → função em `skewlib/`, depois script fino `analysis/NN_*.py` que a
usa (NÃO duplicar lógica em script). Parâmetros só em `config.py`. Rodar:
`cd study && ./run.sh` (ou um bloco isolado com `PYTHONPATH=. python analysis/NN_*.py`).
Após mexer no dado/resultado, rodar `analysis/export_site_data.py` p/ atualizar o
site. Rigor: janelas não-sobrepostas p/ inferência, bootstrap p/ momento de 3ª
ordem, ADF+KPSS dupla, reportar sensibilidade.

## Sugestão de ordem (payoff×custo)
1. **B1+B2** (multi-momento + colapso de distribuição) — barato, dataset, fortalece muito.
2. **A1** (tênis) — maior payoff de generalização; custo = 1 adaptador de I/O.
3. **C1+C2** (prêmio de skew + CPT invariante) — o ângulo econômico do paper.
4. **E1+E2** (forma fechada + robustez de força) — blinda a teoria.
5. **G1–G3** (robustez adversarial) — pré-submissão.
