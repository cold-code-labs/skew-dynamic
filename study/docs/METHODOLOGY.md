# Structural Stability of Skewness in Football Betting Markets

**Status:** consolidated methodology · pipeline reproduced on a 2005–2025 sample
**Author:** Vitor Alves
**Dataset:** frozen (`data/PROVENANCE.json`, sha256 `6905ca53…`), 205,435
matches, 38 leagues, 2005-01→2025-06. Target: *Royal Society Open Science* (empirical
regularity + mechanism + reproducible artefact).

---

## 1. Research question

Is the skewness of the distribution of implied returns in football betting
markets a **temporal process** or a **structural invariant**? Three fronts:

1. *Cross-sectional* — where does the skewness come from? (mechanism)
2. *Temporal* — does it have dynamics (drift, persistence, breaks) or is it constant?
3. *Structural* — what determines the level of each league?

**Thesis:** skewness is, to first order, the **algebraic image** of the
distribution of implied probabilities; the level of each league is determined by
(slow) sporting competitiveness, which makes it a temporal invariant. The
bookmakers' margin is orthogonal to the asymmetry.

## 2. Gap in the literature

Golec & Tamarkin (1998) treat the preference for skewness as a
*cross-sectional* phenomenon (across bets, within a cross-section); the
favourite-longshot bias (FLB) is the mechanism (Snowberg & Wolfers 2010).
Missing are (i) the **mechanical decomposition** quantifying how much of the
market skewness is the Bernoulli identity of the distribution of p; (ii) the
**structural law** skewness=f(competitiveness) measured with a regressor
*independent of the odds*; (iii) the **temporal invariance** over 20 years as a
statement about efficiency/microstructure. This is the contribution.

## 3. Data

- **Source:** normalised football-data.co.uk (xgabora mirror; main + extra/South
  American leagues), frozen by hash. Cut-off ≥2005 (odds coverage ~100%).
- **N:** 205,435 1X2 matches; 148,261 with an over/under 2.5 market.
- **Columns:** `OddH/D/A` (closing average) and `MaxH/D/A` (best price →
  margin test); `FTResult`, `FTHome/FTAway` (goals → O/U and Elo);
  `HomeTeam/AwayTeam` (Elo); `Division`, `MatchDate`.

## 4. Primary object — ex-ante (de-vigged) skewness

A unit bet on the favourite at decimal odds *o* with true probability *p*:
return `(o−1)` with prob. *p*, `−1` with prob. `1−p` — a **rescaled Bernoulli**
with closed-form central moments (`μ=po−1`, `σ²=p(1−p)o²`, `m₃=p(1−p)(1−2p)o³`).
The per-match skewness **depends only on p**: `(1−2p)/√(p(1−p))`, crossing zero
at p=0.5. The aggregate skewness (league/window) is that of the **mixture**,
decomposed by the **law of total cumulants**:

```
M₃ = E[m₃ᵢ]                     (mechanical: within-match asymmetry / FLB)
   + 3·E[σ²ᵢ(μᵢ−μ)]             (variance×mean covariance)
   + E[(μᵢ−μ)³]                 (between-match dispersion)
```

- **De-vig:** Shin (1993) primary (by-product *z* = fraction of informed
  money); multiplicative and power as robustness.
- **Realised ex-post** (skewness of the actual returns) = robustness; should
  converge to the ex-ante under calibration.

**Multi-moment extension (shape).** The rescaled Bernoulli has closed-form
central moments of **every order**, `m_k = oᵏ·p(1−p)·[(1−p)^{k−1} + (−1)ᵏ·p^{k−1}]`,
and the k-th moment of the mixture follows from the **law of total moments**,
`M_k = E_i[Σ_j C(k,j)·m_{j,i}·dᵢ^{k−j}]`, `dᵢ=μᵢ−μ` (the decomposition of M₃ above
is the k=3 case). This measures var/skew/**kurtosis**/5th–6th order of the implied
distribution and the **`within` fraction** (mechanical) per order. Under fair odds the
means are zero (d≡0), so `M_k=E[m_k]` and the ordered-probit predicts **each** league
moment from competitiveness (not only the 3rd) — *shape invariance*. The **distribution
collapse** (KS conditional on the p_fav band; the effect size is the KS statistic, since
the p-value saturates with large n) tests whether, holding competitiveness fixed, the
distribution is the same across leagues.

## 5. Odds-free competitiveness (breaking the circularity)

Measuring competitiveness via p_fav (from the odds) is circular. We build a
**results-only Elo**: chronological multi-league step (W/D/L + goal difference,
home advantage), and a rating-diff→(P_H,P_D,P_A) map via an **MNLogit calibrated on
the results**. Per-league measures: mean forecast entropy, Elo favourite
probability, force dispersion, upset rate. None touches odds.

## 6. Temporal panel

Unit = (league, season) — dissolves the composition confound by construction.
Tests: secular trend (league FE + year, cluster SE); between/within
decomposition with a **sampling-noise benchmark** (bootstrap of matches);
per-league trends/breaks; **COVID vignette** (empty stadiums in 2020 as a
natural experiment of a shock to home advantage).

## 7. Tests

| Dimension | Test |
|---|---|
| De-vig calibration | over-rate vs p_over; ex-ante vs ex-post |
| Decomposition | law of total cumulants (within/cov/between) |
| Odds-free mechanism | corr/OLS skew~Elo + bootstrap CI (n=38) |
| Stationarity/i.i.d. | ADF+KPSS, Ljung-Box, Variance-Ratio, AR(1) |
| Temporal invariance | panel FE+year (cluster SE), ICC, breaks |
| Margin | overround and skew: average vs maximum odds |
| Closed form (E1) | quadrature of the Gaussian integral vs MC; near-balance expansion |
| Force robustness (E2) | skew×p_fav curve under t-Student/skew-normal/uniform |
| Robustness | de-vig (mult/power/shin), window, overlap, binary O/U |

## 8. Results (frozen sample)

| Finding | Value | Reading |
|---|---|---|
| Global ex-ante / ex-post skew | **+0.236 / +0.230** | implied object reproduces the realised |
| M₃ decomposition | **+102.6% within-match**, ~0% between-match | skewness = algebraic image of the FLB |
| corr(elo_pfav, p_fav_odds) | **+0.909** | odds *read off* sporting competitiveness |
| skew ~ odds-free competitiveness | **+0.83** (upset) / **−0.75** (elo_pfav) | non-circular law survives |
| Secular trend (panel) | β=**+0.00015/year** (p=0.73) | no drift over 20 years |
| ICC (between/total) | **0.70** | league invariant dominates over time |
| Margin: overround vs skew | 1.067→1.009 vs +0.236→+0.254 | margin orthogonal to asymmetry |
| Binary O/U 2.5 | ex-ante −0.210 (within 99.6%) | identity holds beyond 1X2 |
| Closed form S(σ_L) (E1) | quadrature ≈ MC (max\|Δ\|=**0.0015**); S₀=(1−2p₀)/√(p₀(1−p₀)) | law is a closed integral, not a simulation |
| Force robustness (E2) | max\|ΔS\|=**0.03** (t/skew-normal/uniform) < league-sd 0.05 | law = geometry of the mixture, not Gaussianity |

### Synthesis
The skewness of the betting market is a **structural invariant**: ~100% the
within-match asymmetry of the distribution of probabilities (mechanical), with a
league level determined by sporting competitiveness — a relationship that
**survives a competitiveness measure independent of the odds** — and **with no
temporal drift over 20 years**. The bookmakers' margin affects the level of
return, not the asymmetry. The risk asymmetry is **inherited from the sport**,
not produced by the pricing.

## 9. Core references
- Golec & Tamarkin (1998). *Bettors Love Skewness, Not Risk, at the Horse Track.* JPE.
- Snowberg & Wolfers (2010). *Explaining the Favorite-Longshot Bias.* JPE.
- Shin (1993). *Measuring the Incidence of Insider Trading in a Market for
  State-Contingent Claims.* Economic Journal. (de-vigging)
- Štrumbelj (2014). *On determining probability forecasts from betting odds.* IJF.
- Andrikogiannopoulou & Papakonstantinou. *Estimating Risk Preferences from Betting Choices.*
- Constantinou & Fenton (2012). *Solving the problem of inadequate scoring
  rules for assessing probabilistic football forecasts.* (Elo/probabilities)
- Kraus & Litzenberger (1976); Harvey & Siddique (2000); Barberis & Huang (2008)
  — skewness in finance (contrast).
