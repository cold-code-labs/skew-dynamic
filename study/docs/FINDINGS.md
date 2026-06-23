# Estabilidade da Skewness em Mercados de Apostas de Futebol
## Resultados aprofundados — 6 frentes

**Amostra:** 205.435 jogos · 38 ligas · 2005–2025 · football-data mirror
**Estratégia base:** aposta unitária no favorito (menor odd), retorno ex-post.

---

## TESE CENTRAL (revisada e fortalecida)

> A skewness do mercado de apostas **não é um processo dinâmico — é um
> invariante estrutural**. Cada liga tem um nível de skewness próprio,
> fixo no tempo, determinado pela sua competitividade. A flutuação observada
> é ruído amostral puro, não memória de mercado. A assimetria é propriedade
> do gerador esportivo, exógena ao apreçamento das casas.

Evoluiu de "estável-com-memória" (rascunho v1) → **"constante estrutural +
ruído branco"** (confirmado por 3 testes independentes). E de **invariância de
skewness** → **invariância de FORMA** (Fases B1/B2): não só o 3º momento, mas a
distribuição implícita inteira (var/skew/kurtose) é função única da competitividade
— colapsa entre ligas quando se condiciona nela.

---

## BLOCO A — Robustez (o achado sobrevive aos confounds?)

| Configuração | ADF | KPSS | Ljung-Box | ACF(1) |
|---|---|---|---|---|
| baseline (overlap) | <0.001 | 0.10 | <0.001 | 0.74 |
| league-demeaned (overlap) | <0.001 | 0.10 | <0.001 | 0.74 |
| **não-overlap** | <0.001 | 0.10 | **0.71** | **−0.08** |
| league-demeaned não-overlap | <0.001 | 0.10 | 0.70 | −0.08 |

- **Estacionariedade: blindada.** Sobrevive a demeaning, não-overlap e janelas
  de 500 a 3000 jogos. ADF<0.001 e KPSS=0.10 em todas as 10 configs.
- **Persistência: era artefato.** O ACF=0.74 vinha 100% da sobreposição de
  janelas. Sem overlap → ruído branco (LB p=0.71). **Correção honesta vs v1.**
- Composição de liga **não** é confound: demeaning quase não move nada.
- sd cai monotonicamente com tamanho de janela → variação é erro amostral.

## BLOCO B — De onde vem a skewness?

**B1 — por estratégia:** skewness monotônica na improbabilidade da aposta.
favorito +0.23 · empate +1.27 · azarão +2.26 · "sempre fora" +2.40.
Retorno médio acompanha (favorito −4.8%, azarão −10.2%) = FLB clássico.

**B2 — favorite-longshot bias (a tabela-chave):** skewness desce monotonicamente
conforme o favorito fortalece, cruzando zero em p≈0.50:

| p_favorito | ret médio | skewness | win% |
|---|---|---|---|
| (0.40] | −7.5% | +0.59 | 36% |
| (0.45,0.50] | −4.7% | +0.19 | 45% |
| (0.55,0.60] | −3.5% | −0.22 | 56% |
| (0.70,1.0] | −1.6% | −1.19 | 77% |

**B3 — o mecanismo da estabilidade:** corr(força do favorito, variância)=**−0.90**
mas corr(força, skewness)=−0.21 e corr(variância, skewness)≈0. A variância é
sensível à composição; a skewness **não**, porque as contribuições das duas
caudas (favoritos fracos→+, fortes→−) se cancelam de forma estável.

## BLOCO C — A série é mesmo i.i.d.?

- Variance Ratio(2,4,8) = 0.94, 0.94, 1.00 (=1 → i.i.d.)
- AR(1) φ = −0.06, **não-significativo** (p=0.39), half-life ≈ 0
- **Conclusão:** ruído branco confirmado por 3 testes. Sem dinâmica temporal.

## BLOCO D — Cross-casa (odd média vs melhor odd) — 2º achado

| métrica | odd média | melhor odd |
|---|---|---|
| skewness | 0.229 | 0.242 |
| retorno médio | −4.75% | **−0.16%** |
| overround | 1.067 | 1.009 |

- **A margem da casa é majoritariamente spread entre casas.** Arbitrar odds
  recupera 4.6 p.p. de retorno; a margem "irredutível" é ~0.2%.
- **A skewness é invariante à casa:** corr temporal das duas séries = **0.984**.
  Casas competem na margem (nível); a skewness é exógena a essa competição.
- Separa apreçamento (margem, varia) de estrutura (skewness, fixa).

## BLOCO E — Heterogeneidade entre ligas (achado mais rico)

- Skewness **não** é universal: varia de 0.10 (Holanda) a 0.33 (Itália B), sd=0.06.
- **corr(previsibilidade da liga, skewness) = −0.83.** Quase determinística.
- Ligas com favoritos fortes (poucos dominam) → skewness baixa; ligas parelhas
  (2ªs divisões) → skewness alta.
- **Generalização:** cada liga tem skewness-invariante = f(competitividade).
  O mesmo mecanismo de B3 (escala intra-janela) reaparece entre ligas (escala
  cross-sectional). Um princípio único explica as duas escalas.
- BRA +0.18, ARG +0.31 — ligas sul-americanas no extremo competitivo/assimétrico.

## BLOCO F — Forense do blip 2012/13

- A única "quebra estrutural" em 20 anos era **artefato de amostragem**: o
  dataset saltou de 21→37 ligas em 2012 (entraram ARG, MEX, BRA, JAP, POL,
  ROM...), muitas de alta skewness, inflando a média da janela temporariamente.
- **Não havia evento de mercado.** Reforça a estabilidade real e valida o
  controle de composição.

---

## SÍNTESE PARA O PAPER

Três níveis de resultado, coesos sob um princípio:

1. **Cross-sectional:** FLB confirmado; skewness monotônica na improbabilidade.
2. **Temporal:** skewness é constante + ruído branco (sem dinâmica) — robusto.
3. **Estrutural:** o nível é f(competitividade da liga); estabilidade temporal
   decorre de a competitividade ser uma propriedade lenta (escala de décadas).

**Princípio unificador:** competitividade estrutural gera assimetria; como ela
muda devagar, a skewness é um invariante temporal. A margem das casas é
ortogonal a isso (afeta nível de retorno, não assimetria).

## Próximas frentes (não exploradas ainda)
- Drift abertura→fechamento: a skewness do movimento de preço (precisa de odds
  de abertura, dataset tem parcial).
- Sazonalidade intra-temporada controlada por liga (início vs fim).
- Testar invariância em outro esporte (basquete/tênis) — generalização externa.

---

# LOG DE FASES (rumo ao paper)

> Dataset congelado em `data/PROVENANCE.json` (sha256 `6905ca53…`, 205.435
> jogos ≥2005, 38 ligas, 2005-01→2025-06). Baseline reproduzida em
> `outputs/phase0_baseline.log`. Cada fase abaixo adiciona um bloco ao paper.

## Fase 0 — Reprodução + congelamento (2026-06-23)
Blocos 00–06 reproduzem `FINDINGS` exatamente contra o arquivo completo de 38
ligas. Bug corrigido em `06_league_hetero` (`tab.skew` colidia com
`DataFrame.skew()`). Dataset congelado por hash.

## Fase 1 / W1 — Skewness ex-ante e o núcleo mecânico (2026-06-23)
Objeto primário redefinido: **skewness implícita (de-vigada)** da aposta no
favorito, via modelo de **Shin** (z médio 3.4% de dinheiro informado;
overround 1.068). Fechada, sem ruído amostral.

- **Ex-ante ≈ ex-post.** Skew global ex-ante **+0.236** vs realizada **+0.230**
  → o objeto implícito reproduz o realizado; odds bem calibradas no agregado.
- **Decomposição (lei dos cumulantes totais) — assume o núcleo mecânico:**
  M3 = **+102.6% intra-jogo (Bernoulli/FLB)** − 2.6% covariância − 0.0%
  entre-jogos. A skewness de mercado é, a ~100%, a assimetria intra-jogo da
  distribuição de p — não artefato de pooling. `within_frac` ≈ 1.00 em **todas**
  as faixas de p_fav. Converte a crítica de "tautologia" na própria tese: a
  assimetria de risco É a imagem algébrica do FLB.
- **Cross-liga (objeto limpo):** corr(ex-ante, ex-post)=**+0.872**;
  corr(p_fav, skew)=**−0.900** — porém ainda circular (p vem das odds). Alvo
  do W2: reproduzir com competitividade **odds-free**.

Artefatos: `skewlib/devig.py`, `skewlib/exante.py`, `analysis/07_devig_exante.py`,
`outputs/exante_by_league.csv`.

## Fase 2 / W2 — Mecanismo odds-free: a lei não é tautológica (2026-06-23)
Competitividade medida por **Elo construído só de resultados** (sem odds; passo
cronológico multi-liga + mapa rating-diff→(P_H,P_D,P_A) por MNLogit calibrado
nos resultados — P(H) 0.444 = real 0.444, P(D) 0.264 = real 0.264).

- **Odds e Elo medem a MESMA estrutura:** corr(elo_pfav, p_fav_dv)=**+0.909**
  [0.83,0.97]. As odds apenas *leem* a competitividade esportiva (eficiência
  estrutural) — não a criam.
- **A lei skewness=f(competitividade) SOBREVIVE sem odds:**
  skew ~ upset_rate **+0.826** [0.71,0.91] · skew ~ elo_entropy **+0.719**
  [0.50,0.89] · skew ~ elo_pfav **−0.748** · skew ~ elo_disp **−0.731**. Todas
  com IC95% longe de zero. Referência circular (odds p_fav): −0.900.
- **Atenuação −0.90→−0.75/+0.83 = ruído de medida** no proxy Elo (errors-in-
  variables), não evidência contra a lei: corr(elo,odds)=0.91 mostra que medem
  o mesmo latente. A assimetria de risco é **herdada da estrutura competitiva**
  da liga, não do apreçamento.

Artefatos: `skewlib/elo.py`, `skewlib/stats.py` (bootstrap_corr, ols),
`analysis/08_mechanism_elo.py`, `outputs/mechanism_elo.csv`.

## Fase 3 / W3 — Invariância temporal: painel liga×temporada (2026-06-23)
Tratar (liga,temporada) como unidade dissolve o confound de composição do
Bloco F por construção. 638 obs, 38 ligas, 2005–2025.

- **Sem tendência secular:** FE de liga + ano linear (SE cluster por liga):
  β=**+0.00015/ano** (p=0.73, IC95% [−0.0007,+0.0010]). Deriva em 20 anos
  ≈ +0.003 vs sd entre-ligas 0.052 → nula.
- **Domínio estrutural:** sd between-liga **0.052** vs within-liga 0.034;
  ICC=**0.70**. Descontando o ruído amostral (SE bootstrap 0.019), a flutuação
  temporal *real* é sd≈0.028 — pequena, **sem tendência e revertendo à média**
  (coerente com o ruído branco do Bloco C). O invariante de liga domina ~2:1.
- **Por liga:** desvios idiossincráticos e minúsculos (|slope| médio
  0.0024/ano; quebras raras, provável sobre-segmentação do PELT em séries de
  ~20 pontos). Nenhum regime market-wide.
- **Vinheta COVID (experimento natural):** estádios vazios 2020 derrubaram a
  vitória do mandante (0.447→0.417). A lei prevê: HFA↓ → mais paridade →
  skewness↑. Observado: z médio **+0.42** SD, **21/33 ligas com z>0**. O único
  choque exógeno de competitividade em 20 anos moveu a skewness na direção
  prevista — corrobora a *causa* sem violar a invariância secular.

Artefatos: `skewlib/panel.py`, `analysis/09_panel_temporal.py`,
`outputs/panel_league_season.csv`.

## Fase 4 / W5 — Mercado binário over/under 2.5: identidade fora do 1X2 (2026-06-23)
148.261 jogos com odds O/U 2.5 (de-vig Shin; overround 1.067, z **0.067** — mais
dinheiro informado que no 1X2). Calibração impecável: over real 0.490 =
p_over de-vigada 0.492.

- **Mesma identidade, mercado diferente:** aposta no lado favorito → skew
  ex-ante **−0.210** (within intra-jogo **99.6%**), ex-post −0.217. A fórmula
  fechada (1-2p)/√(p(1-p)) bate exatamente per-match (max|dif|=0). Por faixa de
  p, ex-ante e ex-post andam colados (p=0.52→−0.09; p=0.74→−1.05).
- **Conclusão:** o núcleo mecânico do W1 **não** é artefato da estrutura de 3
  vias do 1X2 — vale num mercado binário de gols. within≈100% se replica.

Artefatos: `skewlib/overunder.py`, `analysis/10_overunder.py`, `outputs/overunder.csv`.

## Fase 5 / W4 — Margem ortogonal + robustez ao de-vig (2026-06-23)
- **Margem vs estrutura (odds média vs máxima, 202.760 jogos):** tomar o melhor
  preço do mercado colapsa o overround **1.067→1.009** (retorno −4.8%→~0) mas a
  skewness ex-ante quase não anda: **+0.236→+0.254** (corr p_fav por jogo
  **0.996**). A casa compete na MARGEM (nível), não na assimetria — margem
  largamente ortogonal à skewness.
- **Robustez ao método de de-vig:** skew global 0.224 (power) / 0.236 (shin) /
  0.263 (mult) — ±8% no nível; mas a **lei cross-liga é invariante**:
  corr(p_fav,skew) = −0.906 / −0.900 / −0.891. O achado estrutural não é
  artefato da escolha de de-vig.

Artefatos: `skewlib/exante.py` (market_skew), `analysis/11_margin_robustness.py`.

## Fase P1 — Reframe: invariância INTRA-REGIME (2026-06-23)
A literatura (Lee & Fort 2012; Basini 2023; ver `docs/LITERATURA.md`) acha
quebras de regime **reais** na competitividade da EPL ligadas a choques
institucionais (Champions League 94/95, Bosman 95, desigualdade de receita
~2003) — **todos anteriores** ao recorte ≥2005. Reposicionamos a tese de
"constante atemporal" para **baseline estrutural específico-da-liga, estável
DENTRO do regime competitivo**.

- **Teste de quebras intra-janela (PELT conservador):** só **1 quebra em 38
  ligas** (F1/França 2020 = COVID, salto −0.064); **nenhum ano comum** de quebra
  (máx 1 liga/ano) → sem regime market-wide em 2005–2025.
- **EPL (E0):** **0 quebras** no recorte; média 0.165, sd 0.027 — estável
  intra-regime, coerente com os choques de regime da EPL serem pré-2005.
- **Conclusão:** 2005–2025 ≈ regime moderno único; "sem tendência" (β≈0) é
  **invariância intra-regime**, não atemporalidade absoluta. Confronta Lee &
  Fort/Basini de frente e os usa como moldura — a contra-evidência vira aliada.

Artefatos: `skewlib/panel.py` (league_breaks), `analysis/13_regimes.py`.

## Fase P2 — CB canônico odds-independente da classificação (2026-06-23)
Hardening da W2 com os índices size-robust da literatura (Gini fora, Utt & Fort
2002), computados da **classificação final** (resultados, sem odds nem Elo) —
ataque mais forte à circularidade.

- **Lei reproduzida, sinal previsto (desequilíbrio → skewness↓):**
  skew ~ Noll-Scully **−0.625** [−0.83,−0.36] · ~ HHI* (Owen 2007) −0.593 · ~
  Theil/GE1 (Borooah-Mangan) −0.478. Todas IC95% excluem zero.
- **Escada de errors-in-variables limpa:** odds (circular) −0.90 > Elo
  (match-level) +0.83 > classificação (season-level) 0.48–0.63. Quanto mais perto
  do p-por-jogo, mais forte o corr — o latente é forte, medido por proxies de
  fidelidade variável.
- Time a time bate: N1/EPL (NS~1.84, dominância) skew baixa; MLS (NS 1.13, salary
  cap) e Argentina (NS 1.20) skew alta. Mecanismo visível na classificação.

Artefatos: `skewlib/balance.py`, `analysis/14_balance_indices.py`,
`outputs/balance_indices.csv`.

## Fase P3 — Derivação formal: skewness = f(dispersão de força) (2026-06-23)
A lei vira **consequência de um modelo**, não ajuste. Ordered-probit
(Goddard-Asimakopoulos 2004; Koning 2000): força r~N(0,σ_L²), margem latente
y*=d+h+ε, cutoffs ±c → (A,D,H); favorito p=max; sob odds justas a skewness
agrupada S(σ_L)=E[m₃(p)]/E[σ²(p)]^{3/2}.

- **Calibração** (taxas pooled H 0.444 / D 0.264 / p_fav 0.499): h=0.220,
  c=0.373, σ_ref=0.291.
- **Validação 1ª→3ª ordem:** o modelo prevê a skewness de cada liga a partir só
  do mean p_fav: **corr(previsto, observado)=+0.904**, RMSE **0.024** (< metade
  do sd entre ligas 0.051). As 38 ligas caem na curva derivada (F5).
- **Leitura:** a lei skewness~competitividade é consequência analítica do modelo
  de força do esporte + a identidade FLB — fecha "o gap" (ninguém amarrou 3º
  momento de odds a um modelo de força). Curva teórica cobre skew −0.03..+0.30
  (p_fav 0.44..0.76), bracketando o empírico.

Artefatos: `skewlib/model.py`, `analysis/15_model.py`, `outputs/fig/f5_model.png`.

## Fase P4 — Estabilidade do FLB no tempo (Angelini confound) (2026-06-23)
Angelini & De Angelis (2019) acham FLB enfraquecendo em dados europeus recentes;
um viés em movimento poderia fingir invariância de skewness. Testado 2005–2025:

- **FLB sem tendência significativa:** ret_dog (barômetro) corr(ano)=+0.27
  [−0.23,+0.67] (IC inclui 0; leve hint na direção de Angelini, não-significativo);
  flb_spread corr −0.02; calib_err corr −0.13. Δ20a do spread ≈ −0.002.
- **Calibração ano a ano intacta:** |skew_exante − skew_expost| médio = **0.015**;
  erro de calibração do favorito ∈ [−0.004,+0.012] todo ano.
- **Conclusão:** a invariância de skewness **não** é artefato de um FLB driftando
  — o viés é estável e a skewness é mecânica na distribuição de p, robusta a
  micro-drift de calibração.

Artefatos: `skewlib/decompose.py` (flb_by_year), `analysis/16_flb_stability.py`,
`outputs/flb_by_year.csv`.

## Fase B1 — Invariância de FORMA: não só o 3º momento (2026-06-23)
Generalização da decomposição de momentos da mistura (lei dos momentos totais) para
var/skew/**kurtose**/5ª–6ª ordem, e teste de cada um contra a curva derivada do
ordered-probit (P3 fez só p/ a skew). Object: a distribuição implícita inteira é
invariante após controlar competitividade?

- **Toda a forma é MECÂNICA (intra-jogo), não pooling:** a fração `within` (parte
  vinda da assimetria/forma intra-jogo, o FLB, vs dispersão entre jogos) é ≈1 em
  **todas as ordens** — m2 +1.000, m3 +1.026, m4 +1.006, m5 +1.026, m6 +1.016. A
  forma inteira é a imagem algébrica da distribuição de p, não artefato de mistura.
- **O modelo de força prevê a forma inteira pelo p_fav:** corr(previsto, observado)
  entre as 38 ligas = **var +0.987 · skew +0.904 · exkurt +0.890**. Skew e exkurt
  (padronizados, scale-free) batem em **nível e ordenação**; a var segue a ordenação
  (r=0.99) com offset de escala do overround (odds reais o<1/p). Global: skew
  **+0.236** (boot SE 0.001), exkurt **−1.683** (forte caudas-curtas, esperado de
  mistura de Bernoullis), std5 +0.85, std6 +2.18.
- **Conclusão:** "invariância de skewness" se fortalece para **invariância de FORMA**
  — a distribuição implícita inteira é uma função única da competitividade da liga.

Artefatos: `skewlib/exante.py` (pooled_moments, per_match_central_moments),
`skewlib/model.py` (league_moments, curve_moments), `analysis/17_moments.py`,
`outputs/moments_by_league.csv`, `outputs/fig/f6_moments.png`.

## Fase B2 — Colapso de distribuição: forma = f(competitividade) (2026-06-23)
Teste tipo "data collapse" (física estatística): a forma é universal, ou colapsa
sob a competitividade? KS sobre o retorno do favorito (efeito = estatística KS, pois
o p-valor satura com n grande).

- **Sem controlar competitividade** (retornos z-scored por liga, 38 ligas): KS
  par-a-par com estatística mediana **0.474**, 100% dos pares rejeitam — a forma
  padronizada **difere** entre ligas (a skew varia), logo não é universal.
- **Controlando competitividade** (one-vs-rest dentro de 8 faixas de p_fav, 264
  testes): estatística KS mediana **0.059** — **queda de 87%**. Dentro de cada faixa
  as ligas ficam quase indistinguíveis; a identidade da liga não acrescenta nada
  além da competitividade.
- **Conclusão:** a distribuição **colapsa** quando se condiciona na competitividade —
  fato estilizado de que a forma é função (única) da competitividade, não da liga.

Artefatos: `skewlib/collapse.py`, `analysis/18_collapse.py`,
`outputs/collapse_ks.csv`, `outputs/fig/f7_collapse.png`.

## Fase C1 — Prêmio de skewness: nada além do FLB mecânico (2026-06-23)
Decomposição do retorno do favorito (identidade exata) em margem + nível FLB
mecânico + resíduo, e teste do resíduo contra a skewness implícita por liga.

- **Retorno = margem + FLB (calibração):** global ret −4.82% = **vig −4.97%** +
  **FLB +0.15%**. A perda é quase toda margem; o FLB do favorito é pequeno e
  positivo (favoritos levemente subapreçados). Curva mecânica do FLB monotônica em
  p_fav (favoritos fracos contribuem −, fortes +).
- **Sem prêmio de skewness por liga ALÉM do mecânico:** corr(resíduo, skew) =
  **+0.11** [−0.20,+0.38] (IC inclui 0); corr(FLB total, skew) −0.04; corr(vig,
  skew) −0.29. O resíduo de mispricing não acompanha a skewness da liga — a casa
  não deixa prêmio extra atrelado à assimetria. Coerente com a margem ortogonal (W4).
- **Conclusão:** o "prêmio de skewness" é inteiramente o FLB mecânico (entre tipos
  de aposta, já em W1/Bloco B); no nível da liga não sobra prêmio puro — o
  apreçamento é eficiente até a margem + o viés mecânico.

Artefatos: `skewlib/premium.py`, `analysis/19_premium.py`,
`outputs/return_decomp.csv`, `outputs/fig/f8_premium.png`.

## Fase C2 — A preferência (CPT) é ela própria invariante (2026-06-23)
Ajuste da ponderação de probabilidade de Tversky-Kahneman `w(p)=p^γ/(p^γ+(1−p)^γ)^{1/γ}`
à curva de calibração (implícito PROPORCIONAL `q` vs acerto objetivo `π`; o de-vig de
Shin apagaria o viés a medir, então usa-se o proporcional).

- **Inverse-S confirmado (γ<1 = FLB):** γ global **0.958**; calibração revela o viés
  (azarão q 0.101 vs π 0.086 = superposto; favorito q 0.711 vs π 0.743 = subposto).
- **γ é um invariante TEMPORAL:** por temporada γ médio 0.955, sd 0.020, tendência
  **β=+0.0003/ano** (r=+0.08, Δ20a ≈ +0.006) — **sem drift em 20 anos**. A preferência
  de ponderação é estável no tempo, espelhando a invariância da skewness (e o FLB
  estável do P4).
- **Quase invariante entre ligas:** γ médio 0.945, sd **0.040**, range [0.85,1.00] —
  apertado. Mostra associação leve com a competitividade (corr(γ,p_fav) −0.45
  [−0.74,−0.10]), nuance honesta (pode refletir a faixa de p amostrada por liga),
  não uma quebra da estabilidade temporal.
- **Conclusão:** o parâmetro de preferência por trás do FLB é uma constante
  estrutural estável (não um processo) — a invariância vale também do lado da
  preferência, não só da assinatura de risco.

Artefatos: `skewlib/cpt.py`, `analysis/20_cpt.py`, `outputs/cpt_by_league.csv`,
`outputs/cpt_by_season.csv`, `outputs/fig/f9_cpt.png`.

## Fase E1 — Forma fechada de S(σ_L): a derivação sai do Monte Carlo (2026-06-23)
O P3/bloco 15 traça a lei skewness=f(competitividade) por SIMULAÇÃO sobre a força
`d`. Aqui mostramos que a esperança é um INTEGRAL gaussiano 1-D em `d` e o
avaliamos por QUADRATURA — a forma fechada de `S(σ_L)=E[m₃(p_fav(d))]/E[σ²(p_fav(d))]^{3/2}`,
`d~N(0,2σ_L²)`, determinística e sem ruído de MC.

- **A quadratura reproduz o MC, sem ruído:** max|MC−exato| = **0.0015** (com
  n=4·10⁵; é a magnitude do próprio ruído de MC), médio 0.0006, em toda a grade de
  σ_L. A curva teórica vira exata e suave — a "derivação por simulação" passa a ser
  derivação fechada.
- **Limite balanceado em forma fechada:** `S(σ_L→0) = (1−2p₀)/√(p₀(1−p₀)) = +0.2449`,
  com `p₀=Φ(h−c)=0.4392` (o favorito de equilíbrio = mandante). É a identidade por
  jogo avaliada em p₀ — o intercepto da lei sai analítico. A curvatura líder
  `S₂=+8.44>0` (a skew SOBE ao sair do equilíbrio), válida p/ σ_L≲0.1.
- **A curva NÃO é monótona (caracterização exata):** côncava, com **pico em σ*=0.123
  (S_max=+0.304, p_fav*=0.446)** e zerando em σ_L≈1.09 (favorito forte ⇒ skew→0 e
  vira negativa). Corrige o "monótona" do docstring antigo.
- **Honestidade matemática:** `p_fav(d)=max(p_H,p_D,p_A)` tem QUINAS onde o favorito
  troca → `S(σ_L)` é C^∞ mas **não-analítica global** (a série de Taylor diverge além
  do regime near-balance, confirmado numericamente). A forma fechada legítima é o
  integral (quadratura), não uma série elementar; a expansão S₀+S₂σ² é a âncora
  analítica local.
- **Prevê as 38 ligas pela curva fechada:** corr(previsto,observado) = **+0.903**,
  RMSE 0.024 — idêntico ao bloco 15 por MC (r=0.904), agora sem reamostragem.
- **Conclusão:** a lei skewness=f(competitividade) é uma consequência fechada do
  modelo de força + FLB, derivada do integral gaussiano, não um ajuste nem um
  artefato de simulação.

Artefatos: `skewlib/model.py` (league_moments_exact, league_skew_exact,
mean_pfav_exact, smallsigma_coeffs/skew, fav_switch_points, curve_exact),
`analysis/21_closed_form.py`, `outputs/closed_form_curve.csv`,
`outputs/fig/f10_closed_form.png`.

## Fase E2 — Robustez da distribuição de força (2026-06-23)
O modelo assume força gaussiana, `r~N(0,σ_L²)`. A lei sobrevive se a força for
cauda-pesada (t-Student), assimétrica (skew-normal) ou de suporte limitado
(uniforme)? Predição teórica: a diferença de força `d=rᵢ−rⱼ` é **simétrica p/
qualquer força iid** — a assimetria da força não pode enviesar a lei; só a CAUDA
(kurtose de `d`) pode mover algo.

- **A teoria bate:** exc.kurt(d) = normal 0.0, t₅ +2.8, **t₃ +42.6** (cauda
  pesadíssima), skew-normal ±0.3, uniforme −0.6. skew(d)≈0 em TODAS (incl. as
  skew-normais) — a força assimétrica gera diferença simétrica.
- **A curva skew×competitividade quase não se move:** reparametrizando pela
  competitividade observável (mean p_fav) e comparando à gaussiana, max|ΔS| =
  t₅ **0.017**, t₃ **0.032**, skew-normal ±0.012, uniforme 0.011 — todos abaixo do
  sd entre ligas (0.051). O deslocamento escala com a CAUDA de `d` (t₃ é o maior),
  não com sua assimetria (skew-normal cola na gaussiana, como previsto).
- **No ponto operacional do futebol** (p_fav=0.499): skew ∈ [+0.223,+0.250],
  amplitude entre famílias = **0.027** (pequena perante o efeito da competitividade,
  que varre +0.30→−0.02).
- **Conclusão:** a lei é **geometria da mistura**, não da hipótese gaussiana —
  robusta a caudas pesadas e a assimetria de força. A gaussianidade é conveniência,
  não premissa carregando o resultado.

Artefatos: `skewlib/model.py` (force_diff, curve_family), `analysis/22_force_robustness.py`,
`outputs/force_robustness.csv`, `outputs/fig/f11_force_robustness.png`.

## Fase G1 — De-vig confiável e invariante (2026-06-23)
Robustez adversarial: o de-vig de Shin é confiável e a skewness não é artefato do
método? Reliability diagram + decomposição de Brier (Murphy: BS=REL−RES+UNC) do
favorito por liga/ano, e skewness sob 5 de-vigs/casas.

- **De-vig calibrado quase perfeitamente:** acerto do favorito 0.501 vs prob média
  0.499; **REL (erro de calibração) global = 0.0000**. Brier 0.236 = REL 0.000 −
  RES 0.014 + UNC 0.250.
- **REL pequeno e homogêneo:** entre 32 ligas média 0.0005 (sd 0.0003, max 0.0014);
  entre 21 temporadas média 0.0002 (sd 0.0001). Nenhuma liga/ano mal calibrado — o
  resíduo do de-vig é estável (não há viés escondido que produza a assimetria).
- **Skewness invariante ao método/casa:** shin·odd +0.236, shin·max +0.254,
  mult +0.263, power +0.224, consenso multi-casa +0.252 — amplitude **0.039**,
  todos positivos. Estende W4: o achado não depende do de-vig nem da casa.
- **Conclusão:** a skewness não é fabricada pelo de-vig; a assimetria implícita é
  bem calibrada contra os resultados e robusta à escolha de método.

Artefatos: `skewlib/adversarial.py` (fav_won, reliability, brier_decomp,
reliability_by, skew_by_devig), `analysis/23_devig_reliability.py`,
`outputs/reliability_by_league.csv`, `outputs/fig/f12_reliability.png`.

## Fase G2 — Painel balanceado estrito (composição morta) (2026-06-23)
A série GLOBAL de skewness refeita usando SÓ as ligas presentes em todas as 21
temporadas (15 ligas: B1,D1,D2,E0–E3,F1,F2,I1,I2,N1,SP1,SP2,T1) — mata 100% o
confound de composição que P1 atacou por-liga.

- **Sem tendência com cesta fixa:** β = **−0.00013/ano** (r=−0.06, Δ20a −0.003) na
  série balanceada vs −0.00009 na cheia; KPSS p=0.10 (estacionária). Nível médio
  **+0.243 (sd 0.014)** — apertadíssimo.
- **Conclusão:** a invariância temporal NÃO vem de a cesta de ligas mudar ano a ano;
  com o núcleo fixo a série global continua plana. O "sem drift" é real.

Artefatos: `skewlib/adversarial.py` (balanced_leagues, global_series_balanced),
`analysis/24_balanced_panel.py`, `outputs/balanced_global_series.csv`,
`outputs/fig/f13_balanced_panel.png`.

## Fase G3 — IC por block-bootstrap sobre temporadas (2026-06-23)
ICs honestos reamostrando TEMPORADAS inteiras (com reposição), respeitando a
dependência intra-ano que a reamostragem de jogos quebraria.

- **Skewness global +0.236**, IC95 **[+0.232, +0.239]** (SE 0.0019) — exclui 0 com
  folga.
- **Lei estrutural corr(skew_liga, p_fav_liga) = −0.900**, IC95 **[−0.922, −0.876]**
  (SE 0.011) — a relação skewness↔competitividade sobrevive à reamostragem de anos.
- **Retorno do favorito −4.82%**, IC95 [−5.37%, −4.43%].
- **Conclusão:** os números-título carregam IC por reamostragem de temporadas; o
  sinal e a magnitude não dependem de uma janela específica de anos.

Artefatos: `skewlib/adversarial.py` (season_block_bootstrap, stat_global_skew,
stat_league_corr), `analysis/25_block_bootstrap.py`.

## Fase D2 — Sharp vs soft: a margem é ortogonal também na melhor odd (2026-06-23)
A skewness diverge entre a odd MÉDIA do mercado (Odd*, soft) e a MELHOR odd
(Max*, ~sharp/arb)? Por liga.

- **Melhor preço quase zera a margem:** overround soft 1.069 → sharp 1.008.
- **Skew mal se move e uniformemente:** soft +0.218 → sharp +0.238 (Δ médio
  **+0.020**, sd 0.006). corr(skew_soft, skew_sharp) entre ligas = **+0.993** — a
  ordenação das ligas é idêntica; a **lei estrutural sobrevive na sharp**
  (corr(skew_sharp, p_fav) = −0.876).
- **Conclusão:** tirar a margem desloca a skew pouco e de forma uniforme; a casa
  compete em margem, não em assimetria (aprofunda W4) — a lei é invariante ao livro.

Artefatos: `skewlib/microstructure.py` (skew_by_book_league),
`analysis/26_sharp_soft.py`, `outputs/sharp_soft_by_league.csv`,
`outputs/fig/f14_sharp_soft.png`.

## Fase D3 — z de Shin (dinheiro informado) como série (2026-06-23)
z é subproduto do de-vig de Shin: a fração do book atribuída a insiders. z por
liga/ano, sua estabilidade e relação com competitividade/overround.

- **z baixo e apertado:** global 0.034 (3.4% de dinheiro informado no 1X2); entre
  38 ligas média 0.035, sd 0.004, range [0.023, 0.042].
- **z é essencialmente a margem reparametrizada:** corr(z, overround) = **+0.999**
  (quase tautológico no modelo de Shin — z é monótono no booksum). O útil é a
  **ortogonalidade à competitividade**: corr(z, p_fav) = −0.04 [−0.37, +0.30] —
  o conteúdo informacional não dirige a lei de skewness.
- **No tempo:** leve compressão (β=−0.0009/ano, Δ20a −0.019), espelhando a queda
  suave de margem; magnitude pequena.
- **Conclusão:** o dinheiro informado precificado é uma constante estrutural baixa,
  ligada à margem e ortogonal à competitividade — consistente com a invariância.

Artefatos: `skewlib/microstructure.py` (shin_z_frame, z_by),
`analysis/27_shin_z_series.py`, `outputs/shin_z_by_league.csv`,
`outputs/fig/f15_shin_z.png`.

## Fase D4 — Handicap asiático: a identidade num 3º mercado (2026-06-23)
Além de 1X2 (W1) e O/U 2.5 (W5), o AH é um mercado de 2 vias com linha MÓVEL que
equilibra o jogo para ~50/50. Teste mais nítido da identidade num regime de p_fav
diferente.

- **Linha equilibra p/ ~0.5:** 150.003 jogos com AH válido, p_fav médio **0.533**
  (vs 0.44 no 1X2). overround AH 1.044.
- **Mesma identidade, sinal oposto:** skew ex-ante AGRUPADA = **−0.104** (within-match
  102.7% = mecânico), pois p_fav>0.5 (favorito cobre com frequência ⇒ skew negativa)
  — espelho do 1X2 (+0.236, p_fav<0.5). Ex-post (70.965 liquidados) **−0.117** ≈
  ex-ante −0.112.
- **Por liga na curva:** skew_ah vs identidade (1−2p)/√(p(1−p)) no p_fav do AH →
  **r=+0.80**.
- **Conclusão:** um TERCEIRO mercado independente confirma o núcleo mecânico — a
  skewness é função de p (o sinal é fixado por qual lado de 0.5 o favorito cai), não
  artefato da estrutura de 3 vias do 1X2.

Artefatos: `skewlib/microstructure.py` (prep_ah, ah_league),
`analysis/28_asian_handicap.py`, `outputs/asian_handicap_by_league.csv`,
`outputs/fig/f16_asian_handicap.png`.

## Fase F1 — Sazonalidade intra-temporada: invariância vale dentro do ano (2026-06-23)
A skewness se move do início ao fim da temporada (Ago→Jul, terços por data)?

- **Drift LEVE e previsto:** global por fase +0.243 → +0.235 → +0.229 (amplitude
  **0.015**); p_fav sobe 0.494 → 0.503 (favoritos um pouco mais fortes no fim, com a
  classificação cristalizando). Δskew(fim−início) por liga: média **−0.008**, IC95
  [−0.013, −0.0015] (exclui 0 por pouco).
- **Conclusão:** existe uma cristalização pequena — mas ~3–4× menor que o sd entre
  ligas (0.05) e **prevista pela própria lei** (mais p_fav ⇒ menos skew). A
  invariância vale também DENTRO da temporada, a menos desse drift mínimo.

Artefatos: `skewlib/intraleague.py` (add_season_phase, skew_by_phase,
phase_shift_by_league), `analysis/29_intraseason.py`,
`outputs/intraseason_shift_by_league.csv`, `outputs/fig/f17_intraseason.png`.

## Fase F2 — Que jogos carregam a skewness (cancelamento de caudas) (2026-06-23)
Decomposição do 3º momento agrupado por faixa de competitividade do JOGO (p_fav):
quais jogos contribuem a assimetria.

- **Lei no nível do jogo:** skew por faixa vai de **+0.465** (p_fav 0.39, favorito
  fraco) a **−1.055** (p_fav 0.73, favorito forte) — exatamente a identidade
  (1−2p)/√(p(1−p)). Jogos de favorito FRACO (p<0.5) somam **+126%** do M₃; favorito
  FORTE (p>0.5) **−26%**.
- **Conclusão:** a skewness da liga é a soma líquida de contribuições que o
  cancelamento de caudas quase zera; a competitividade no nível do JOGO fixa o sinal
  e a magnitude de cada contribuição — a lei macro emerge do micro.

Artefatos: `skewlib/intraleague.py` (m3_contribution_by_bin),
`analysis/30_game_contribution.py`, `outputs/m3_contribution_by_bin.csv`,
`outputs/fig/f18_game_contribution.png`.

## Fase F3 — Decomposição por time: a assinatura vem da dispersão de força (2026-06-23)
Por clube: dominância (Elo médio) vs skewness média dos jogos que disputa.

- **Clubes dominantes puxam p/ skew negativa:** Barcelona (Elo 1983, favorito 97%)
  skew dos jogos **−1.10**, Bayern −1.09, Real Madrid −0.90; clubes fracos (Lahti
  Elo 1182) **+0.06**. corr(Elo, skew dos jogos) = **−0.44** [−0.53,−0.34].
- **A lei, vista por dentro:** corr(dispersão de Elo da liga, skew da liga) =
  **−0.60** [−0.77,−0.42] — ligas com mais super-clubes têm skew mais baixa.
- **Conclusão:** a assinatura de skew da liga é função da sua dispersão de força no
  nível dos TIMES — a versão micro de skewness=f(competitividade).

Artefatos: `skewlib/intraleague.py` (team_long, team_dominance),
`analysis/31_team_decomposition.py`, `outputs/team_dominance.csv`,
`outputs/fig/f19_team_decomposition.png`.

## Fase H2 — Liga aberta vs fechada: a MLS na lei (2026-06-23)
A MLS (USA) é a única liga FECHADA da amostra (salary cap, draft, sem
rebaixamento), desenhada para comprimir a dispersão de força; as europeias são
abertas. Predição: estrutura fechada ⇒ mais competitividade ⇒ skew balanceada.

- **MLS é a mais balanceada por medida estrutural:** Noll-Scully **1.13, rank 1/38**
  (a mais competitiva da amostra) — exatamente o que cap + sem-rebaixamento preveem.
  Skew ex-ante **+0.162**, abaixo da média das abertas (+0.219); p_fav 0.503.
- **Na curva, com nuance honesta:** resíduo vs a lei das abertas −0.06 (~1 sd) — a
  MLS fica no extremo competitivo/balanceado, consistente com a teoria open-vs-closed.
- **Conclusão:** a liga fechada não quebra a lei — sua estrutura aperta a
  competitividade e a skewness segue para o balanceado. Não é teste nítido (1 só liga
  fechada na amostra; pleno exige mais ligas fechadas = dado externo).

Artefatos: `analysis/32_open_vs_closed.py`, `outputs/open_vs_closed.csv`,
`outputs/fig/f20_open_vs_closed.png`.

## Fase C3 — Kelly/staking: o crescimento sob a estrutura de skewness (2026-06-23)
O que a assimetria implica para o crescimento ótimo de banca?

- **Kelly manda NÃO apostar:** sob a margem real, **0.0%** das apostas têm EV>0 (f*=0
  em todas) — após a vig não há crescimento a extrair (ecoa a eficiência do C1).
- **A skewness é o canal do FLB:** decompondo o log-crescimento (g ≈ μ − σ²/2 +
  m₃/3) a uma fração fixa, o termo de SKEWNESS do azarão é **+0.60** (×1e3) vs **+0.01**
  do favorito — a assimetria positiva compensa parte do EV negativo no
  crescimento/utilidade. É o canal pelo qual a preferência por skew (FLB) sobrevive a
  ser EV-negativa.
- **Conclusão:** a estrutura de skewness não abre crescimento (mercado eficiente),
  mas explica quantitativamente por que o apostador de azarão paga EV em troca de
  assimetria — o prêmio de skewness em termos de crescimento/utilidade.

Artefatos: `skewlib/staking.py` (kelly_fraction, growth_rate, moment_growth_terms),
`analysis/33_kelly_staking.py`, `outputs/fig/f21_kelly.png`.

## Fase E3 — Calibração por liga (cutoff de empate endógeno) (2026-06-23)
Calibração de (h, c, σ_L) POR liga (vs global do P3/bloco 15): vantagem de casa,
cutoff de empate e dispersão de força endógenos.

- **Parâmetros endógenos plausíveis** (32 ligas): h [0.085, 0.350], **c [0.297,
  0.449]** (cutoff de empate por liga), σ_L [0.137, 0.436]. corr(c, taxa de empate) =
  **+0.906** — c capta a "empatabilidade" da liga; corr(σ_L, p_fav) = **+0.874** —
  σ_L recupera a competitividade observável.
- **A lei sobrevive:** skew prevista pelo modelo da PRÓPRIA liga vs observada r =
  **+0.905**, RMSE 0.026 — igual ao global (r=+0.90). Calibrar (h,c,σ) por liga não
  muda a história.
- **Conclusão:** a invariância sobrevive ao cutoff de empate endógeno; σ_L
  (competitividade) continua governando a skewness, liga a liga.

Artefatos: `skewlib/model.py` (calibrate_by_league),
`analysis/34_per_league_calibration.py`, `outputs/per_league_calibration.csv`,
`outputs/fig/f22_per_league_calib.png`.

---

> **1ª rodada no dataset congelado EXAURIDA** (2026-06-23): W1–W5 · P1–P5 · B1–B2 ·
> C1–C3 · E1–E3 · D2–D4 · F1–F3 · G1–G3 · H2. Segue a **2ª rodada** (I…) explorando
> veias intocadas do MESMO dataset. Lineage em `lineage.json` / `docs/LINEAGE.md`.

## Fase I — Validação cruzada do mecanismo: modelo de gols (Poisson) (2026-06-23)
A lei skewness=f(competitividade) foi derivada de um ordered-probit sobre a margem
latente. Aqui um modelo COMPLETAMENTE diferente — Poisson de GOLS (ataque/defesa +
mando por liga-temporada, resultado via Skellam) — gera as probabilidades e a
skewness. 617 liga-temporadas ajustadas.

- **O modelo de gols recupera a competitividade:** corr(p_fav Poisson, p_fav
  empírico) entre 38 ligas = **+0.972** [+0.95,+0.99].
- **E reproduz a skewness:** corr(skew Poisson, skew empírico) = **+0.925**
  [+0.85,+0.97]; o Poisson cai na curva do ordered-probit com r=**+0.85** (vs
  empírico +0.90). Nível um pouco menor (skew Poisson médio +0.177 vs +0.215) porque
  o Poisson subdispersa levemente o p_fav — a LEI (ordenação) é o que importa.
- **Conclusão:** três modelos independentes — margem latente (ordered-probit), gols
  (Poisson) e o mercado (empírico) — caem na MESMA curva. A lei é independente do
  modelo gerador; não é artefato de uma forma funcional escolhida.

Artefatos: `skewlib/goals.py` (fit_match_probs, league_season_table, by_league),
`analysis/35_poisson_crossmodel.py`, `outputs/poisson_crossmodel_by_league.csv`,
`outputs/fig/f23_poisson_crossmodel.png`.

## Fase J — Chegada de informação (HT→FT): o núcleo mecânico é dinâmico (2026-06-23)
Sem odds de abertura (D1 fora), o RESULTADO do intervalo é o choque de informação. A
prob de vitória do favorito pré-jogo se atualiza com o placar do HT, e a skewness do
"resto do jogo" é de novo a identidade (1−2q)/√(q(1−q)) na prob condicional q.
150.950 jogos com HT.

- **A assimetria RESOLVE com a informação:** estado do favorito no HT → skew do resto
  do jogo: **atrás** (20.6%) q=0.139, skew **+2.08** (virou lotérica); **empatado**
  (42.4%) q=0.402, skew +0.40; **+1** (26.1%) q=0.757, skew **−1.20**; **+2 ou mais**
  (10.9%) q=0.945, skew **−3.91** (quase certo). A identidade mecânica vale a CADA
  estado de info, não só no apito inicial.
- **Calibração dinâmica (martingale):** E[q condicional do HT | faixa de p0] ≈ p0,
  erro médio |p0−q| = **0.0035** — a prob pré-jogo é bem calibrada e o HT a refina sem
  viés.
- **Conclusão:** o FLB/identidade é um fato DINÂMICO — a skewness implícita acompanha
  a prob de vitória em qualquer instante; ela não "descobre" um valor eficiente ao
  longo do tempo, ela já É a imagem algébrica da prob corrente. Extensão temporal do W1.

Artefatos: `skewlib/inplay.py` (fav_state, conditional_table, martingale_check),
`analysis/36_inplay_resolution.py`, `outputs/inplay_conditional.csv`,
`outputs/fig/f24_inplay.png`.

## Fase K — Diversificação: a skewness é fenômeno de aposta única (2026-06-23)
A skewness padronizada do retorno MÉDIO de N apostas (quase) independentes escala
skew(X)/√N. Uma banca diversificada tende ao gaussiano; a aposta isolada é
fortemente assimétrica.

- **Aposta única:** skew realizada favorito **+0.230**, azarão **+2.254**
  (lotérica). O retorno médio de N apostas decai como skew/√N (empírico ≈ previsto).
- **Diversificar mata a assimetria:** favorito vira ~gaussiano (skew<0.1) em **~6**
  apostas; o azarão precisa de **~509** (muito mais skewed). O sindicato
  diversificado vê retornos ~gaussianos — só o EV negativo.
- **Conclusão:** a assimetria que o apostador "ama" (Golec-Tamarkin) é da aposta
  ISOLADA; ela some sob diversificação. O FLB sobrevive porque o apostador
  RECREATIVO concentra poucas apostas lotéricas — o canal microeconômico que
  sustenta o viés ser EV-negativo (complementa C3).

Artefatos: `skewlib/portfolio.py` (skew_decay, n_to_gaussian),
`analysis/37_diversification.py`, `outputs/diversification.csv`,
`outputs/fig/f25_diversification.png`.

## Fase L — Vantagem de casa secular vs invariância da skewness (2026-06-23)
A vantagem de casa (HFA) caiu nas décadas recentes; a skewness acompanha?

- **HFA cai, skew não:** taxa de vitória do mandante 0.449 (2005) → 0.431 (2025),
  β=**−0.00133/ano** (Δ20a −0.027, queda marcada); skewness β=−0.00009/ano (Δ20a
  −0.002, plana). corr(HFA, skew) ano a ano = **−0.24** [−0.72,+0.55] (IC inclui 0).
- **Conclusão:** a assimetria depende da DISPERSÃO de p_fav (competitividade), não
  do nível do mando — fecha o confound pelo lado da vantagem de casa.

Artefatos: `skewlib/extras.py` (hfa_and_skew_by_year),
`analysis/38_home_advantage.py`, `outputs/hfa_by_year.csv`,
`outputs/fig/f26_home_advantage.png`.

## Fase M — Risco de cauda realizado das estratégias (2026-06-23)
Lado quant: momentos realizados, VaR/CVaR e max drawdown do P&L acumulado
(aposta unitária, ordem cronológica).

- **Favorito vs azarão:** favorito ret −4.82%, skew +0.23, exkurt −1.7, maxDD
  **−9.9k** unidades; azarão ret −10.2%, skew +2.25, exkurt +8.2, maxDD **−20.9k**.
  Ambas sangram a margem (P&L final negativo), mas o azarão é a CAUDA — drawdown
  ~2× mais fundo, sequências longas de perdas pontuadas por prêmios raros.
- **Conclusão:** a estrutura de skewness se traduz em risco de banca concreto — a
  "lotérica" do azarão é drawdown profundo + caudas grossas, não só um momento.

Artefatos: `skewlib/extras.py` (tail_metrics, max_drawdown),
`analysis/39_tail_risk.py`, `outputs/fig/f27_tail_risk.png`.

## Fase N — Entropia + co-momento entre mercados (2026-06-23)
(1) Entropia de Shannon da distribuição 1X2 como índice de competitividade
odds-based; (2) a skew do 1X2 e a do O/U compartilham um fator comum?

- **Entropia é a competitividade:** média 1.004 nats (máx 3-vias 1.099);
  corr(entropia, skew) = **+0.827** [+0.70,+0.91] — índice alternativo robusto
  (mais entropia/mais parelho ⇒ mais skew positiva).
- **NULO honesto no co-momento:** corr(skew 1X2, skew O/U 2.5) = **+0.15**
  [−0.39,+0.65] (IC inclui 0). As duas assimetrias NÃO são um fator único: o 1X2
  mede dispersão de quem-vence (competitividade), o O/U mede o ambiente de GOLS —
  dimensões largamente ortogonais. Cada mercado precifica uma feição estrutural
  diferente.
- **Conclusão:** entropia confirma a lei por mais um índice; mas a assimetria não é
  um latente único entre mercados — é específica à dimensão que cada mercado mede.

Artefatos: `skewlib/extras.py` (shannon_entropy, entropy_by_league),
`analysis/40_entropy_comoment.py`, `outputs/entropy_comoment.csv`,
`outputs/fig/f28_entropy_comoment.png`.

## Fase O — Bateria de modelos geradores: a lei é independente do modelo (2026-06-23)
A Frente I validou a lei com UM gerador alternativo (Poisson de gols). Aqui a
submetemos a uma BATERIA de geradores genuinamente distintos, cada um produzindo
(pH,pD,pA) por jogo por liga-temporada, e medimos se todos reproduzem a lei e caem
na curva S(σ_L) do ordered-probit. 617 liga-temporadas, 38 ligas.

- **Cinco famílias + o mercado, uma curva.** corr(skew do modelo, skew empírico)
  entre 38 ligas: **Poisson +0.925** [+0.85,+0.97] · **Dixon-Coles +0.874**
  [+0.77,+0.94] · **Bradley-Terry-Davidson +0.840** [+0.71,+0.93] · **Elo de
  resultados (odds-free) +0.786** [+0.59,+0.90]. Todos recuperam a competitividade
  (corr p_fav +0.91…+0.97) e caem na curva derivada (r na curva +0.85…+0.96 vs
  empírico +0.90).
- **O Dixon-Coles aproxima o NÍVEL do mercado:** a correção de dependência em
  placares baixos (ρ médio −0.05, empurra empates 0-0/1-1) sobe a skew para **+0.199**
  (vs Poisson +0.177), mais perto do empírico +0.215 — o modelo canônico do futebol
  é o que melhor casa o nível, não só a ordenação.
- **Família SEM gols também cai na lei:** o Bradley-Terry-Davidson (forças
  multiplicativas + empate, comparação pareada logística — nenhum gol) reproduz a
  ordenação a **+0.84**. E o gerador ODDS-FREE (Elo de resultados → mapa ordinal, a
  máquina da W2) cai exatamente na curva (r=**+0.96**).
- **Modelos desenhados para desviar COLAPSAM ao Poisson:** gols de futebol são
  Poisson independente quase puro — covariância casa×fora mediana **−0.07** (Poisson
  bivariado λ₃≈0) e super-dispersão ≈0 (Negative-Binomial α≈0). Ambos colapsam ao
  Poisson e nada acrescentam — reportados como robustez, não como série.
- **Nota de reprodução (hardening):** sob o stack novo (pandas 3 / numpy 2 /
  statsmodels atual) o GLM de uma liga-temporada patológica (JAP 2017) sofre
  separação quase-completa (p_fav≈1 em todo jogo vs ~0.48 empírico), explodindo a
  skewness de odds-justas. Adicionado `goals.degenerate_fit` (guard de separação);
  a Frente I volta exatamente ao ledger (corr_skew +0.925) e a bateria fica blindada.
- **Conclusão:** a lei skewness=f(competitividade) não é artefato de nenhuma forma
  funcional — margem-probit, gols-Poisson, gols-com-dependência, forças-logísticas
  e ratings-de-resultados convergem todos à MESMA curva. É geometria da mistura de
  apostas de dois pontos sobre a distribuição de competitividade da liga.

Artefatos: `skewlib/crossmodel.py` (dc_probs, dc_rho, btd_probs, elo_by_league,
battery_table), `skewlib/goals.py` (fit_rates, degenerate_fit),
`analysis/41_model_battery.py`, `outputs/model_battery_by_league.csv`,
`outputs/fig/f29_model_battery.png`.

---

> **2ª rodada no dataset (I–N) concluída** (2026-06-23): cross-model Poisson,
> dinâmica HT→FT, diversificação, HFA secular, cauda realizada, entropia+co-momento.
> **Fase O (2026-06-23):** bateria de modelos geradores — 5 famílias independentes +
> o mercado na mesma curva (independência de modelo).

---

# 3ª RODADA — frentes de DADO EXTERNO (football-data.co.uk canônico)

> A 1ª/2ª rodadas exauriram o mirror congelado. Estas frentes usam o
> football-data.co.uk **canônico** (`data/canonical/`, baixado por
> `analysis/50_fetch_canonical.py`), que traz o que o mirror não tem: odds de
> ABERTURA vs FECHAMENTO e profundidade pré-2005. VAR (H1) usa o mirror congelado.
> Proveniência do dado canônico em `canonical_hash()` (carimbada em cada fase).

## Fase D1 — Descoberta de preço: a assimetria já nasce na abertura (2026-06-23) [canônico]
O mirror só tem o fechamento; o canônico traz odds de ABERTURA (Avg*) e FECHAMENTO
(Avg*C) do mesmo jogo (2019/20–2023/24, 21 ligas, 34.659 jogos). Teste da tese no
eixo TEMPORAL da formação de preço: a skewness é herdada da estrutura (presente já
na abertura) ou produzida pela negociação (construída até o fechamento)?

- **A assimetria já está no preço de abertura:** skew global abertura **+0.248** →
  fechamento **+0.249** (within ~1.03 nos dois); corr(skew_open, skew_close) entre
  21 ligas = **+0.998** [+0.99,+1.00]. Δskew médio por liga +0.0005 (sd 0.0045).
- **O mercado refina a MARGEM, não a assimetria:** overround abertura 1.0609 →
  fechamento 1.0597; Brier do favorito 0.2344 → 0.2330 (fechamento mais afiado).
  Mas a lei estrutural está presente já na abertura: corr(skew, p_fav) = −0.866
  (abre) / −0.874 (fecha). Drift do favorito +0.0001 (sem steam sistemático).
- **Conclusão:** a assimetria não é construída pela negociação — está no primeiro
  preço. O fechamento aperta margem e calibração e deixa a skewness intacta.
  Extensão TEMPORAL da ortogonalidade da margem (W4/D2, que era entre books).

Artefatos: `skewlib/fdcanon.py`, `analysis/42_open_close.py`,
`outputs/open_close_by_league.csv`, `outputs/fig/f30_open_close.png`.

## Fase H1 — VAR: choque institucional não move a skewness (placebo) (2026-06-23)
O VAR é um choque institucional que NÃO altera a dispersão de força dos times.
Diferenças-em-diferenças escalonado (mirror congelado): ligas adotam em 2018/2019/
2020; divisões inferiores inglesas/escocesas (sem VAR de liga) são controle
nunca-tratado. 321 liga-anos, 10 tratadas + 6 controles.

- **Efeito NULO na skewness:** β=**−0.0066** [−0.035,+0.022], p=**0.65** (=−0.14 SD
  da liga, IC inclui 0). Taxa de vitória do favorito β=+0.0024 (p=0.80) e p_fav do
  mercado β=+0.0050 (p=0.45) — também nulos. Event-study sem salto na adoção.
- **Contraste com a COVID (W3):** o único choque que moveu a skewness foi a COVID
  (+0.42 SD, via queda de HFA) — um choque REAL de competitividade. O VAR, que não
  toca a estrutura de força, deixa a skewness invariante.
- **Conclusão:** placebo de competitividade — só choques de COMPETITIVIDADE movem a
  skewness, não fatores institucionais. Confirma skewness = f(dispersão de força).

Artefatos: `skewlib/var.py`, `analysis/44_var.py`, `outputs/var_panel.csv`,
`outputs/fig/f31_var.png`.

## Fase P6 — Pré-2005: o regime moderno já vigora desde ~2000 (2026-06-23) [canônico]
O paper prevê que o baseline da liga se desloca nos choques de regime (Bosman 95,
Champions 94/95, receita ~2003). Estendemos para trás com WILLIAM HILL — o único
book contínuo 2000–2025 (book consistente; skewness é book-invariante, G1/D2).
158.323 jogos, 21 ligas, 2000–2023.

- **SEM quebra em 2005:** o recorte ≥2005 do estudo NÃO é fronteira de regime —
  PELT acha quebras espalhadas (2005/2007/2010×2/2014/2016), nenhuma comum. A
  ESTRUTURA por liga é a mesma desde 2000: corr(baseline pré-2005, moderno) entre
  17 ligas = **+0.76**.
- **Drift de NÍVEL fraco e marginal:** moderno +0.232 vs pré-2005 +0.214 (Δ +0.018);
  FE de liga β=−0.019 [−0.037,−0.002] p=0.03, mas pareado p=0.10 e **sensível ao
  endpoint** (com 2024 parcial incluído, p=0.25). Magnitude bem abaixo da variação
  entre-ligas (sd 0.047) — coerente com invariância INTRA-regime + evolução lenta de
  balanço, não atemporalidade.
- **Limite honesto:** odds 1X2 só existem desde ~2000 — os choques dos anos 1990
  (Bosman/Champions) ficam ANTES das odds e permanecem intestáveis. Estendemos a
  janela de invariância em 5 anos; a predição completa do paper exige dado pré-odds.

Artefatos: `skewlib/fdcanon.py` (WH), `analysis/43_pre2005.py`,
`outputs/pre2005_by_league.csv`, `outputs/fig/f32_pre2005.png`.

---

> **3ª rodada (dado externo) concluída** (2026-06-23): D1 (abertura→fechamento),
> H1 (VAR), P6 (pré-2005). 38 fases no ledger.

---

# 4ª RODADA — síntese: SIMILARIDADE DE ASSIMETRIAS (objetivo-raiz)

> O objetivo original do projeto era **medir a similaridade de assimetrias**. Toda a
> evidência acima vira um único APARELHO (`skewlib/skewmeter.py`) que mede a assinatura
> de assimetria de uma entidade e a distância entre assimetrias de duas.

## Fase Q — skew-meter: a similaridade de assimetrias, operacionalizada (2026-06-23)
Aparelho que mede, por liga/era/mercado/janela: assinatura (skew/forma + competitividade),
distância BRUTA, distância RESIDUAL (descontada a competitividade pela lei fechada),
piso amostral e veredito de equivalência. 38 ligas.

- **Similaridade de assimetrias = similaridade de competitividade.** Distância bruta
  |Δskew| mediana entre ligas **0.051**; descontada a competitividade por **1 parâmetro**
  (média p_fav), cai para residual **0.023** — 1 número explica **R²=0.82** da variância.
- **Escada de suficiência (resultado novo, corrige a 1ª leitura):** 1 parâmetro
  R²=**0.82** → 2 momentos (média+variância de p_fav) R²=**0.98** → distribuição INTEIRA
  R²=**0.99** (resíduo = piso amostral). A **estatística suficiente mínima é a
  distribuição de p_fav**; a média sozinha deixa um resíduo **estável** (split-half
  temporal r=**0.98**), que é a **curvatura da lei** (capturada pelo 2º momento), não ruído.
- **Aparelho de POUCOS parâmetros:** sem Shin (inverse-odds, ~0 custo) corr **0.997** ·
  1 parâmetro **0.90** · odds-free (só W/D/L) **0.83**. Convergência em tempo real:
  SE 0.026 em 200 jogos, **0.018 em 400** (< sd entre-ligas 0.051 → já ranqueia).
- **Veredito por EQUIVALÊNCIA (TOST), não significância** (com n enorme tudo rejeita):
  margem ½·sd=0.026. **E0 vs E3** (Premier vs 4ª divisão inglesa): skew bruto 0.167 vs
  0.294 (muito diferente) → residual **0.009** → **EQUIVALENTES** (competitividade explica
  93%). E0 vs SP1 equivalentes; N1 vs I2 e BRA vs ARG distintas (resíduo real).
- **Conclusão:** "quão parecidas são as assimetrias de A e B?" reduz-se a "quão parecidas
  são as competitividades de A e B?" — medível com 1 número, em tempo real, até sem odds.
  A distribuição de p_fav é o que torna a redução EXATA.

- **Endurecimento (rigor):** SE por **block-bootstrap de temporadas** 0.0070 vs i.i.d.
  0.0042 (×1.7, dependência intra-ano); distância de forma de **Mahalanobis** (skew+
  exkurt) corr 0.74 com o escalar; lei **out-of-sample** (calibra anos pares, prevê
  ímpares) R²=**0.80** ≈ in-sample 0.82 — a régua do resíduo não é overfit.

Artefatos: `skewlib/skewmeter.py` (measure, distance, residual, sufficiency_ladder,
tost, skew_se_block, shape_distance, law_oos_r2), `analysis/45_skewmeter.py`,
`outputs/fig/f33_skewmeter.png`. **Produto:** widget interativo `site/src/components/
SkewMeter.astro` (gauge + lei/resíduo + similaridade) na seção §07 do site, com dados
exportados por `export_site_data.py` (blocos `skewmeter`/`convergence`). Paper §4.8.

---

> **4ª rodada (síntese)** (2026-06-23): skew-meter — o objetivo-raiz "similaridade de
> assimetrias" virou aparelho com escada de suficiência e veredito de equivalência.
> 39 fases no ledger. Fronteiras restantes: outros esportes (decisão: futebol
> exclusivamente) e odds pré-2000 (inexistentes). Lineage em `lineage.json`/`LINEAGE.md`.
