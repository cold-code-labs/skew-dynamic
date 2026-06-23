# Structural Invariance of Return Skewness in Football Betting Markets

*Vitor Alves* — Cold Code Labs

**Target:** Royal Society Open Science (working draft)

---

## Abstract

We study the asymmetry (skewness) of returns implied by football betting markets
and ask whether it is a temporal process or a structural invariant. Using
205,435 matches across 38 leagues (2005–2025), we define the *ex-ante* skewness
of the favourite bet from de-vigged (Shin) implied probabilities and show, via a
law-of-total-cumulants decomposition, that market skewness is ≈100% the
within-match Bernoulli asymmetry of the win-probability distribution — the
algebraic image of the favourite–longshot bias, not an emergent pooling effect
(ex-ante +0.236 ≈ ex-post +0.230; the within-match term is +102.6% of the third
moment). The cross-league level tracks competitiveness, and the relation
survives a competitiveness measure built **without odds** — a results-only Elo
(skewness vs upset rate r = +0.83) — while odds- and Elo-based favourite strength
agree at r = 0.91, implying the market merely *reads* the sporting structure. A
league×season panel shows **no secular trend** within the modern competitive
regime spanning our 2005–2025 window (β = +0.00015/yr, p = 0.73; a single
structural break across 38 leagues, COVID-19 in France; 70% of variance is
between-league), and the COVID-19 empty-stadium shock moves skewness in the
predicted direction. Bookmaker margin is orthogonal to asymmetry, and the
identity reappears in the binary over/under-2.5 market. We conclude that the
market's risk asymmetry is a **league-specific structural baseline inherited from
the competitive structure of the sport**, stable within a competitive regime
rather than produced by the pricing of it.

**Keywords:** skewness; favourite–longshot bias; betting markets; market
efficiency; implied probabilities; structural invariance.

---

## 1. Introduction

Betting markets are a long-standing laboratory for studying how prices encode
beliefs and preferences, because each contract has a known, exogenously
determined terminal payoff [Thaler & Ziemba 1988; Snowberg, Wolfers & Zitzewitz
2013]. A central, well-documented regularity is the **favourite–longshot bias**
(FLB): longshots are systematically over-priced and favourites under-priced
relative to their empirical win frequencies [Snowberg & Wolfers 2010]. A leading
explanation is a **preference for skewness**: bettors accept a lower expected
return in exchange for the small-probability, large-payoff (positively skewed)
profile of a longshot [Golec & Tamarkin 1998; Garrett, Hartley & Coughlin 2006;
Andrikogiannopoulou & Papakonstantinou]. This literature is overwhelmingly
**cross-sectional**: it characterises how skewness varies *across* bets within a
single cross-section.

We ask a different, complementary question. Treat the skewness of the market's
return distribution as a quantity that can be measured repeatedly over time and
across competitions. **Is it a temporal process — drifting, mean-reverting,
regime-switching — or a structural invariant fixed by the sport?** Three sub-
questions follow: (i) where does the skewness come from (mechanism); (ii) does
its time series carry dynamics; and (iii) what determines its level in a given
league?

Our contribution is threefold. First, we make explicit and quantify the
**mechanical core**: the skewness of a fixed-odds bet is, by construction, an
algebraic function of the win probability, and we show via a moment decomposition
that essentially *all* of the aggregated market skewness is this within-match
term — the FLB structure — rather than an artefact of pooling heterogeneous
matches. This converts the natural objection ("isn't this tautological?") into
the result itself. Second, we establish the **structural law** skewness =
*f*(competitiveness) using a competitiveness measure constructed **without any
market information** (a results-only Elo), breaking the circularity that would
otherwise undermine the claim. Third, we document **intra-regime temporal
invariance** as a statement about market efficiency and microstructure: despite
the enormous growth of online betting, exchanges and algorithmic pricing over this
period, the risk-asymmetry structure of the market did not move. We are careful
here: the competitive-balance literature documents *real* regime breaks in English
football tied to institutional shocks — the Champions League expansion (1994/95),
the Bosman ruling (1995) and rising revenue inequality around 2003 [Lee & Fort
2012; Basini et al. 2023]. These all predate our ≥2005 sample, which therefore
sits within a single modern regime; our claim is invariance of a league-specific
baseline *within* that regime, not atemporality, and we test for within-window
breaks directly.

## 2. Data

We use a normalised, multi-league compilation of football-data.co.uk match data
(2000–2025), restricted to seasons ≥ 2005, from which odds coverage is
essentially complete. The analysis sample is **205,435 matches across 38 leagues**
(top and second divisions across Europe, plus South-American, North-American and
Asian competitions). For each match we observe the 1X2 closing odds (market
average, `OddH/D/A`, and best market price, `MaxH/D/A`), full-time result and
goals, team identities, division and date. A subset of **148,261 matches** also
carries over/under-2.5-goals odds. The dataset is frozen by content hash
(`PROVENANCE.json`) and the full pipeline is reproducible from a single command.
Invalid odds (≤ 1.01) are dropped.

## 3. The object: ex-ante implied skewness

### 3.1 The two-point payoff and the Bernoulli identity

A unit stake on the favourite at decimal odds *o*, with true win probability *p*,
returns `o − 1` with probability *p* and `−1` with probability `1 − p`. This is a
re-scaled Bernoulli variable, with closed-form central moments

- mean `μ = p·o − 1`,
- variance `σ² = p(1 − p)·o²`,
- third moment `m₃ = p(1 − p)(1 − 2p)·o³`,

so that the **per-match skewness depends only on *p***:

> skew(p) = (1 − 2p) / √(p(1 − p)),

crossing zero at p = ½, positive for longshots (p < ½) and negative for strong
favourites (p > ½). The odds *o* set the magnitude of the winning payoff but,
by affine invariance, do not affect the skewness. This identity is the analytic
backbone of the FLB.

### 3.2 De-vigging

Bookmaker odds embed a margin (overround): the raw inverse-odds sum to more than
one. To recover probabilities we de-vig using the **Shin (1993)** model, whose
single parameter *z* estimates the proportion of informed ("insider") money; we
use multiplicative (proportional) and power de-vigging as robustness. The mean
1X2 overround is 1.067 and the mean Shin *z* is 0.034.

### 3.3 Aggregation and decomposition

For a league or window we measure the skewness of the **mixture** of the per-
match two-point distributions. By the law of total cumulants, the aggregate third
central moment decomposes as

> M₃ = E[m₃ᵢ] + 3·E[σ²ᵢ(μᵢ − μ)] + E[(μᵢ − μ)³],

i.e. a **within-match** term (the per-match Bernoulli/FLB asymmetry), a
**covariance** term (between match-level variance and mean), and a
**between-match** term (dispersion of match means). This decomposition lets us
ask precisely how much of the market's skewness is the mechanical image of the
probability distribution versus an emergent property of pooling.

The de-vigged ex-ante object is our primary measurement; the **ex-post realised**
skewness (the skewness of actual returns) is a robustness check that should
coincide with it under well-calibrated odds.

## 4. Results

### 4.1 The mechanical core (Figure 1, Figure 3)

The global ex-ante skewness of the favourite bet is **+0.236**, against an ex-post
realised **+0.230** — the implied object reproduces the realised one, confirming
aggregate calibration and licensing the cleaner, sampling-noise-free ex-ante
measure. The cumulant decomposition is decisive: the within-match term is
**+102.6%** of M₃, the covariance term −2.6%, and the between-match term
**−0.0%**. *Market skewness is, to within sampling error, entirely the within-
match Bernoulli asymmetry of the win-probability distribution.* The same holds
conditionally: in every probability bucket the within-match fraction is ≈ 100%,
and ex-ante and ex-post skewness track each other tightly along the theoretical
identity curve, from +0.51 at the longshot end to −1.22 for strong favourites
(Figure 1). The skewness of the betting market is the algebraic image of the
favourite–longshot bias — not an emergent feature of aggregation.

### 4.2 The structural law, without odds (Figure 2)

Across leagues the ex-ante skewness ranges from 0.10 (Netherlands Eredivisie) to
0.33 (Italian Serie B), with standard deviation 0.06, and is strongly related to
how strong favourites typically are. Measured from the odds, corr(mean favourite
probability, skewness) = −0.900 — but this is circular, since both quantities are
built from the same odds.

To break the circularity we construct competitiveness from a **results-only Elo**:
a single chronological pass over all leagues (win/draw/loss plus goal margin,
home advantage), with a rating-difference → (P_H, P_D, P_A) map calibrated on
outcomes by multinomial logit (predicted P(H) = 0.444 = realised 0.444). None of
the resulting league measures touch market data. Two findings follow. First, the
odds- and Elo-based favourite strengths agree across leagues at **r = +0.909**
[0.83, 0.97]: the odds simply *read off* the sporting competitive structure
(structural efficiency). Second, the law survives the odds-free regressors —
skewness vs upset rate **r = +0.826** [0.71, 0.91], vs Elo predictive entropy
+0.719, vs Elo favourite probability −0.748, vs Elo rating dispersion −0.731
(all bootstrap CIs exclude zero). The attenuation relative to the circular −0.900
is the expected errors-in-variables effect of a noisier proxy, not evidence
against the law. The asymmetry of market returns is inherited from the
competitive structure of the league.

### 4.3 Temporal invariance (Figure 4)

Treating (league, season) as the unit of analysis dissolves, by construction, the
composition confound that produced an apparent break in earlier pooled analyses
(the sample grew from 21 to 37 leagues in 2012). In a 638-observation panel with
league fixed effects, the linear year coefficient is **+0.00015 per year**
(cluster-robust SE 0.00045, p = 0.73; 95% CI [−0.0007, +0.0010]) — a twenty-year
drift of ≈ +0.003 against a between-league standard deviation of 0.052. There is
no secular trend.

A variance decomposition attributes 70% of the total variance to the
between-league component (the structural invariant); the within-league standard
deviation is 0.034, of which a per-match bootstrap benchmark attributes 0.019 to
pure sampling noise, leaving a small (≈ 0.028) real temporal fluctuation that is
trendless and mean-reverting — consistent with the white-noise dynamics found in
the time-series tests (variance ratios 0.94/0.94/1.00; AR(1) φ = −0.06, p = 0.39).
The structural league invariant dominates the temporal component roughly 2:1.

We test directly for within-window regime breaks. A conservative PELT search on
each league's season-by-season series finds a *single* break across all 38
leagues — France 2020 (a −0.064 shift, i.e. COVID) — with no common break year
across leagues, and zero breaks for the English top flight (E0: mean 0.165,
sd 0.027). This is consistent with, not contrary to, the competitive-balance
literature: the regime breaks identified for English football [Lee & Fort 2012;
Basini et al. 2023] are tied to shocks (Bosman, the Champions League expansion,
the early-2000s revenue divergence) that predate our sample, so 2005–2025 is
effectively a single regime. The invariance we document is therefore an
*intra-regime* property of a league-specific baseline.

As a natural experiment, the COVID-19 empty-stadium seasons sharply reduced home
advantage (home-win rate 0.447 → 0.417 in 2020). The structural law predicts that
weaker home favourites should shift the probability distribution toward parity and
*raise* skewness; we observe a mean within-league shift of +0.42 standard
deviations, positive in 21 of 33 leagues. The single exogenous competitiveness
shock in twenty years moved skewness in the predicted direction — corroborating
the mechanism without contradicting secular invariance.

### 4.4 Margin is orthogonal to asymmetry

Comparing the market-average odds with the best available price over the same
202,760 matches, taking the best price collapses the overround from 1.067 to 1.009
(the expected return rises from −4.8% to near zero), yet the ex-ante skewness
barely moves, +0.236 → +0.254, with a per-match favourite-probability correlation
of 0.996. Bookmakers compete on *margin* (the level of returns), not on the
*asymmetry* (the structure). Pricing and risk-structure are separable.

### 4.5 The binary market

The over/under-2.5-goals market is a clean two-outcome contract: skewness is a
function of a single probability, free of the three-way 1X2 structure. On 148,261
matches the de-vig is well calibrated (over-rate 0.490 = de-vigged p_over 0.492),
and the favourite-side bet has ex-ante skewness −0.210 with a within-match
fraction of **99.6%**, matching the realised −0.217 and the closed-form identity
exactly across every probability bucket. The mechanical core is not an artefact
of the 1X2 structure.

## 5. Mechanism

The results cohere under one principle. The skewness of a fixed-odds bet is the
Bernoulli asymmetry of its win probability; the market's aggregate skewness is the
average of these over the matches on offer, with negligible contribution from how
the matches are mixed (§4.1). A league's typical favourite strength — its
competitiveness — therefore *determines* its skewness almost deterministically
(§4.2). Because competitiveness is a slow-moving property of a sporting
competition (its scale of change is decades, governed by the distribution of club
strengths, promotion/relegation and the like), the skewness it pins down is a
**temporal invariant** (§4.3). What looks like a question about market dynamics is
answered by a property of the sport: the cancellation of the two tails (weak
favourites contributing right-skew, strong favourites left-skew) is stable because
the underlying competitive distribution is stable. Bookmaker margin shifts the
level of returns but not this asymmetry (§4.4), and the principle is market-
agnostic (§4.5).

## 6. Robustness

The central findings are insensitive to analytical choices. The global ex-ante
skewness is 0.224 / 0.236 / 0.263 under power / Shin / multiplicative de-vigging,
while the cross-league law is essentially unchanged (corr −0.906 / −0.900 /
−0.891). Stationarity is confirmed by both ADF (p < 0.001) and KPSS (p = 0.10)
across window sizes from 500 to 3000 matches and under league-demeaning. The
apparent short-run persistence in overlapping windows (ACF₁ = 0.74) is entirely a
window-overlap artefact: with disjoint windows the series is white noise
(Ljung-Box p = 0.70, ACF₁ = −0.06). The per-match bootstrap benchmark (§4.3)
quantifies how much within-league variation is mere sampling noise. Ex-ante and
ex-post measures agree throughout.

## 7. Discussion

Our results recast a familiar object. The favourite–longshot bias is usually read
as a statement about *prices* — a pricing anomaly explained by skewness
preference. We show that, viewed as the skewness of the market's return
distribution, the phenomenon is better described as a **structural invariant of
the sport** that prices faithfully transcribe: the odds-implied and results-based
measures of competitive structure agree at r = 0.91, and the resulting skewness is
flat across two decades. The market is, in this dimension, efficient and stable —
it neither learns nor drifts, because there is nothing to learn: the asymmetry is
exogenous to pricing.

This contrasts with financial markets, where return skewness is a conditional,
time-varying object actively priced as a risk factor [Kraus & Litzenberger 1976;
Harvey & Siddique 2000] and rationalised through probability weighting [Barberis &
Huang 2008; Boyer, Mitton & Vorkink 2010]. In betting markets the terminal payoff
is exogenous and the skewness is mechanically tied to a slow sporting primitive,
so the same statistical object behaves as a constant rather than a process. The
betting market thus isolates the "supply" side of skewness — set by the event
generator — from the "demand" side studied in asset pricing.

Limitations. Competitiveness is a latent construct; our Elo proxy, though odds-
free, is noisier than the odds themselves, attenuating the estimated law. Team
identities are matched by name across a global pool, which may conflate rare
homonyms. The dataset is a normalised mirror; primary-source provenance from
football-data.co.uk is a natural pre-submission step. Our window is one
competitive regime by construction; extending the odds record back through the
mid-1990s shocks would let us test whether the *baseline itself* shifts across
regimes (the prediction being that it does, in the direction of the documented
competitive-balance changes). Finally, our evidence is from football; whether the
same invariance holds in sports with different competitive structures (tennis,
basketball) is left for external validation.

## 8. Conclusion

The skewness of football betting returns is a structural invariant. It is, to
within sampling error, the algebraic image of the win-probability distribution
(the favourite–longshot bias); its league-level value is fixed by sporting
competitiveness — a relation that survives an odds-free measure of competitiveness
— and it shows no secular drift within the modern competitive regime that spans
our window. Bookmaker margin is orthogonal
to it, and the identity holds in a second, binary market. The market's risk
asymmetry is inherited from the sport, not produced by the pricing of it.

---

## Figures

- **Figure 1.** Favourite–longshot bias: ex-ante and ex-post skewness against
  favourite probability, on the theoretical identity curve (1 − 2p)/√(p(1 − p)).
- **Figure 2.** The structural law: league ex-ante skewness against odds-free
  competitiveness (Elo upset rate), r = +0.83.
- **Figure 3.** Decomposition of the aggregate third moment into within-match,
  covariance and between-match components.
- **Figure 4.** League×season panel: no secular trend in twenty years.

## References

- Andrikogiannopoulou, A. & Papakonstantinou, F. *Estimating Risk Preferences
  from Betting Choices.* Review of Financial Studies.
- Barberis, N. & Huang, M. (2008). *Stocks as Lotteries.* American Economic Review.
- Boyer, B., Mitton, T. & Vorkink, K. (2010). *Expected Idiosyncratic Skewness.*
  Review of Financial Studies.
- Constantinou, A. & Fenton, N. (2012). *Solving the problem of inadequate scoring
  rules for assessing probabilistic football forecasts.* J. Quantitative Analysis
  in Sports.
- Garrett, T., Hartley, R. & Coughlin, C. (2006). *Moment preferences and the
  favorite–longshot bias.*
- Golec, J. & Tamarkin, M. (1998). *Bettors Love Skewness, Not Risk, at the Horse
  Track.* Journal of Political Economy.
- Harvey, C. & Siddique, A. (2000). *Conditional Skewness in Asset Pricing Tests.*
  Journal of Finance.
- Kraus, A. & Litzenberger, R. (1976). *Skewness Preference and the Valuation of
  Risk Assets.* Journal of Finance.
- Shin, H. S. (1993). *Measuring the Incidence of Insider Trading in a Market for
  State-Contingent Claims.* Economic Journal.
- Snowberg, E. & Wolfers, J. (2010). *Explaining the Favorite–Longshot Bias: Is it
  Risk-Love or Misperceptions?* Journal of Political Economy.
- Snowberg, E., Wolfers, J. & Zitzewitz, E. (2013). *Prediction Markets for
  Economic Forecasting.* Handbook of Economic Forecasting.
- Štrumbelj, E. (2014). *On determining probability forecasts from betting odds.*
  International Journal of Forecasting.
- Thaler, R. & Ziemba, W. (1988). *Anomalies: Parimutuel Betting Markets.* Journal
  of Economic Perspectives.
