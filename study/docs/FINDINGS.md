# Stability of Skewness in Football Betting Markets
## In-depth results — 6 fronts

**Sample:** 205,435 matches · 38 leagues · 2005–2025 · football-data mirror
**Baseline strategy:** unit bet on the favourite (shortest odds), ex-post return.

---

## CENTRAL THESIS (revised and strengthened)

> The skewness of the betting market **is not a dynamic process — it is a
> structural invariant**. Each league has its own level of skewness, fixed in
> time, determined by its competitiveness. The observed fluctuation is pure
> sampling noise, not market memory. The asymmetry is a property of the sporting
> generator, exogenous to the bookmakers' pricing.

It evolved from "stable-with-memory" (draft v1) → **"structural constant +
white noise"** (confirmed by 3 independent tests). And from **skewness
invariance** → **SHAPE invariance** (Phases B1/B2): not only the 3rd moment, but
the entire implied distribution (var/skew/kurtosis) is a unique function of
competitiveness — it collapses across leagues once conditioned on it.

---

## BLOCK A — Robustness (does the finding survive the confounds?)

| Configuration | ADF | KPSS | Ljung-Box | ACF(1) |
|---|---|---|---|---|
| baseline (overlap) | <0.001 | 0.10 | <0.001 | 0.74 |
| league-demeaned (overlap) | <0.001 | 0.10 | <0.001 | 0.74 |
| **non-overlap** | <0.001 | 0.10 | **0.71** | **−0.08** |
| league-demeaned non-overlap | <0.001 | 0.10 | 0.70 | −0.08 |

- **Stationarity: armoured.** Survives demeaning, non-overlap and windows of
  500 to 3000 matches. ADF<0.001 and KPSS=0.10 in all 10 configs.
- **Persistence: it was an artefact.** The ACF=0.74 came 100% from window
  overlap. Without overlap → white noise (LB p=0.71). **An honest correction
  vs v1.**
- League composition is **not** a confound: demeaning moves almost nothing.
- sd falls monotonically with window size → the variation is sampling error.

## BLOCK B — Where does the skewness come from?

**B1 — by strategy:** skewness monotone in the improbability of the bet.
favourite +0.23 · draw +1.27 · longshot +2.26 · "always away" +2.40.
Mean return follows along (favourite −4.8%, longshot −10.2%) = classic FLB.

**B2 — favourite-longshot bias (the key table):** skewness falls monotonically
as the favourite strengthens, crossing zero at p≈0.50:

| p_favourite | mean ret | skewness | win% |
|---|---|---|---|
| (0.40] | −7.5% | +0.59 | 36% |
| (0.45,0.50] | −4.7% | +0.19 | 45% |
| (0.55,0.60] | −3.5% | −0.22 | 56% |
| (0.70,1.0] | −1.6% | −1.19 | 77% |

**B3 — the mechanism of stability:** corr(favourite strength, variance)=**−0.90**
but corr(strength, skewness)=−0.21 and corr(variance, skewness)≈0. The variance is
sensitive to composition; the skewness is **not**, because the contributions of the
two tails (weak favourites→+, strong→−) cancel in a stable way.

## BLOCK C — Is the series really i.i.d.?

- Variance Ratio(2,4,8) = 0.94, 0.94, 1.00 (=1 → i.i.d.)
- AR(1) φ = −0.06, **non-significant** (p=0.39), half-life ≈ 0
- **Conclusion:** white noise confirmed by 3 tests. No temporal dynamics.

## BLOCK D — Cross-bookmaker (average odd vs best odd) — 2nd finding

| metric | average odd | best odd |
|---|---|---|
| skewness | 0.229 | 0.242 |
| mean return | −4.75% | **−0.16%** |
| overround | 1.067 | 1.009 |

- **The bookmaker's margin is mostly spread across bookmakers.** Arbitraging
  odds recovers 4.6 p.p. of return; the "irreducible" margin is ~0.2%.
- **Skewness is invariant to the bookmaker:** temporal corr of the two series =
  **0.984**. Bookmakers compete on the margin (level); the skewness is exogenous
  to that competition.
- Separates pricing (margin, varies) from structure (skewness, fixed).

## BLOCK E — Heterogeneity across leagues (the richest finding)

- Skewness is **not** universal: it ranges from 0.10 (Netherlands) to 0.33 (Italy B), sd=0.06.
- **corr(league predictability, skewness) = −0.83.** Almost deterministic.
- Leagues with strong favourites (a few dominate) → low skewness; balanced leagues
  (2nd divisions) → high skewness.
- **Generalisation:** each league has a skewness-invariant = f(competitiveness).
  The same mechanism as B3 (within-window scale) reappears across leagues
  (cross-sectional scale). A single principle explains both scales.
- BRA +0.18, ARG +0.31 — South American leagues at the competitive/asymmetric extreme.

## BLOCK F — Forensics of the 2012/13 blip

- The only "structural break" in 20 years was a **sampling artefact**: the
  dataset jumped from 21→37 leagues in 2012 (ARG, MEX, BRA, JAP, POL,
  ROM... came in), many high-skewness, temporarily inflating the window mean.
- **There was no market event.** It reinforces the real stability and validates
  the composition control.

---

## SYNTHESIS FOR THE PAPER

Three levels of result, cohesive under one principle:

1. **Cross-sectional:** FLB confirmed; skewness monotone in improbability.
2. **Temporal:** skewness is constant + white noise (no dynamics) — robust.
3. **Structural:** the level is f(league competitiveness); temporal stability
   follows from competitiveness being a slow property (decadal scale).

**Unifying principle:** structural competitiveness generates asymmetry; since it
changes slowly, skewness is a temporal invariant. The bookmakers' margin is
orthogonal to this (it affects the level of return, not the asymmetry).

## Next fronts (not yet explored)
- Opening→closing drift: the skewness of the price movement (needs opening
  odds; the dataset has partial coverage).
- Intra-season seasonality controlled per league (start vs end).
- Testing the invariance in another sport (basketball/tennis) — external
  generalisation.

---

# PHASE LOG (towards the paper)

> Dataset frozen in `data/PROVENANCE.json` (sha256 `6905ca53…`, 205,435
> matches ≥2005, 38 leagues, 2005-01→2025-06). Baseline reproduced in
> `outputs/phase0_baseline.log`. Each phase below adds a block to the paper.

## Phase 0 — Reproduction + freezing (2026-06-23)
Blocks 00–06 reproduce `FINDINGS` exactly against the full 38-league archive.
Bug fixed in `06_league_hetero` (`tab.skew` collided with `DataFrame.skew()`).
Dataset frozen by hash.

## Phase 1 / W1 — Ex-ante skewness and the mechanical core (2026-06-23)
Primary object redefined: **implied (de-vigged) skewness** of the bet on the
favourite, via the **Shin** model (mean z 3.4% of informed money; overround
1.068). Closed-form, free of sampling noise.

- **Ex-ante ≈ ex-post.** Global ex-ante skew **+0.236** vs realised **+0.230**
  → the implied object reproduces the realised; odds well calibrated in the
  aggregate.
- **Decomposition (law of total cumulants) — establishes the mechanical core:**
  M3 = **+102.6% within-match (Bernoulli/FLB)** − 2.6% covariance − 0.0%
  between-match. The market skewness is, at ~100%, the within-match asymmetry of
  the distribution of p — not a pooling artefact. `within_frac` ≈ 1.00 in **all**
  p_fav bands. It turns the "tautology" criticism into the thesis itself: the
  risk asymmetry IS the algebraic image of the FLB.
- **Cross-league (clean object):** corr(ex-ante, ex-post)=**+0.872**;
  corr(p_fav, skew)=**−0.900** — but still circular (p comes from the odds).
  Target of W2: reproduce with **odds-free** competitiveness.

Artefacts: `skewlib/devig.py`, `skewlib/exante.py`, `analysis/07_devig_exante.py`,
`outputs/exante_by_league.csv`.

## Phase 2 / W2 — Odds-free mechanism: the law is not tautological (2026-06-23)
Competitiveness measured by **Elo built from results only** (no odds;
chronological multi-league step + rating-diff→(P_H,P_D,P_A) map via MNLogit
calibrated on the results — P(H) 0.444 = real 0.444, P(D) 0.264 = real 0.264).

- **Odds and Elo measure the SAME structure:** corr(elo_pfav, p_fav_dv)=**+0.909**
  [0.83,0.97]. The odds merely *read off* sporting competitiveness (structural
  efficiency) — they do not create it.
- **The law skewness=f(competitiveness) SURVIVES without odds:**
  skew ~ upset_rate **+0.826** [0.71,0.91] · skew ~ elo_entropy **+0.719**
  [0.50,0.89] · skew ~ elo_pfav **−0.748** · skew ~ elo_disp **−0.731**. All
  with CI95 far from zero. Circular reference (odds p_fav): −0.900.
- **Attenuation −0.90→−0.75/+0.83 = measurement noise** in the Elo proxy
  (errors-in-variables), not evidence against the law: corr(elo,odds)=0.91 shows
  they measure the same latent. The risk asymmetry is **inherited from the
  competitive structure** of the league, not from the pricing.

Artefacts: `skewlib/elo.py`, `skewlib/stats.py` (bootstrap_corr, ols),
`analysis/08_mechanism_elo.py`, `outputs/mechanism_elo.csv`.

## Phase 3 / W3 — Temporal invariance: league×season panel (2026-06-23)
Treating (league,season) as a unit dissolves the composition confound of Block F
by construction. 638 obs, 38 leagues, 2005–2025.

- **No secular trend:** league FE + linear year (cluster SE by league):
  β=**+0.00015/year** (p=0.73, CI95 [−0.0007,+0.0010]). Drift over 20 years
  ≈ +0.003 vs between-league sd 0.052 → null.
- **Structural dominance:** between-league sd **0.052** vs within-league 0.034;
  ICC=**0.70**. Netting out the sampling noise (bootstrap SE 0.019), the *real*
  temporal fluctuation is sd≈0.028 — small, **with no trend and mean-reverting**
  (consistent with the white noise of Block C). The league invariant dominates ~2:1.
- **Per league:** idiosyncratic and tiny deviations (mean |slope|
  0.0024/year; breaks rare, likely PELT over-segmentation in series of ~20
  points). No market-wide regime.
- **COVID vignette (natural experiment):** empty stadiums in 2020 lowered the
  home win (0.447→0.417). The law predicts: HFA↓ → more parity →
  skewness↑. Observed: mean z **+0.42** SD, **21/33 leagues with z>0**. The only
  exogenous competitiveness shock in 20 years moved the skewness in the predicted
  direction — corroborates the *cause* without violating the secular invariance.

Artefacts: `skewlib/panel.py`, `analysis/09_panel_temporal.py`,
`outputs/panel_league_season.csv`.

## Phase 4 / W5 — Binary over/under 2.5 market: identity beyond 1X2 (2026-06-23)
148,261 matches with O/U 2.5 odds (Shin de-vig; overround 1.067, z **0.067** —
more informed money than in 1X2). Impeccable calibration: real over 0.490 =
de-vigged p_over 0.492.

- **Same identity, different market:** bet on the favourite side → ex-ante skew
  **−0.210** (within-match **99.6%**), ex-post −0.217. The closed form
  (1-2p)/√(p(1-p)) matches exactly per-match (max|diff|=0). By p band, ex-ante
  and ex-post move in lockstep (p=0.52→−0.09; p=0.74→−1.05).
- **Conclusion:** the mechanical core of W1 is **not** an artefact of the 3-way
  structure of 1X2 — it holds in a binary goals market. within≈100% replicates.

Artefacts: `skewlib/overunder.py`, `analysis/10_overunder.py`, `outputs/overunder.csv`.

## Phase 5 / W4 — Orthogonal margin + de-vig robustness (2026-06-23)
- **Margin vs structure (average vs maximum odds, 202,760 matches):** taking the
  best market price collapses the overround **1.067→1.009** (return −4.8%→~0) but
  the ex-ante skewness barely moves: **+0.236→+0.254** (per-match corr p_fav
  **0.996**). The bookmaker competes on the MARGIN (level), not on the asymmetry —
  the margin is largely orthogonal to the skewness.
- **Robustness to the de-vig method:** global skew 0.224 (power) / 0.236 (shin) /
  0.263 (mult) — ±8% in level; but the **cross-league law is invariant**:
  corr(p_fav,skew) = −0.906 / −0.900 / −0.891. The structural finding is not a
  de-vig-choice artefact.

Artefacts: `skewlib/exante.py` (market_skew), `analysis/11_margin_robustness.py`.

## Phase P1 — Reframe: INTRA-REGIME invariance (2026-06-23)
The literature (Lee & Fort 2012; Basini 2023; see `docs/LITERATURA.md`) finds
**real** regime breaks in EPL competitiveness tied to institutional shocks
(Champions League 94/95, Bosman 95, revenue inequality ~2003) — **all prior** to
the ≥2005 cut-off. We reposition the thesis from a "timeless constant" to a
**league-specific structural baseline, stable WITHIN the competitive regime**.

- **Intra-window break test (conservative PELT):** only **1 break across 38
  leagues** (F1/France 2020 = COVID, jump −0.064); **no common break year** (max
  1 league/year) → no market-wide regime in 2005–2025.
- **EPL (E0):** **0 breaks** in the cut-off; mean 0.165, sd 0.027 — stable
  intra-regime, consistent with the EPL's regime shocks being pre-2005.
- **Conclusion:** 2005–2025 ≈ a single modern regime; "no trend" (β≈0) is
  **intra-regime invariance**, not absolute timelessness. It confronts Lee &
  Fort/Basini head-on and uses them as a frame — the counter-evidence becomes an ally.

Artefacts: `skewlib/panel.py` (league_breaks), `analysis/13_regimes.py`.

## Phase P2 — Canonical odds-independent CB from standings (2026-06-23)
Hardening of W2 with the size-robust indices from the literature (Gini out,
Utt & Fort 2002), computed from the **final standings** (results, no odds or Elo)
— a stronger attack on circularity.

- **Law reproduced, sign predicted (imbalance → skewness↓):**
  skew ~ Noll-Scully **−0.625** [−0.83,−0.36] · ~ HHI* (Owen 2007) −0.593 · ~
  Theil/GE1 (Borooah-Mangan) −0.478. All CI95 exclude zero.
- **A clean errors-in-variables ladder:** odds (circular) −0.90 > Elo
  (match-level) +0.83 > standings (season-level) 0.48–0.63. The closer to per-match
  p, the stronger the corr — the latent is strong, measured by proxies of varying
  fidelity.
- Team by team it holds: N1/EPL (NS~1.84, dominance) low skew; MLS (NS 1.13,
  salary cap) and Argentina (NS 1.20) high skew. The mechanism is visible in the
  standings.

Artefacts: `skewlib/balance.py`, `analysis/14_balance_indices.py`,
`outputs/balance_indices.csv`.

## Phase P3 — Formal derivation: skewness = f(force dispersion) (2026-06-23)
The law becomes a **consequence of a model**, not a fit. Ordered-probit
(Goddard-Asimakopoulos 2004; Koning 2000): force r~N(0,σ_L²), latent margin
y*=d+h+ε, cutoffs ±c → (A,D,H); favourite p=max; under fair odds the pooled
skewness S(σ_L)=E[m₃(p)]/E[σ²(p)]^{3/2}.

- **Calibration** (pooled rates H 0.444 / D 0.264 / p_fav 0.499): h=0.220,
  c=0.373, σ_ref=0.291.
- **1st→3rd order validation:** the model predicts the skewness of each league
  from the mean p_fav alone: **corr(predicted, observed)=+0.904**, RMSE **0.024**
  (< half the between-league sd 0.051). The 38 leagues fall on the derived curve (F5).
- **Reading:** the law skewness~competitiveness is an analytic consequence of the
  sport's force model + the FLB identity — it closes "the gap" (no one had tied
  the 3rd moment of odds to a force model). The theoretical curve covers skew
  −0.03..+0.30 (p_fav 0.44..0.76), bracketing the empirical range.

Artefacts: `skewlib/model.py`, `analysis/15_model.py`, `outputs/fig/f5_model.png`.

## Phase P4 — FLB stability over time (Angelini confound) (2026-06-23)
Angelini & De Angelis (2019) find the FLB weakening in recent European data; a
bias in motion could fake skewness invariance. Tested 2005–2025:

- **FLB with no significant trend:** ret_dog (barometer) corr(year)=+0.27
  [−0.23,+0.67] (CI includes 0; a mild hint in Angelini's direction,
  non-significant); flb_spread corr −0.02; calib_err corr −0.13. Δ20yr of the
  spread ≈ −0.002.
- **Year-by-year calibration intact:** mean |skew_exante − skew_expost| = **0.015**;
  the favourite's calibration error ∈ [−0.004,+0.012] every year.
- **Conclusion:** the skewness invariance is **not** an artefact of a drifting FLB
  — the bias is stable and the skewness is mechanical in the distribution of p,
  robust to calibration micro-drift.

Artefacts: `skewlib/decompose.py` (flb_by_year), `analysis/16_flb_stability.py`,
`outputs/flb_by_year.csv`.

## Phase B1 — SHAPE invariance: not only the 3rd moment (2026-06-23)
Generalisation of the mixture's moment decomposition (law of total moments) to
var/skew/**kurtosis**/5th–6th order, and a test of each against the curve derived
from the ordered-probit (P3 did only the skew). Object: is the entire implied
distribution invariant after controlling for competitiveness?

- **The whole shape is MECHANICAL (within-match), not pooling:** the `within`
  fraction (the part coming from within-match asymmetry/shape, the FLB, vs
  between-match dispersion) is ≈1 at **all orders** — m2 +1.000, m3 +1.026,
  m4 +1.006, m5 +1.026, m6 +1.016. The whole shape is the algebraic image of the
  distribution of p, not a mixture artefact.
- **The force model predicts the entire shape from p_fav:** corr(predicted,
  observed) across the 38 leagues = **var +0.987 · skew +0.904 · exkurt +0.890**.
  Skew and exkurt (standardised, scale-free) match in **level and ordering**;
  the var follows the ordering (r=0.99) with an overround scale offset (real odds
  o<1/p). Global: skew **+0.236** (boot SE 0.001), exkurt **−1.683** (strongly
  short-tailed, expected from a mixture of Bernoullis), std5 +0.85, std6 +2.18.
- **Conclusion:** "skewness invariance" strengthens to **SHAPE invariance** —
  the entire implied distribution is a unique function of league competitiveness.

Artefacts: `skewlib/exante.py` (pooled_moments, per_match_central_moments),
`skewlib/model.py` (league_moments, curve_moments), `analysis/17_moments.py`,
`outputs/moments_by_league.csv`, `outputs/fig/f6_moments.png`.

## Phase B2 — Distribution collapse: shape = f(competitiveness) (2026-06-23)
A "data collapse" test (statistical physics): is the shape universal, or does it
collapse under competitiveness? KS on the favourite's return (effect = KS
statistic, since the p-value saturates with large n).

- **Without controlling for competitiveness** (per-league z-scored returns, 38
  leagues): pairwise KS with median statistic **0.474**, 100% of pairs reject —
  the standardised shape **differs** across leagues (the skew varies), so it is
  not universal.
- **Controlling for competitiveness** (one-vs-rest within 8 p_fav bands, 264
  tests): median KS statistic **0.059** — **an 87% drop**. Within each band the
  leagues are nearly indistinguishable; the league identity adds nothing beyond
  competitiveness.
- **Conclusion:** the distribution **collapses** when conditioned on
  competitiveness — a stylised fact that the shape is a (unique) function of
  competitiveness, not of the league.

Artefacts: `skewlib/collapse.py`, `analysis/18_collapse.py`,
`outputs/collapse_ks.csv`, `outputs/fig/f7_collapse.png`.

## Phase C1 — Skewness premium: nothing beyond the mechanical FLB (2026-06-23)
Decomposition of the favourite's return (exact identity) into margin + mechanical
FLB level + residual, and a test of the residual against the per-league implied
skewness.

- **Return = margin + FLB (calibration):** global ret −4.82% = **vig −4.97%** +
  **FLB +0.15%**. The loss is almost all margin; the favourite's FLB is small and
  positive (favourites slightly underpriced). The mechanical FLB curve is monotone
  in p_fav (weak favourites contribute −, strong +).
- **No per-league skewness premium BEYOND the mechanical:** corr(residual, skew) =
  **+0.11** [−0.20,+0.38] (CI includes 0); corr(total FLB, skew) −0.04; corr(vig,
  skew) −0.29. The mispricing residual does not track the league's skewness — the
  bookmaker leaves no extra premium attached to the asymmetry. Consistent with the
  orthogonal margin (W4).
- **Conclusion:** the "skewness premium" is entirely the mechanical FLB (across
  bet types, already in W1/Block B); at the league level no pure premium remains —
  the pricing is efficient up to the margin + the mechanical bias.

Artefacts: `skewlib/premium.py`, `analysis/19_premium.py`,
`outputs/return_decomp.csv`, `outputs/fig/f8_premium.png`.

## Phase C2 — The preference (CPT) is itself invariant (2026-06-23)
Fit of the Tversky-Kahneman probability weighting `w(p)=p^γ/(p^γ+(1−p)^γ)^{1/γ}`
to the calibration curve (PROPORTIONAL implied `q` vs objective hit `π`; the Shin
de-vig would erase the bias to be measured, so the proportional is used).

- **Inverse-S confirmed (γ<1 = FLB):** global γ **0.958**; the calibration reveals
  the bias (longshot q 0.101 vs π 0.086 = overweighted; favourite q 0.711 vs π
  0.743 = underweighted).
- **γ is a TEMPORAL invariant:** by season mean γ 0.955, sd 0.020, trend
  **β=+0.0003/year** (r=+0.08, Δ20yr ≈ +0.006) — **no drift over 20 years**. The
  weighting preference is stable over time, mirroring the skewness invariance (and
  the stable FLB of P4).
- **Nearly invariant across leagues:** mean γ 0.945, sd **0.040**, range [0.85,1.00]
  — tight. It shows a mild association with competitiveness (corr(γ,p_fav) −0.45
  [−0.74,−0.10]), an honest nuance (it may reflect the range of p sampled per
  league), not a break in temporal stability.
- **Conclusion:** the preference parameter behind the FLB is a stable structural
  constant (not a process) — the invariance holds also on the preference side, not
  only on the risk signature.

Artefacts: `skewlib/cpt.py`, `analysis/20_cpt.py`, `outputs/cpt_by_league.csv`,
`outputs/cpt_by_season.csv`, `outputs/fig/f9_cpt.png`.

## Phase E1 — Closed form of S(σ_L): the derivation leaves Monte Carlo (2026-06-23)
P3/block 15 traces the law skewness=f(competitiveness) by SIMULATION over the
force `d`. Here we show that the expectation is a 1-D Gaussian INTEGRAL in `d` and
evaluate it by QUADRATURE — the closed form of
`S(σ_L)=E[m₃(p_fav(d))]/E[σ²(p_fav(d))]^{3/2}`, `d~N(0,2σ_L²)`, deterministic and
free of MC noise.

- **The quadrature reproduces the MC, without noise:** max|MC−exact| = **0.0015**
  (with n=4·10⁵; this is the magnitude of the MC noise itself), mean 0.0006, over
  the whole σ_L grid. The theoretical curve becomes exact and smooth — the
  "derivation by simulation" becomes a closed-form derivation.
- **Balanced limit in closed form:** `S(σ_L→0) = (1−2p₀)/√(p₀(1−p₀)) = +0.2449`,
  with `p₀=Φ(h−c)=0.4392` (the equilibrium favourite = home team). It is the
  per-match identity evaluated at p₀ — the law's intercept comes out analytically.
  The leading curvature `S₂=+8.44>0` (the skew RISES on leaving equilibrium), valid
  for σ_L≲0.1.
- **The curve is NOT monotone (exact characterisation):** concave, with a **peak at
  σ*=0.123 (S_max=+0.304, p_fav*=0.446)** and crossing zero at σ_L≈1.09 (a strong
  favourite ⇒ skew→0 and turns negative). It corrects the "monotone" of the old
  docstring.
- **Mathematical honesty:** `p_fav(d)=max(p_H,p_D,p_A)` has KINKS where the
  favourite switches → `S(σ_L)` is C^∞ but **globally non-analytic** (the Taylor
  series diverges beyond the near-balance regime, confirmed numerically). The
  legitimate closed form is the integral (quadrature), not an elementary series;
  the expansion S₀+S₂σ² is the local analytic anchor.
- **Predicts the 38 leagues from the closed curve:** corr(predicted,observed) =
  **+0.903**, RMSE 0.024 — identical to block 15 by MC (r=0.904), now without
  resampling.
- **Conclusion:** the law skewness=f(competitiveness) is a closed-form consequence
  of the force model + FLB, derived from the Gaussian integral, not a fit nor a
  simulation artefact.

Artefacts: `skewlib/model.py` (league_moments_exact, league_skew_exact,
mean_pfav_exact, smallsigma_coeffs/skew, fav_switch_points, curve_exact),
`analysis/21_closed_form.py`, `outputs/closed_form_curve.csv`,
`outputs/fig/f10_closed_form.png`.

## Phase E2 — Robustness of the force distribution (2026-06-23)
The model assumes Gaussian force, `r~N(0,σ_L²)`. Does the law survive if the force
is heavy-tailed (Student-t), skewed (skew-normal) or bounded-support (uniform)?
Theoretical prediction: the force difference `d=rᵢ−rⱼ` is **symmetric for any iid
force** — the asymmetry of the force cannot bias the law; only the TAIL (kurtosis
of `d`) can move anything.

- **The theory holds:** exc.kurt(d) = normal 0.0, t₅ +2.8, **t₃ +42.6** (very
  heavy tail), skew-normal ±0.3, uniform −0.6. skew(d)≈0 in ALL (incl. the
  skew-normals) — the skewed force generates a symmetric difference.
- **The skew×competitiveness curve barely moves:** reparametrising by observable
  competitiveness (mean p_fav) and comparing to the Gaussian, max|ΔS| =
  t₅ **0.017**, t₃ **0.032**, skew-normal ±0.012, uniform 0.011 — all below the
  between-league sd (0.051). The shift scales with the TAIL of `d` (t₃ is the
  largest), not with its asymmetry (skew-normal sticks to the Gaussian, as predicted).
- **At football's operating point** (p_fav=0.499): skew ∈ [+0.223,+0.250],
  amplitude across families = **0.027** (small relative to the competitiveness
  effect, which sweeps +0.30→−0.02).
- **Conclusion:** the law is **mixture geometry**, not the Gaussian hypothesis —
  robust to heavy tails and force asymmetry. Gaussianity is convenience, not a
  premise carrying the result.

Artefacts: `skewlib/model.py` (force_diff, curve_family), `analysis/22_force_robustness.py`,
`outputs/force_robustness.csv`, `outputs/fig/f11_force_robustness.png`.

## Phase G1 — Reliable and invariant de-vig (2026-06-23)
Adversarial robustness: is the Shin de-vig reliable and the skewness not a method
artefact? Reliability diagram + Brier decomposition (Murphy: BS=REL−RES+UNC) of
the favourite by league/year, and skewness under 5 de-vigs/bookmakers.

- **De-vig calibrated almost perfectly:** favourite hit 0.501 vs mean prob
  0.499; **global REL (calibration error) = 0.0000**. Brier 0.236 = REL 0.000 −
  RES 0.014 + UNC 0.250.
- **REL small and homogeneous:** across 32 leagues mean 0.0005 (sd 0.0003, max
  0.0014); across 21 seasons mean 0.0002 (sd 0.0001). No league/year miscalibrated
  — the de-vig residual is stable (no hidden bias producing the asymmetry).
- **Skewness invariant to method/bookmaker:** shin·odd +0.236, shin·max +0.254,
  mult +0.263, power +0.224, multi-bookmaker consensus +0.252 — amplitude **0.039**,
  all positive. Extends W4: the finding depends on neither the de-vig nor the bookmaker.
- **Conclusion:** the skewness is not manufactured by the de-vig; the implied
  asymmetry is well calibrated against the results and robust to the method choice.

Artefacts: `skewlib/adversarial.py` (fav_won, reliability, brier_decomp,
reliability_by, skew_by_devig), `analysis/23_devig_reliability.py`,
`outputs/reliability_by_league.csv`, `outputs/fig/f12_reliability.png`.

## Phase G2 — Strictly balanced panel (composition killed) (2026-06-23)
The GLOBAL skewness series rebuilt using ONLY the leagues present in all 21
seasons (15 leagues: B1,D1,D2,E0–E3,F1,F2,I1,I2,N1,SP1,SP2,T1) — killing 100% of
the composition confound that P1 attacked per-league.

- **No trend with a fixed basket:** β = **−0.00013/year** (r=−0.06, Δ20yr −0.003)
  in the balanced series vs −0.00009 in the full one; KPSS p=0.10 (stationary).
  Mean level **+0.243 (sd 0.014)** — extremely tight.
- **Conclusion:** the temporal invariance does NOT come from the league basket
  changing year on year; with the core fixed the global series stays flat. The "no
  drift" is real.

Artefacts: `skewlib/adversarial.py` (balanced_leagues, global_series_balanced),
`analysis/24_balanced_panel.py`, `outputs/balanced_global_series.csv`,
`outputs/fig/f13_balanced_panel.png`.

## Phase G3 — CI by block-bootstrap over seasons (2026-06-23)
Honest CIs resampling whole SEASONS (with replacement), respecting the intra-year
dependence that match resampling would break.

- **Global skewness +0.236**, CI95 **[+0.232, +0.239]** (SE 0.0019) — excludes 0
  comfortably.
- **Structural law corr(skew_league, p_fav_league) = −0.900**, CI95 **[−0.922, −0.876]**
  (SE 0.011) — the skewness↔competitiveness relation survives the year resampling.
- **Favourite return −4.82%**, CI95 [−5.37%, −4.43%].
- **Conclusion:** the headline numbers carry a CI from season resampling; the sign
  and magnitude do not depend on a specific window of years.

Artefacts: `skewlib/adversarial.py` (season_block_bootstrap, stat_global_skew,
stat_league_corr), `analysis/25_block_bootstrap.py`.

## Phase D2 — Sharp vs soft: the margin is orthogonal also in the best odd (2026-06-23)
Does the skewness diverge between the market's AVERAGE odd (Odd*, soft) and the
BEST odd (Max*, ~sharp/arb)? By league.

- **Best price almost zeroes the margin:** overround soft 1.069 → sharp 1.008.
- **Skew barely moves, and uniformly:** soft +0.218 → sharp +0.238 (mean Δ
  **+0.020**, sd 0.006). corr(skew_soft, skew_sharp) across leagues = **+0.993** —
  the ordering of the leagues is identical; the **structural law survives in the
  sharp** (corr(skew_sharp, p_fav) = −0.876).
- **Conclusion:** removing the margin shifts the skew little and uniformly; the
  bookmaker competes on margin, not on asymmetry (deepens W4) — the law is invariant
  to the book.

Artefacts: `skewlib/microstructure.py` (skew_by_book_league),
`analysis/26_sharp_soft.py`, `outputs/sharp_soft_by_league.csv`,
`outputs/fig/f14_sharp_soft.png`.

## Phase D3 — Shin's z (informed money) as a series (2026-06-23)
z is a by-product of the Shin de-vig: the fraction of the book attributed to
insiders. z by league/year, its stability and its relation to
competitiveness/overround.

- **z low and tight:** global 0.034 (3.4% of informed money in 1X2); across 38
  leagues mean 0.035, sd 0.004, range [0.023, 0.042].
- **z is essentially the margin reparametrised:** corr(z, overround) = **+0.999**
  (almost tautological in the Shin model — z is monotone in the booksum). The useful
  part is the **orthogonality to competitiveness**: corr(z, p_fav) = −0.04 [−0.37,
  +0.30] — the informational content does not drive the skewness law.
- **Over time:** a slight compression (β=−0.0009/year, Δ20yr −0.019), mirroring the
  smooth decline in the margin; small magnitude.
- **Conclusion:** the priced-in informed money is a low structural constant, tied
  to the margin and orthogonal to competitiveness — consistent with the invariance.

Artefacts: `skewlib/microstructure.py` (shin_z_frame, z_by),
`analysis/27_shin_z_series.py`, `outputs/shin_z_by_league.csv`,
`outputs/fig/f15_shin_z.png`.

## Phase D4 — Asian handicap: the identity in a 3rd market (2026-06-23)
Beyond 1X2 (W1) and O/U 2.5 (W5), the AH is a 2-way market with a MOVING line that
balances the match to ~50/50. The sharpest test of the identity in a different
p_fav regime.

- **The line balances to ~0.5:** 150,003 matches with a valid AH, mean p_fav
  **0.533** (vs 0.44 in 1X2). AH overround 1.044.
- **Same identity, opposite sign:** pooled ex-ante skew = **−0.104** (within-match
  102.7% = mechanical), because p_fav>0.5 (the favourite covers frequently ⇒
  negative skew) — a mirror of 1X2 (+0.236, p_fav<0.5). Ex-post (70,965 settled)
  **−0.117** ≈ ex-ante −0.112.
- **By league on the curve:** skew_ah vs the identity (1−2p)/√(p(1−p)) at the AH's
  p_fav → **r=+0.80**.
- **Conclusion:** a THIRD independent market confirms the mechanical core — the
  skewness is a function of p (the sign is fixed by which side of 0.5 the favourite
  falls), not an artefact of the 3-way structure of 1X2.

Artefacts: `skewlib/microstructure.py` (prep_ah, ah_league),
`analysis/28_asian_handicap.py`, `outputs/asian_handicap_by_league.csv`,
`outputs/fig/f16_asian_handicap.png`.

## Phase F1 — Intra-season seasonality: the invariance holds within the year (2026-06-23)
Does the skewness move from the start to the end of the season (Aug→Jul, thirds
by date)?

- **MILD and predicted drift:** global by phase +0.243 → +0.235 → +0.229
  (amplitude **0.015**); p_fav rises 0.494 → 0.503 (favourites a bit stronger at
  the end, as the standings crystallise). Δskew(end−start) by league: mean
  **−0.008**, CI95 [−0.013, −0.0015] (just excludes 0).
- **Conclusion:** there is a small crystallisation — but ~3–4× smaller than the
  between-league sd (0.05) and **predicted by the law itself** (more p_fav ⇒ less
  skew). The invariance holds also WITHIN the season, up to this minimal drift.

Artefacts: `skewlib/intraleague.py` (add_season_phase, skew_by_phase,
phase_shift_by_league), `analysis/29_intraseason.py`,
`outputs/intraseason_shift_by_league.csv`, `outputs/fig/f17_intraseason.png`.

## Phase F2 — Which matches carry the skewness (tail cancellation) (2026-06-23)
Decomposition of the pooled 3rd moment by MATCH competitiveness band (p_fav):
which matches contribute the asymmetry.

- **Law at the match level:** skew by band ranges from **+0.465** (p_fav 0.39,
  weak favourite) to **−1.055** (p_fav 0.73, strong favourite) — exactly the
  identity (1−2p)/√(p(1−p)). WEAK-favourite matches (p<0.5) sum **+126%** of M₃;
  STRONG-favourite (p>0.5) **−26%**.
- **Conclusion:** the league skewness is the net sum of contributions that tail
  cancellation nearly zeroes; competitiveness at the MATCH level fixes the sign and
  magnitude of each contribution — the macro law emerges from the micro.

Artefacts: `skewlib/intraleague.py` (m3_contribution_by_bin),
`analysis/30_game_contribution.py`, `outputs/m3_contribution_by_bin.csv`,
`outputs/fig/f18_game_contribution.png`.

## Phase F3 — Per-team decomposition: the signature comes from force dispersion (2026-06-23)
By club: dominance (mean Elo) vs the mean skewness of the matches it plays.

- **Dominant clubs pull towards negative skew:** Barcelona (Elo 1983, favourite
  97%) match skew **−1.10**, Bayern −1.09, Real Madrid −0.90; weak clubs (Lahti
  Elo 1182) **+0.06**. corr(Elo, match skew) = **−0.44** [−0.53,−0.34].
- **The law, seen from inside:** corr(league Elo dispersion, league skew) =
  **−0.60** [−0.77,−0.42] — leagues with more super-clubs have lower skew.
- **Conclusion:** the league's skew signature is a function of its force dispersion
  at the TEAM level — the micro version of skewness=f(competitiveness).

Artefacts: `skewlib/intraleague.py` (team_long, team_dominance),
`analysis/31_team_decomposition.py`, `outputs/team_dominance.csv`,
`outputs/fig/f19_team_decomposition.png`.

## Phase H2 — Open vs closed league: the MLS on the law (2026-06-23)
The MLS (USA) is the only CLOSED league in the sample (salary cap, draft, no
relegation), designed to compress force dispersion; the European ones are open.
Prediction: a closed structure ⇒ more competitiveness ⇒ balanced skew.

- **MLS is the most balanced by structural measure:** Noll-Scully **1.13, rank 1/38**
  (the most competitive in the sample) — exactly what a cap + no-relegation predict.
  Ex-ante skew **+0.162**, below the open mean (+0.219); p_fav 0.503.
- **On the curve, with an honest nuance:** residual vs the open-league law −0.06
  (~1 sd) — the MLS sits at the competitive/balanced extreme, consistent with the
  open-vs-closed theory.
- **Conclusion:** the closed league does not break the law — its structure tightens
  competitiveness and the skewness moves towards the balanced. It is not a sharp test
  (only 1 closed league in the sample; a full test needs more closed leagues =
  external data).

Artefacts: `analysis/32_open_vs_closed.py`, `outputs/open_vs_closed.csv`,
`outputs/fig/f20_open_vs_closed.png`.

## Phase C3 — Kelly/staking: growth under the skewness structure (2026-06-23)
What does the asymmetry imply for optimal bankroll growth?

- **Kelly says DON'T bet:** under the real margin, **0.0%** of bets have EV>0 (f*=0
  in all) — after the vig there is no growth to extract (echoes the C1 efficiency).
- **Skewness is the FLB channel:** decomposing the log-growth (g ≈ μ − σ²/2 +
  m₃/3) at a fixed fraction, the longshot SKEWNESS term is **+0.60** (×1e3) vs
  **+0.01** for the favourite — the positive asymmetry offsets part of the negative
  EV in growth/utility. It is the channel through which the preference for skew (FLB)
  survives being EV-negative.
- **Conclusion:** the skewness structure does not open growth (efficient market),
  but it quantitatively explains why the longshot bettor pays EV in exchange for
  asymmetry — the skewness premium in growth/utility terms.

Artefacts: `skewlib/staking.py` (kelly_fraction, growth_rate, moment_growth_terms),
`analysis/33_kelly_staking.py`, `outputs/fig/f21_kelly.png`.

## Phase E3 — Per-league calibration (endogenous draw cutoff) (2026-06-23)
Calibration of (h, c, σ_L) PER league (vs the global of P3/block 15): endogenous
home advantage, draw cutoff and force dispersion.

- **Plausible endogenous parameters** (32 leagues): h [0.085, 0.350], **c [0.297,
  0.449]** (per-league draw cutoff), σ_L [0.137, 0.436]. corr(c, draw rate) =
  **+0.906** — c captures the league's "draw-proneness"; corr(σ_L, p_fav) = **+0.874**
  — σ_L recovers observable competitiveness.
- **The law survives:** skew predicted by each league's OWN model vs observed r =
  **+0.905**, RMSE 0.026 — equal to the global (r=+0.90). Calibrating (h,c,σ) per
  league does not change the story.
- **Conclusion:** the invariance survives the endogenous draw cutoff; σ_L
  (competitiveness) keeps governing the skewness, league by league.

Artefacts: `skewlib/model.py` (calibrate_by_league),
`analysis/34_per_league_calibration.py`, `outputs/per_league_calibration.csv`,
`outputs/fig/f22_per_league_calib.png`.

---

> **1st round on the frozen dataset EXHAUSTED** (2026-06-23): W1–W5 · P1–P5 · B1–B2 ·
> C1–C3 · E1–E3 · D2–D4 · F1–F3 · G1–G3 · H2. The **2nd round** (I…) follows, exploring
> untouched veins of the SAME dataset. Lineage in `lineage.json` / `docs/LINEAGE.md`.

## Phase I — Cross-validation of the mechanism: goals model (Poisson) (2026-06-23)
The law skewness=f(competitiveness) was derived from an ordered-probit over the
latent margin. Here a COMPLETELY different model — a Poisson of GOALS
(attack/defence + home advantage by league-season, result via Skellam) — generates
the probabilities and the skewness. 617 league-seasons fitted.

- **The goals model recovers competitiveness:** corr(p_fav Poisson, empirical
  p_fav) across 38 leagues = **+0.972** [+0.95,+0.99].
- **And reproduces the skewness:** corr(skew Poisson, empirical skew) = **+0.925**
  [+0.85,+0.97]; the Poisson falls on the ordered-probit curve with r=**+0.85** (vs
  empirical +0.90). The level is slightly lower (mean skew Poisson +0.177 vs +0.215)
  because the Poisson slightly underdisperses p_fav — the LAW (ordering) is what matters.
- **Conclusion:** three independent models — latent margin (ordered-probit), goals
  (Poisson) and the market (empirical) — fall on the SAME curve. The law is
  independent of the generating model; it is not an artefact of a chosen functional form.

Artefacts: `skewlib/goals.py` (fit_match_probs, league_season_table, by_league),
`analysis/35_poisson_crossmodel.py`, `outputs/poisson_crossmodel_by_league.csv`,
`outputs/fig/f23_poisson_crossmodel.png`.

## Phase J — Information arrival (HT→FT): the mechanical core is dynamic (2026-06-23)
Without opening odds (D1 out), the HALF-TIME RESULT is the information shock. The
favourite's pre-match win probability updates with the HT scoreline, and the
skewness of the "rest of the match" is again the identity (1−2q)/√(q(1−q)) at the
conditional probability q. 150,950 matches with HT.

- **The asymmetry RESOLVES with information:** the favourite's HT state → the skew
  of the rest of the match: **behind** (20.6%) q=0.139, skew **+2.08** (turned
  lottery-like); **level** (42.4%) q=0.402, skew +0.40; **+1** (26.1%) q=0.757, skew
  **−1.20**; **+2 or more** (10.9%) q=0.945, skew **−3.91** (almost certain). The
  mechanical identity holds at EVERY info state, not only at kick-off.
- **Dynamic calibration (martingale):** E[q conditional on the HT | p0 band] ≈ p0,
  mean error |p0−q| = **0.0035** — the pre-match probability is well calibrated and
  the HT refines it without bias.
- **Conclusion:** the FLB/identity is a DYNAMIC fact — the implied skewness tracks
  the win probability at any instant; it does not "discover" an efficient value over
  time, it already IS the algebraic image of the current probability. A temporal
  extension of W1.

Artefacts: `skewlib/inplay.py` (fav_state, conditional_table, martingale_check),
`analysis/36_inplay_resolution.py`, `outputs/inplay_conditional.csv`,
`outputs/fig/f24_inplay.png`.

## Phase K — Diversification: skewness is a single-bet phenomenon (2026-06-23)
The standardised skewness of the MEAN return of N (nearly) independent bets scales
as skew(X)/√N. A diversified bankroll tends to the Gaussian; the isolated bet is
strongly asymmetric.

- **Single bet:** realised skew favourite **+0.230**, longshot **+2.254**
  (lottery-like). The mean return of N bets decays as skew/√N (empirical ≈ predicted).
- **Diversifying kills the asymmetry:** the favourite becomes ~Gaussian (skew<0.1)
  in **~6** bets; the longshot needs **~509** (much more skewed). The diversified
  syndicate sees ~Gaussian returns — only the negative EV.
- **Conclusion:** the asymmetry the bettor "loves" (Golec-Tamarkin) is that of the
  ISOLATED bet; it vanishes under diversification. The FLB survives because the
  RECREATIONAL bettor concentrates a few lottery-like bets — the microeconomic
  channel that sustains the bias being EV-negative (complements C3).

Artefacts: `skewlib/portfolio.py` (skew_decay, n_to_gaussian),
`analysis/37_diversification.py`, `outputs/diversification.csv`,
`outputs/fig/f25_diversification.png`.

## Phase L — Secular home advantage vs skewness invariance (2026-06-23)
Home advantage (HFA) has fallen in recent decades; does the skewness follow?

- **HFA falls, skew does not:** home win rate 0.449 (2005) → 0.431 (2025),
  β=**−0.00133/year** (Δ20yr −0.027, a marked fall); skewness β=−0.00009/year
  (Δ20yr −0.002, flat). corr(HFA, skew) year by year = **−0.24** [−0.72,+0.55] (CI
  includes 0).
- **Conclusion:** the asymmetry depends on the DISPERSION of p_fav
  (competitiveness), not on the level of home advantage — closes the confound on
  the home-advantage side.

Artefacts: `skewlib/extras.py` (hfa_and_skew_by_year),
`analysis/38_home_advantage.py`, `outputs/hfa_by_year.csv`,
`outputs/fig/f26_home_advantage.png`.

## Phase M — Realised tail risk of the strategies (2026-06-23)
The quant side: realised moments, VaR/CVaR and max drawdown of the cumulative P&L
(unit bet, chronological order).

- **Favourite vs longshot:** favourite ret −4.82%, skew +0.23, exkurt −1.7, maxDD
  **−9.9k** units; longshot ret −10.2%, skew +2.25, exkurt +8.2, maxDD **−20.9k**.
  Both bleed the margin (negative final P&L), but the longshot is the TAIL —
  drawdown ~2× deeper, long losing streaks punctuated by rare prizes.
- **Conclusion:** the skewness structure translates into concrete bankroll risk —
  the longshot "lottery" is a deep drawdown + thick tails, not only a moment.

Artefacts: `skewlib/extras.py` (tail_metrics, max_drawdown),
`analysis/39_tail_risk.py`, `outputs/fig/f27_tail_risk.png`.

## Phase N — Entropy + cross-market co-moment (2026-06-23)
(1) Shannon entropy of the 1X2 distribution as an odds-based competitiveness
index; (2) do the 1X2 skew and the O/U skew share a common factor?

- **Entropy is competitiveness:** mean 1.004 nats (3-way max 1.099);
  corr(entropy, skew) = **+0.827** [+0.70,+0.91] — a robust alternative index
  (more entropy/more balanced ⇒ more positive skew).
- **An honest NULL in the co-moment:** corr(skew 1X2, skew O/U 2.5) = **+0.15**
  [−0.39,+0.65] (CI includes 0). The two asymmetries are NOT a single factor: 1X2
  measures the dispersion of who-wins (competitiveness), O/U measures the GOALS
  environment — largely orthogonal dimensions. Each market prices a different
  structural feature.
- **Conclusion:** entropy confirms the law via one more index; but the asymmetry is
  not a single latent across markets — it is specific to the dimension each market
  measures.

Artefacts: `skewlib/extras.py` (shannon_entropy, entropy_by_league),
`analysis/40_entropy_comoment.py`, `outputs/entropy_comoment.csv`,
`outputs/fig/f28_entropy_comoment.png`.

## Phase O — Battery of generating models: the law is model-independent (2026-06-23)
Front I validated the law with ONE alternative generator (a Poisson of goals).
Here we subject it to a BATTERY of genuinely distinct generators, each producing
(pH,pD,pA) per match per league-season, and measure whether they all reproduce the
law and fall on the ordered-probit curve S(σ_L). 617 league-seasons, 38 leagues.

- **Five families + the market, one curve.** corr(model skew, empirical skew)
  across 38 leagues: **Poisson +0.925** [+0.85,+0.97] · **Dixon-Coles +0.874**
  [+0.77,+0.94] · **Bradley-Terry-Davidson +0.840** [+0.71,+0.93] · **results Elo
  (odds-free) +0.786** [+0.59,+0.90]. All recover competitiveness
  (corr p_fav +0.91…+0.97) and fall on the derived curve (r on the curve +0.85…+0.96 vs
  empirical +0.90).
- **Dixon-Coles approximates the market LEVEL:** the dependence correction at low
  scores (mean ρ −0.05, pushes 0-0/1-1 draws) raises the skew to **+0.199**
  (vs Poisson +0.177), closer to the empirical +0.215 — the canonical football model
  best matches the level, not only the ordering.
- **A family WITHOUT goals also falls on the law:** Bradley-Terry-Davidson
  (multiplicative forces + draw, logistic pairwise comparison — no goals) reproduces
  the ordering at **+0.84**. And the ODDS-FREE generator (results Elo → ordinal map,
  the W2 machine) falls exactly on the curve (r=**+0.96**).
- **Models designed to deviate COLLAPSE to the Poisson:** football goals are nearly
  pure independent Poisson — median home×away covariance **−0.07** (bivariate
  Poisson λ₃≈0) and over-dispersion ≈0 (Negative-Binomial α≈0). Both collapse to the
  Poisson and add nothing — reported as robustness, not as a series.
- **Reproduction note (hardening):** under the new stack (pandas 3 / numpy 2 /
  current statsmodels) the GLM of a pathological league-season (JAP 2017) suffers
  quasi-complete separation (p_fav≈1 in every match vs ~0.48 empirical), exploding
  the fair-odds skewness. Added `goals.degenerate_fit` (a separation guard); Front I
  returns exactly to the ledger (corr_skew +0.925) and the battery is armoured.
- **Conclusion:** the law skewness=f(competitiveness) is not an artefact of any
  functional form — margin-probit, goals-Poisson, goals-with-dependence,
  logistic-forces and results-ratings all converge to the SAME curve. It is the
  geometry of the mixture of two-point bets over the league's competitiveness
  distribution.

Artefacts: `skewlib/crossmodel.py` (dc_probs, dc_rho, btd_probs, elo_by_league,
battery_table), `skewlib/goals.py` (fit_rates, degenerate_fit),
`analysis/41_model_battery.py`, `outputs/model_battery_by_league.csv`,
`outputs/fig/f29_model_battery.png`.

---

> **2nd round on the dataset (I–N) completed** (2026-06-23): cross-model Poisson,
> HT→FT dynamics, diversification, secular HFA, realised tail, entropy+co-moment.
> **Phase O (2026-06-23):** battery of generating models — 5 independent families +
> the market on the same curve (model independence).

---

# 3rd ROUND — EXTERNAL-DATA fronts (canonical football-data.co.uk)

> The 1st/2nd rounds exhausted the frozen mirror. These fronts use the
> **canonical** football-data.co.uk (`data/canonical/`, downloaded by
> `analysis/50_fetch_canonical.py`), which brings what the mirror lacks: OPENING vs
> CLOSING odds and pre-2005 depth. VAR (H1) uses the frozen mirror.
> Provenance of the canonical data in `canonical_hash()` (stamped in each phase).

## Phase D1 — Price discovery: the asymmetry is born at the open (2026-06-23) [canonical]
The mirror has only the close; the canonical brings OPENING odds (Avg*) and
CLOSING (Avg*C) for the same match (2019/20–2023/24, 21 leagues, 34,659 matches).
A test of the thesis on the TEMPORAL axis of price formation: is the skewness
inherited from the structure (present already at the open) or produced by trading
(built up to the close)?

- **The asymmetry is already in the opening price:** global skew opening **+0.248**
  → closing **+0.249** (within ~1.03 in both); corr(skew_open, skew_close) across
  21 leagues = **+0.998** [+0.99,+1.00]. Mean Δskew per league +0.0005 (sd 0.0045).
- **The market refines the MARGIN, not the asymmetry:** overround opening 1.0609 →
  closing 1.0597; favourite Brier 0.2344 → 0.2330 (the close is sharper). But the
  structural law is present already at the open: corr(skew, p_fav) = −0.866
  (open) / −0.874 (close). Favourite drift +0.0001 (no systematic steam).
- **Conclusion:** the asymmetry is not built up by trading — it is in the first
  price. The close tightens the margin and the calibration and leaves the skewness
  intact. A TEMPORAL extension of the margin orthogonality (W4/D2, which was across
  bookmakers).

Artefacts: `skewlib/fdcanon.py`, `analysis/42_open_close.py`,
`outputs/open_close_by_league.csv`, `outputs/fig/f30_open_close.png`.

## Phase H1 — VAR: an institutional shock does not move the skewness (placebo) (2026-06-23)
VAR is an institutional shock that does NOT alter the force dispersion of the
teams. Staggered difference-in-differences (frozen mirror): leagues adopt in
2018/2019/2020; lower English/Scottish divisions (no league VAR) are the
never-treated control. 321 league-years, 10 treated + 6 controls.

- **NULL effect on the skewness:** β=**−0.0066** [−0.035,+0.022], p=**0.65** (=−0.14
  SD of the league, CI includes 0). The favourite win rate β=+0.0024 (p=0.80) and
  the market p_fav β=+0.0050 (p=0.45) — also null. Event-study with no jump at adoption.
- **Contrast with COVID (W3):** the only shock that moved the skewness was COVID
  (+0.42 SD, via the HFA drop) — a REAL competitiveness shock. VAR, which does not
  touch the force structure, leaves the skewness invariant.
- **Conclusion:** a competitiveness placebo — only COMPETITIVENESS shocks move the
  skewness, not institutional factors. Confirms skewness = f(force dispersion).

Artefacts: `skewlib/var.py`, `analysis/44_var.py`, `outputs/var_panel.csv`,
`outputs/fig/f31_var.png`.

## Phase P6 — Pre-2005: the modern regime already holds since ~2000 (2026-06-23) [canonical]
The paper predicts that the league baseline shifts at the regime shocks (Bosman 95,
Champions 94/95, revenue ~2003). We extend backwards with WILLIAM HILL — the only
bookmaker continuous over 2000–2025 (a consistent bookmaker; skewness is
bookmaker-invariant, G1/D2). 158,323 matches, 21 leagues, 2000–2023.

- **NO break in 2005:** the study's ≥2005 cut-off is NOT a regime boundary — PELT
  finds breaks scattered (2005/2007/2010×2/2014/2016), none common. The per-league
  STRUCTURE is the same since 2000: corr(pre-2005 baseline, modern) across 17
  leagues = **+0.76**.
- **LEVEL drift weak and marginal:** modern +0.232 vs pre-2005 +0.214 (Δ +0.018);
  league FE β=−0.019 [−0.037,−0.002] p=0.03, but paired p=0.10 and **endpoint-sensitive**
  (with partial 2024 included, p=0.25). The magnitude is well below the between-league
  variation (sd 0.047) — consistent with INTRA-regime invariance + slow balance
  evolution, not timelessness.
- **Honest limit:** 1X2 odds only exist since ~2000 — the 1990s shocks
  (Bosman/Champions) lie BEFORE the odds and remain untestable. We extend the
  invariance window by 5 years; the paper's full prediction requires pre-odds data.

Artefacts: `skewlib/fdcanon.py` (WH), `analysis/43_pre2005.py`,
`outputs/pre2005_by_league.csv`, `outputs/fig/f32_pre2005.png`.

---

> **3rd round (external data) completed** (2026-06-23): D1 (opening→closing),
> H1 (VAR), P6 (pre-2005). 38 phases in the ledger.

---

# 4th ROUND — synthesis: SIMILARITY OF ASYMMETRIES (root objective)

> The project's original objective was to **measure the similarity of asymmetries**.
> All the evidence above becomes a single APPARATUS (`skewlib/skewmeter.py`) that
> measures the asymmetry signature of an entity and the distance between the
> asymmetries of two.

## Phase Q — skew-meter: the similarity of asymmetries, operationalised (2026-06-23)
An apparatus that measures, by league/era/market/window: the signature (skew/shape
+ competitiveness), the RAW distance, the RESIDUAL distance (competitiveness netted
out by the closed-form law), the sampling floor and an equivalence verdict. 38 leagues.

- **Similarity of asymmetries = similarity of competitiveness.** The raw distance
  |Δskew| has a median across leagues of **0.051**; netting out competitiveness by
  **1 parameter** (mean p_fav), it falls to a residual **0.023** — 1 number explains
  **R²=0.82** of the variance.
- **Sufficiency ladder (a new result, correcting the 1st reading):** 1 parameter
  R²=**0.82** → 2 moments (mean+variance of p_fav) R²=**0.98** → the ENTIRE
  distribution R²=**0.99** (residual = sampling floor). The **minimal sufficient
  statistic is the distribution of p_fav**; the mean alone leaves a **stable**
  residual (temporal split-half r=**0.98**), which is the **curvature of the law**
  (captured by the 2nd moment), not noise.
- **A FEW-parameter apparatus:** without Shin (inverse-odds, ~0 cost) corr **0.997** ·
  1 parameter **0.90** · odds-free (W/D/L only) **0.83**. Real-time convergence:
  SE 0.026 in 200 matches, **0.018 in 400** (< between-league sd 0.051 → already ranks).
- **Verdict by EQUIVALENCE (TOST), not significance** (with huge n everything
  rejects): margin ½·sd=0.026. **E0 vs E3** (Premier League vs the English 4th
  division): raw skew 0.167 vs 0.294 (very different) → residual **0.009** →
  **EQUIVALENT** (competitiveness explains 93%). E0 vs SP1 equivalent; N1 vs I2 and
  BRA vs ARG distinct (a real residual).
- **Conclusion:** "how similar are the asymmetries of A and B?" reduces to "how
  similar are the competitivenesses of A and B?" — measurable with 1 number, in real
  time, even without odds. The distribution of p_fav is what makes the reduction EXACT.

- **Hardening (rigour):** SE by **season block-bootstrap** 0.0070 vs i.i.d.
  0.0042 (×1.7, intra-year dependence); **Mahalanobis** shape distance (skew+
  exkurt) corr 0.74 with the scalar; the law **out-of-sample** (calibrate even
  years, predict odd) R²=**0.80** ≈ in-sample 0.82 — the residual ruler is not overfit.

Artefacts: `skewlib/skewmeter.py` (measure, distance, residual, sufficiency_ladder,
tost, skew_se_block, shape_distance, law_oos_r2), `analysis/45_skewmeter.py`,
`outputs/fig/f33_skewmeter.png`. **Product:** interactive widget `site/src/components/
SkewMeter.astro` (gauge + law/residual + similarity) in section §07 of the site, with
data exported by `export_site_data.py` (blocks `skewmeter`/`convergence`). Paper §4.8.

---

## Phase R — Bet type: the law mirrored across the whole book (block 46)

Each match offers three two-point bets: **favourite** (argmax p), **draw**
(outcome D) and **longshot** (argmin p). Measuring the pooled ex-ante skewness of
the three per league (38 leagues, market odds):

- **All positively skewed** (lottery-like): global skew **+0.236 / +1.294 /
  +2.349** (favourite / draw / longshot). The FLB is a single-bet phenomenon,
  everywhere.
- **All three governed by competitiveness**, in opposite directions: less balance
  (p_fav ↑) **lowers** the favourite's skew (corr **−0.90**) and **raises** that of
  the draw and the longshot (corr **+0.95 / +0.91**), which become bigger longshots.
  It is not a law of the favourite — it is the SAME structural law, mirrored across
  the whole book.
- **Diversification** (block 37, now exposed): the skew of the mean return of N
  bets ≈ skew/√N. A favourites portfolio turns Gaussian in **~6** bets; the
  longshot's survives up to **~509** — which is why the bias bites the recreational
  bettor, not the syndicate.

Artefacts: `skewlib/exante.py` (`fav_dog_draw`, `bettype_by`), `analysis/46_bettype.py`,
`outputs/fig/f34_bettype.png`. **Product:** "Every side of the book" +
"What survives diversification" panels in the `SkewMeter.astro` widget; Mahalanobis
shape column (`shape_cov_inv`). **Service:** API `study/api/` (`POST /measure`, modes
with-odds/odds-free, monitor `/integrity`). Data in `export_site_data.py` (blocks
`bettype`/`diversification`).

---

> **5th round (product)** (2026-06-23): bet-type — the law skew=f(competitiveness) holds
> across the whole book (favourite/draw/longshot), with diversification ~6 vs ~509. The
> apparatus became a product: API `/measure` (with-odds + odds-free + integrity) and a V2
> widget (bet-type radar + diversification curve + Mahalanobis). 40 phases in the
> ledger. Remaining frontiers: other sports (decision: football exclusively) and
> pre-2000 odds (non-existent). Lineage in `lineage.json`/`LINEAGE.md`.

---

## Phase S — External validity: tennis (block 48)

The CANONICAL layer (`skewlib/canonical.py` + `adapters/`) made the core
sport-agnostic — it only needs `(p, o, won)` per bet. Plugging in **tennis**
(tennis-data.co.uk, ATP+WTA 2005–2025, frozen snapshot in
`data/PROVENANCE-tennis.json`), a sport with a **2-outcome** market (no draw) and
an **independent odds source**, over **62,865 matches** and with ZERO new science:

- **Calibration:** mean p_fav **0.688** ≈ real favourite win **0.692** — the
  de-vig is reliable beyond football.
- **The law reappears:** the favourite's skew is more negative where the tournament
  is more imbalanced — corr(skew_fav, p_fav) by tier = **−1.00 (ATP)** / **−0.98 (WTA)**
  (football −0.90). Grand Slam (more imbalanced) has the most negative favourite in
  both tours.
- **The longshot is lottery-like:** skew **+2.314** ≈ football **+2.349**.

The structural invariance is not an artefact of 1X2 nor of football: it is a
property of the SPORT as a competitive system. External validity for §7 (the "one
sport" limitation).

Artefacts: `skewlib/adapters/tennis.py`, `analysis/00b_fetch_tennis.py`,
`analysis/48_tennis.py`, `outputs/fig/f35_crosssport.png`,
`outputs/tennis_by_tier.csv`. The core (`canonical`/`skewmeter`) unchanged.

---

> **6th round (external validity)** (2026-06-23): tennis — the law skew=f(competitiveness)
> and the lottery-like longshot reappear in a 2nd sport (ATP+WTA, 2-outcome market,
> independent odds), via the canonical layer without changing the core. 41 phases in the
> ledger. Adding a sport = one adapter (`docs/DATA-SCHEMA.md`). Lineage in
> `lineage.json`/`LINEAGE.md`.

## Phase T — External validity: basketball (block 49)

A **3rd sport** on the same canonical layer, without touching the core. Plugging in
the **NBA** (sportsbookreviewsonline.com, 16 seasons 2007–08…2022–23, frozen
snapshot in `data/PROVENANCE-basketball.json`), the **moneyline** market (2
outcomes, no draw) and an **odds source independent** of football and tennis, over
**19,621 matches** and with ZERO new science:

- **Calibration:** mean p_fav **0.694** ≈ real favourite win **0.685** — the
  de-vig is reliable also in the NBA moneyline (the ~0.9pp gap is the
  favourite-longshot bias itself, with the favourite slightly overpriced).
- **The law reappears:** the favourite's skew is more negative in the more
  imbalanced seasons — corr(skew_fav, p_fav) by season = **−0.95** (16 seasons;
  football −0.90, tennis −1.00/−0.98). The most lopsided NBA (2007–08, p_fav 0.71)
  has the most negative favourite; the most balanced (2022–23, p_fav 0.66) the least.
- **The longshot is lottery-like:** skew **+2.609** ≈ football **+2.349**, tennis **+2.314**.

On the cross-sport curve (f36), tennis and basketball **overlap** in the same
lopsided region (~0.66–0.75), both on the descending favourite curve and the
ascending longshot curve that football traces at lower competitiveness. Three
sports, three markets (1X2, match-odds, moneyline), three odds sources, one
structural law.

Artefacts: `skewlib/adapters/basketball.py`, `analysis/00c_fetch_basketball.py`,
`analysis/49_basketball.py`, `outputs/fig/f36_crosssport.png`,
`outputs/basketball_by_season.csv`. The core (`canonical`/`skewmeter`) unchanged; no
new dependencies (the fetch uses the stdlib `html.parser`).

---

> **7th round (external validity, 3rd sport)** (2026-06-23): basketball — the law
> skew=f(competitiveness) and the lottery-like longshot reappear in a 3rd sport (NBA,
> moneyline market, independent odds), via the canonical layer without changing the core.
> 42 phases in the ledger. f36 puts football+tennis+basketball on a single curve. Lineage in
> `lineage.json`/`LINEAGE.md`.

## Phase U — Temporal equivalence: "no drift" as a positive claim (block 51)

W3 showed β_year≈0 with **p=0.73** and a CI crossing zero. But a high p is only
**non-rejection** of a trend — not evidence of absence (an underpowered test also
gives a high p). Here we close the logical gap in §4.3 with an **equivalence test
(TOST)**:

- **Pre-registered margin** Δ = ½ the between-league SD (**0.026**), the SAME as in
  §4.8 — read as the largest 20-year drift we would treat as negligible.
- **Result:** the 90% CI of β falls entirely within [−Δ,+Δ] → we reject any drift
  larger than Δ, **p_tost = 0.006**. Robust to per-league bootstrap (p=0.005) and to
  the **balanced** panel (fixed basket of 15 leagues; β=−0.0003/year, p=0.043).
- **Sensitivity:** equivalent at ½ and 1× the SD; inconclusive only at a severe Δ of
  ¼ SD (drift < 0.013 over 20 years — below that the data neither affirms nor denies).

Conclusion: the skewness is not merely *not shown* to drift — it is **statistically
equivalent to not drifting**, within a fraction of a single between-league
difference accumulated over the whole history. It converts the temporal invariance
from absence-of-evidence into evidence-of-absence.

**Honest check (γ, C2):** the same TOST applied to the preference parameter γ
(annual series of 21 points, Δ=½ the between-league SD of γ ≈ 0.020) comes out
**INCONCLUSIVE** (β_γ=+0.0003/year, drift +0.006 over 20yr, p_tost=0.19): the point
drift is small, but the annual series lacks the power to certify equivalence at that
margin. We record this deliberately — the test **is not rigged to pass**; only the
skewness (n=638, league×season panel) has the power for the verdict. That is why the
paper claims equivalence only for the skewness; the other "no drift" results
(P4/FLB, C2/γ, L/HFA) stand as non-rejection.

Artefacts: `skewlib/stats.py:tost`, `skewlib/panel.py:trend_boot`,
`analysis/51_temporal_equivalence.py`, `outputs/fig/f37_temporal_equivalence.png`.

---

> **8th round (inferential rigour)** (2026-06-23): temporal equivalence — the "no secular
> drift" (W3) becomes a positive claim by TOST (p_tost=0.006, margin ½ between-league SD;
> robust to bootstrap and balanced panel). 43 phases in the ledger. f37 (forest) enters as
> Figure 20; §4.3 and the abstract updated.
