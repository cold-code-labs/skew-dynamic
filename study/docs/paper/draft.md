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

**Related work and the gap.** Three strands meet here. The competitive-balance
literature measures imbalance with size-robust indices — the Noll-Scully ratio,
the normalised HHI* of Owen, Ryan & Weatherston (2007) and generalised-entropy
families [Borooah & Mangan 2012] — and warns that the Gini coefficient is invalid
for zero-sum league play [Utt & Fort 2002]; but it stops at the *first and second*
moments of the outcome distribution. The forecasting literature provides the
bridge from strength to per-match outcome probabilities — ordered-probit models
[Goddard & Asimakopoulos 2004; Koning 2000] and strength-block multinomial models
[Basini et al. 2023] — and the nearest analog to our object, Csató & Petróczy
(2024), expresses ex-ante balance as the (normalised) *mean* win probability of
the stronger side, finding, like us, no long-run trend, but for tournament group
stages and at the mean rather than the third moment. The de-vigging literature
supplies our tools and a caution: the multiplicative method ignores the
favourite–longshot structure [Clarke, Kovalchik & Ingram 2017], Shin's method is
strong but not universally dominant [Shin 1993; Štrumbelj 2014], and each price is
formally consistent with a distribution of true probabilities rather than a single
one [Nash 2018] — a defence against the charge that "odds are probabilities by
definition." To our knowledge no prior work treats the **skewness (third moment)**
of the de-vigged 1X2 distribution as a league-level invariant, formalises
skewness = *f*(competitiveness), or tests its cross-league constancy with explicit
third-moment inference while confronting de-vig circularity head-on. That is the
gap we fill.

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
single parameter *z* estimates the proportion of informed ("insider") money
[Štrumbelj 2014]; we use multiplicative (proportional) and power de-vigging as
robustness, and report sensitivity across all three rather than claiming
unconditional superiority for any (Štrumbelj's strong dominance claim for Shin
does not hold universally). The mean 1X2 overround is 1.067 and the mean Shin *z*
is 0.034.

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
against the law.

The same holds for the canonical, size-robust competitive-balance indices used in
the sports-economics literature, computed from final standings alone — and hence
independent of both the odds *and* our Elo. Following Utt & Fort (2002) we avoid
the Gini coefficient (invalid for zero-sum league play) and use the Noll-Scully
ratio, the size-normalised HHI* of Owen, Ryan & Weatherston (2007), and the
Theil/GE(1) entropy of Borooah & Mangan (2012). All three reproduce the law with
the predicted sign — more imbalance, lower skewness: skewness vs Noll-Scully
r = −0.625 [−0.83, −0.36], vs HHI* −0.593, vs Theil −0.478. This yields a
coherent errors-in-variables ladder, from the (circular) odds at −0.90, through
match-level Elo at +0.83, to season-level standings indices at 0.48–0.63: the
closer the proxy sits to the per-match win-probability distribution that
mechanically generates skewness, the stronger the measured relation. The
asymmetry of market returns is inherited from the competitive structure of the
league.

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

### 4.6 Beyond the third moment: shape invariance (Figure 6, Figure 7)

The mechanical decomposition of §3.3 generalises to every order. A two-point bet
has closed-form central moments of all orders,
m_k = oᵏ · p(1−p) · [(1−p)^{k−1} + (−1)ᵏ p^{k−1}], and the mixture's k-th central
moment follows from the law of total moments, M_k = E_i[Σ_j C(k,j) m_{j,i} dᵢ^{k−j}]
with dᵢ = μᵢ − μ. Computing this through the sixth order, the **within-match
fraction is ≈ 1 at every order** (m₂ +1.00, m₃ +1.03, m₄ +1.01, m₅ +1.03, m₆ +1.02):
not only the skewness but the entire shape of the implied distribution is the
algebraic image of the win-probability distribution, with negligible contribution
from how matches are pooled. Globally the implied favourite distribution has
variance 0.99, skewness +0.236, excess kurtosis **−1.683** (the short-tailed
signature of a mixture of Bernoullis), with bootstrap standard errors ≈ 0.001.

The ordered-probit model of §5 predicts not just the third moment but each moment
of a league from its mean favourite probability: across the thirty-eight leagues,
**variance r = +0.99, skewness r = +0.90, excess kurtosis r = +0.89** (Figure 6).
The standardised moments (skewness, kurtosis) match in both level and ordering;
the raw variance matches in ordering with a multiplicative level offset induced by
the overround (real odds o < 1/p). The skewness invariance is thus a corollary of
a stronger **shape invariance**: the whole implied distribution is a single
function of league competitiveness.

A distribution-collapse test confirms this directly. Standardising favourite
returns within each league (removing location and scale) and comparing leagues
pairwise, the median Kolmogorov–Smirnov statistic is **0.474** — the standardised
shape genuinely differs across leagues, because skewness varies with the league.
But conditioning on competitiveness — comparing each league against the rest
*within* narrow bins of favourite probability — the median KS statistic collapses
to **0.059**, an 87% reduction (Figure 7). (With samples this large the KS p-value
saturates and is uninformative; the statistic itself is the relevant effect size.)
Once competitiveness is fixed, league identity adds essentially nothing: the
distribution collapses, a stylised fact that the shape is a function of
competitiveness and not of the league.

### 4.7 The price of asymmetry: no extra premium, an invariant preference (Figure 8, Figure 9)

If skewness is structural, is it *priced* beyond the mechanical bias? The
favourite's expected return decomposes exactly into a margin term and a
calibration term, r = (p·o − 1) + ((1{win} − p)·o): the first is the vig paid even
under perfect calibration, the second the monetised favourite–longshot bias.
Globally the favourite returns −4.8%, split into **−5.0% margin** and **+0.15%
FLB** — the loss is almost entirely the bookmaker's margin, and the favourite side
of the longshot bias is small and positive (favourites are mildly underpriced).
Decomposing the FLB term into a mechanical level (the global FLB-vs-probability
curve applied to each league's probability composition) and a league residual, the
residual is **uncorrelated with the league's implied skewness** (r = +0.11,
95% CI [−0.20, +0.38]); so are the total FLB (−0.04) and the margin (−0.29). There
is no league-level skewness premium beyond the mechanical bias: the asymmetry is
priced only through the favourite–longshot identity itself, and bookmakers leave no
extra, skewness-linked edge — the asymmetry analogue of the margin orthogonality of
§4.4.

The bias has a behavioural reading. Modelling the proportionally-devigged implied
probability q as the decision weight of the objective probability π through the
Tversky–Kahneman weighting w(p) = p^γ/(p^γ + (1−p)^γ)^{1/γ}, the fit gives
**γ = 0.96 < 1** — the inverse-S that overweights longshots and underweights
favourites (calibration: q = 0.10 vs π = 0.09 for longshots, q = 0.71 vs π = 0.74
for favourites). The new point is that this *preference parameter is itself an
invariant*: across seasons γ has mean 0.955, standard deviation 0.020, and **no
secular trend** (β = +0.0003/yr, Δ over 20 years ≈ +0.006), and across leagues it is
tightly clustered (mean 0.945, sd 0.040), with only a mild association with
competitiveness (r = −0.45). The probability weighting behind the bias is a stable
structural constant, not a moving process — the invariance holds on the preference
side as well as on the risk side [Snowberg & Wolfers 2010; Barberis & Huang 2008].

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

This is not merely a verbal account: the law can be *derived*. Following the
ordered-probit tradition for football outcomes [Goddard & Asimakopoulos 2004;
Koning 2000], let team strengths be Gaussian with within-league dispersion σ_L, so
a match's strength gap is d ~ N(0, 2σ_L²); a latent margin y* = d + h + ε with
home advantage h and standard-normal noise generates (away, draw, home) through a
pair of cut-offs ±c, and the favourite probability is p = max(P_H, P_D, P_A).
Under fair odds the favourite bet has zero mean, so a league's pooled skewness is
the closed functional S(σ_L) = E[m₃(p)] / E[σ²(p)]^{3/2} with σ²(p) = (1 − p)/p and
m₃(p) = (1 − p)(1 − 2p)/p² — a single-peaked (concave) function of the lone
competitiveness parameter σ_L. Calibrating (h, c, σ) once to the pooled marginal
rates (home 0.444, draw 0.264, mean favourite probability 0.499) gives h = 0.22,
c = 0.37, and the resulting curve **predicts each league's third moment from its
first moment (mean favourite probability) at r = +0.90, RMSE 0.024** — less than
half the between-league standard deviation. The thirty-eight leagues lie on the
derived curve (Figure 5): the skewness–competitiveness law is an analytic
consequence of a strength model plus the favourite–longshot identity, not a free
fit.

**The law in closed form (Figure 10).** S(σ_L) need not be simulated. Its two
expectations are one-dimensional Gaussian integrals in the strength gap d, which we
evaluate by adaptive quadrature, partitioning at the gap values where the favourite
identity switches (the kinks of p_fav). The closed-form curve reproduces the
Monte-Carlo estimate to a maximum absolute difference of 0.0015 — the Monte-Carlo
noise floor — over the whole σ_L range, removing all simulation error. The balanced
limit is fully analytic: as σ_L → 0, S(σ_L) → (1 − 2p₀)/√(p₀(1 − p₀)) with
p₀ = Φ(h − c), the per-match identity evaluated at the equilibrium favourite
(p₀ = 0.439, S₀ = +0.245 here), and the leading correction S₂ = +8.4 σ_L² is
positive — skewness rises as a league departs from perfect balance. The curve is
not monotone: it peaks at σ* = 0.12 (S_max = +0.30, mean favourite probability
0.45) and declines thereafter, crossing zero only when one side becomes
overwhelmingly favoured. Because p_fav is piecewise-smooth (kinked where the
favourite changes identity), S(σ_L) is C^∞ but not globally analytic — its Taylor
series about balance has a finite radius, so the closed form is the integral itself
rather than an elementary series. Evaluated exactly, the curve still places the
thirty-eight leagues at r = +0.90.

**Why the within-match term dominates (tail cancellation).** The empirical finding
that M_k ≈ E[m_{k,i}] at every order has a simple cause. Under fair odds the
favourite bet has mean exactly zero, so every deviation dᵢ = μᵢ − μ vanishes and
the law-of-total-moments expansion collapses to M_k = E[m_{k,i}] *identically* —
every cross term carries a factor of some dᵢ. Real odds carry an overround, so the
means are slightly negative rather than zero, but uniformly so: the dᵢ are small
and tightly clustered, and the covariance and between-match terms, being O(E[dᵢ])
and O(E[dᵢ³]), stay near zero (−2.6% and −0.0% of M₃). The mixing of matches cannot
generate asymmetry because the matches barely differ in mean; all the shape comes
from within each two-point bet. A complementary cancellation explains why the
*level* of skewness is insensitive to league composition while the variance is not:
variance is monotone in favourite strength (corr −0.90), so reweighting matches
moves it, whereas the two skewness tails — weak favourites contributing positive
skew, strong favourites negative — offset, leaving aggregate skewness (corr with
strength ≈ −0.2) and its composition nearly decoupled. Stability of the competitive
distribution therefore buys stability of skewness for free.

## 6. Robustness

The central findings are insensitive to analytical choices. The global ex-ante
skewness is 0.224 / 0.236 / 0.263 under power / Shin / multiplicative de-vigging,
while the cross-league law is essentially unchanged (corr −0.906 / −0.900 /
−0.891). The ordering is itself a sanity check: the multiplicative method, which
removes the margin proportionally and so under-corrects the longshot side, returns
the highest skewness, exactly as expected when a de-vig ignores the
favourite–longshot structure [Clarke, Kovalchik & Ingram 2017]. Stationarity is confirmed by both ADF (p < 0.001) and KPSS (p = 0.10)
across window sizes from 500 to 3000 matches and under league-demeaning. The
apparent short-run persistence in overlapping windows (ACF₁ = 0.74) is entirely a
window-overlap artefact: with disjoint windows the series is white noise
(Ljung-Box p = 0.70, ACF₁ = −0.06). The per-match bootstrap benchmark (§4.3)
quantifies how much within-league variation is mere sampling noise. Ex-ante and
ex-post measures agree throughout.

Three adversarial checks close the robustness case. First, the de-vig is
trustworthy and the result does not depend on it: the favourite probability is
near-perfectly calibrated against realised outcomes (Brier reliability term
0.000 globally, with a between-league standard deviation of 0.0003 and no badly
calibrated league or season), and the aggregate skewness ranges only +0.224 to
+0.263 across Shin, multiplicative and power de-vigs, the best-price book, and a
multi-book consensus (Figure 12). Second, composition is not driving the
invariance: rebuilding the global series from only the fifteen leagues present in
all twenty-one seasons leaves the trend flat (β = −0.0001/yr, twenty-year change
−0.003, level +0.243 ± 0.014; Figure 13), so the absence of drift is not an
artefact of a changing league basket. Third, the headline numbers carry honest
confidence intervals: a block-bootstrap that resamples whole seasons (respecting
within-year dependence) gives global skewness +0.236 [+0.232, +0.239] and a
structural-law correlation of −0.90 [−0.92, −0.88] — both comfortably excluding
the null.

The derivation also does not lean on the Gaussian strength assumption (Figure 11).
A match's strength gap is the difference d = rᵢ − rⱼ of two independent team
strengths, which is symmetric about zero for *any* identically distributed strength
law — so asymmetry in the strengths themselves cannot bias the result; only tail
weight can. Replacing the Normal strengths with Student-t (raising the excess
kurtosis of d from ~0 to as much as 36), with a skew-normal (±α), or with a uniform
law, and comparing curves at matched competitiveness (mean favourite probability),
the skewness–competitiveness relationship shifts by at most |ΔS| = 0.03 — smaller
than the between-league standard deviation of 0.05. The skew-normal curves collapse
onto the Gaussian almost exactly, precisely as the symmetry argument predicts, and
the residual movement scales with the kurtosis of d, not its skew. The law is the
geometry of the two-point mixture, not an artefact of normality.

Finally, we guard against a specific confound: if the favourite–longshot bias
itself drifted over the sample — recent work reports a weakening of the bias in
European data [Angelini & De Angelis 2019] — a moving bias could masquerade as
skewness invariance. It does not. Over 2005–2025 the bias barometer (the underdog
return) shows no significant trend (correlation with year +0.27, 95% CI
[−0.23, +0.67]; a faint, non-significant tendency in the reported direction), the
favourite−underdog return spread is flat (corr −0.02), and the favourite's annual
calibration error stays within [−0.004, +0.012]. Ex-ante and ex-post skewness
coincide every year (mean absolute difference 0.015). The invariance is therefore
not an artefact of a time-varying bias; and because skewness is mechanically set
by the probability distribution, it is in any case robust to mild calibration
drift.

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
(the favourite–longshot bias) — and not merely its third moment but its entire
shape, which collapses across leagues once competitiveness is held fixed; its
league-level value is fixed by sporting
competitiveness — a relation that survives an odds-free measure of competitiveness
— and it shows no secular drift within the modern competitive regime that spans
our window. Bookmaker margin is orthogonal
to it, and the identity holds in a second, binary market. No league-level premium
is priced beyond the mechanical bias, and the preference that underlies that bias —
the probability weighting of cumulative prospect theory — is itself a stable
structural constant, showing no drift over twenty years. The market's risk
asymmetry is inherited from the sport, not produced by the pricing of it.

---

## Figures

- **Figure 1.** Favourite–longshot bias: ex-ante and ex-post skewness against
  favourite probability, on the theoretical identity curve (1 − 2p)/√(p(1 − p)).
- **Figure 2.** The structural law: league ex-ante skewness against odds-free
  competitiveness (Elo upset rate), r = +0.83.
- **Figure 3.** Decomposition of the aggregate third moment into within-match,
  covariance and between-match components.
- **Figure 4.** League×season panel: no secular trend within the modern regime.
- **Figure 5.** The derived law: leagues lie on the ordered-probit curve relating
  mean favourite probability to skewness (r = +0.90).
- **Figure 6.** Shape invariance: each league's skewness and excess kurtosis lie on
  the derived ordered-probit curve as a function of mean favourite probability
  (r = +0.90 and +0.89).
- **Figure 7.** Distribution collapse: standardised favourite-return ECDFs differ
  across leagues (left), but collapse onto one another within a fixed band of
  competitiveness (right).
- **Figure 8.** Return decomposition: the mechanical FLB curve by favourite
  probability (left), and total FLB vs league residual against implied skewness —
  no league-level premium beyond the mechanical level (right).
- **Figure 9.** Invariant preference: the fitted Tversky–Kahneman probability
  weighting (left) and γ by season, flat within the between-league band (right).
- **Figure 10.** Closed form: S(σ_L) by exact quadrature reproduces the Monte-Carlo
  curve (left, max |Δ| = 0.0015) and, evaluated exactly, places the leagues on the
  closed curve (right, r = +0.90).
- **Figure 11.** Strength-law robustness: the skewness–competitiveness curve under
  Normal, Student-t (ν = 3, 5), skew-normal and uniform strengths, near-coincident
  when reparametrised by mean favourite probability (max |ΔS| = 0.03).
- **Figure 12.** De-vig reliability: the favourite's reliability diagram (predicted
  vs realised win frequency) and the calibration-error term by league — small and
  stable, so the implied skewness is not a de-vig artefact.
- **Figure 13.** Balanced panel: the global skewness series from the fifteen
  always-present leagues lies flat against the full-basket series — no drift once
  composition is held fixed.

## References

- Andrikogiannopoulou, A. & Papakonstantinou, F. *Estimating Risk Preferences
  from Betting Choices.* Review of Financial Studies.
- Angelini, G. & De Angelis, L. (2019). *Efficiency of online football betting
  markets.* International Journal of Forecasting 35(2):712–721.
- Barberis, N. & Huang, M. (2008). *Stocks as Lotteries.* American Economic Review.
- Basini, L., Tsouli, V., Ntzoufras, I. & Friel, N. (2023). *Assessing competitive
  balance in football via a stochastic block model.* J. Royal Statistical Society
  A 186(3):530–556.
- Borooah, V. & Mangan, J. (2012). *Measuring competitive balance in sports using
  generalized entropy.* Applied Economics 44(9):1093–1102.
- Boyer, B., Mitton, T. & Vorkink, K. (2010). *Expected Idiosyncratic Skewness.*
  Review of Financial Studies.
- Clarke, S., Kovalchik, S. & Ingram, M. (2017). *Adjusting bookmaker's odds to
  allow for overround.* American J. Sports Science 5(6):45–49.
- Constantinou, A. & Fenton, N. (2012). *Solving the problem of inadequate scoring
  rules for assessing probabilistic football forecasts.* J. Quantitative Analysis
  in Sports.
- Csató, L. & Petróczy, D. (2024). *Long-term trends in the competitive balance of
  the UEFA Champions League group stage.* arXiv:2406.19222.
- Garrett, T., Hartley, R. & Coughlin, C. (2006). *Moment preferences and the
  favorite–longshot bias.*
- Goddard, J. & Asimakopoulos, I. (2004). *Forecasting football results and the
  efficiency of fixed-odds betting.* Journal of Forecasting 23(1):51–66.
- Golec, J. & Tamarkin, M. (1998). *Bettors Love Skewness, Not Risk, at the Horse
  Track.* Journal of Political Economy 106(1):205–225.
- Harvey, C. & Siddique, A. (2000). *Conditional Skewness in Asset Pricing Tests.*
  Journal of Finance.
- Koning, R. (2000). *Balance in competition in Dutch soccer.* The Statistician
  (JRSS-D) 49(3):419–431.
- Kraus, A. & Litzenberger, R. (1976). *Skewness Preference and the Valuation of
  Risk Assets.* Journal of Finance.
- Lee, Y. H. & Fort, R. (2012). *Competitive balance: time series lessons from the
  English Premier League.* Scottish J. Political Economy 59(3):266–282.
- Nash, J. (2018). *A formal approach to modelling the characteristics of sports
  betting markets.* arXiv:1811.12516.
- Owen, P. D., Ryan, M. & Weatherston, C. (2007). *Measuring competitive balance
  in professional team sports using the Herfindahl–Hirschman index.* Review of
  Industrial Organization 31:289–302.
- Shin, H. S. (1993). *Measuring the Incidence of Insider Trading in a Market for
  State-Contingent Claims.* Economic Journal 103(420):1141–1153.
- Snowberg, E. & Wolfers, J. (2010). *Explaining the Favorite–Longshot Bias: Is it
  Risk-Love or Misperceptions?* Journal of Political Economy.
- Snowberg, E., Wolfers, J. & Zitzewitz, E. (2013). *Prediction Markets for
  Economic Forecasting.* Handbook of Economic Forecasting.
- Štrumbelj, E. (2014). *On determining probability forecasts from betting odds.*
  International Journal of Forecasting 30(4):934–943.
- Thaler, R. & Ziemba, W. (1988). *Anomalies: Parimutuel Betting Markets.* Journal
  of Economic Perspectives.
- Tversky, A. & Kahneman, D. (1992). *Advances in Prospect Theory: Cumulative
  Representation of Uncertainty.* Journal of Risk and Uncertainty 5(4):297–323.
- Utt, J. & Fort, R. (2002). *Pitfalls to measuring competitive balance with Gini
  coefficients.* J. Sports Economics 3(4):367–373.
- Whelan, K. (2024). *The favourite–longshot bias in fixed-odds football betting.*
  Economica 91(361):188–209.
