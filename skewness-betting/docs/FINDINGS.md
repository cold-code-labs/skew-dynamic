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
ruído branco"** (confirmado por 3 testes independentes).

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
