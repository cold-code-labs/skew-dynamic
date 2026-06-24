# Literature & Conceptual Anchoring

> Survey (deep-research, Jun 2026) anchoring the thesis: **the skewness of the
> distribution of implied 1X2 returns is a per-league structural invariant, a
> function of competitiveness**. Focus: modelling competitive balance. Each
> source has venue + why it matters. Claims verified adversarially
> (an N-0/N-1 vote indicates robustness).

## Strategic TL;DR

The literature strongly supports **half** of the thesis — the mechanism
`competitiveness → distribution of per-match p → skewness`. But it **contradicts
the strong form** ("constant fixed in time + fluctuation = sampling noise"): the
two best EPL studies (Lee & Fort 2012; Basini et al. 2023) find **real
structural breaks** tied to institutional shocks (Champions League 94/95,
Bosman 95, revenue inequality).

**Recommendation:** reposition from *"fixed constant"* to **"league-specific
structural baseline, stable WITHIN competitive regimes"**. That is the form the
evidence carries; the strong form it does not. Our finding F (the only "break" in
20 years = the dataset growing from 21→37 leagues in 2012) is already compatible
with this — it just needs to be framed as *intra-regime invariance*, not absolute
timelessness.

---

## Axis 1 — Competitive balance measures (PRIMARY)

CB measurement is canonically a **inequality/concentration** problem, and each
index has comparability flaws across leagues of different sizes — critical for
us, since we compare leagues with different numbers of teams.

| Source | Venue | Why it matters |
|---|---|---|
| **Utt & Fort (2002)** | J. Sports Economics 3(4):367-373 | ⚠️ **Gini is invalid for a zero-sum league game**; they recommend **SD of win-pct** for temporal comparison. → *do not use raw Gini* as a competitiveness index. [vote 3-0] |
| **Owen, Ryan & Weatherston (2007)** | Review of Industrial Organization 31:289-302 | Bounds of raw HHI depend on league size; they propose **normalised HHI (HHI\*/dHHI)** for cross-league comparability. → a defensible index for our panel. [3-0] |
| **Borooah & Mangan (2012)** | Applied Economics 44(9):1093-1102 | **Generalised Entropy** family (sensitivity parameter that re-weights parts of the performance distribution). → connects CB to moments/asymmetry of the distribution, a natural bridge to skewness. [3-0] |

**For our W2:** benchmark skewness against a **size-robust** index —
HHI\*/dHHI or SD-of-win-pct (Noll-Scully). **Raw Gini is out** (despite our
current corr −0.83 using it informally — worth re-running with Noll-Scully/HHI\*).

## Axis 1b — From competitiveness to the per-match distribution of p (THE BRIDGE)

Here is the gold: formal machinery already exists that writes the per-match
(home/draw/away) distribution as a function of force/competitiveness — **not** only
the final season ranking. It is the template for deriving `skewness = f(competitiveness)`.

| Source | Venue | Why it matters |
|---|---|---|
| **Csató & Petróczy (2024)** | arXiv:2406.19222 | **Closest analogue to our thesis**: ex-ante CB = (normalised) average win probability of the strongest team, via Elo `W_ij = 1/(1+10^{-(R_i-R_j)/400})`. It is competitiveness expressed as a function over P(strong wins). ⚠️ But it is the **mean**, not the 3rd moment, and the scope is the UCL group stage, not a national league. [3-0] |
| **Basini, Tsouli, Ntzoufras & Friel (2023)** | JRSS-A 186(3):530-556 | **Stochastic block model**: the 1X2 result follows a multinomial whose parameters vary by force block (K×K×3 W/D/L array). → ties competitiveness-in-tiers directly to the 1X2 probabilities. Finds the EPL balanced until ~2003, imbalanced thereafter. [3-0] |
| **Goddard & Asimakopoulos (2004)** | J. Forecasting | **Ordered-probit** maps a latent force variable via 2 cut-offs into away/draw/home. A direct template for the distribution of p from force covariates. [3-0] |
| **Koning (2000)** | The Statistician / JRSS-D 49:419-431 | Ordered-probit of Dutch results used **explicitly to study CB change over time** — a precedent for match-level (not standings-level) CB analysis. [3-0] |

## Axis 1c — Cross-league heterogeneity & temporal stability (COUNTER-EVIDENCE)

⚠️ **Direct confrontation with the strong form of the thesis.** CB is **not**
timeless in the EPL:

| Source | Venue | Finding |
|---|---|---|
| **Lee & Fort (2012)** | Scottish J. Political Economy 59(3):266-282 | **Structural breaks** split the EPL's history into 4 regimes; a sharp drop in the "Modern Period" aligned with Champions League 94/95, revenue inequality and Bosman 95. *Regime change, not noise.* [3-0; tri-causal attribution 2-1] |
| **Basini et al. (2023)** | JRSS-A | EPL balanced until ~2003, "quite imbalanced since then". [3-0] |
| **Csató & Petróczy (2024)** | arXiv:2406.19222 | ✅ **The only strong ally for "fluctuation can be no-trend"**: with better measures, **no long-run trend** in the UCL group stage CB (2003/04–2023/24), overturning earlier studies that saw a decline. But it argues *measurement artefact* > *pure sampling noise*, and it is a tournament, not a national league. [2-1] |

**Implication:** our study must **distinguish a FIXED-per-league skewness
baseline from real regime breaks**. That is exactly what blocks A
(stationarity) and F (forensics of the 2012 break) attack — but the framing must
acknowledge Lee & Fort and Basini head-on.

---

## Axis 2 — FLB → skewness (SUPPORT; the mechanical link)

The favourite-longshot bias is the channel that converts the per-match
distribution of p into skewness in the betting returns.

| Source | Venue | Why it matters |
|---|---|---|
| **Whelan (2024)** | Economica 91(361):188-209 | FLB present in **fixed-odds football markets** (not only pari-mutuel), generated by bettor disagreement + bookmaker risk aversion. → confirms the FLB in our own market. [3-0] |
| **Golec & Tamarkin (1998)** | J. Political Economy 106:205-225 | FLB as a **preference for skewness** — links return skewness to the shape of the bettor's utility, observationally equivalent to risk-love. ⚠️ **Competing interpretation**: skewness may reflect bettor preference / market structure, not (only) "true competitiveness". [3-0] |
| **Snowberg & Wolfers (2010)** | J. Political Economy / NBER WP 15923 | Via compound bets, they find that **probability misperception** (Prospect Theory) drives the FLB, not risk-love. ⚠️ Matters for circularity: de-vigged odds embed *bettor cognition*, not only true p. (Setting: US horse racing, not football.) [3-0] |

> **Football-specific to close (cited in the corroboration, not verified here):**
> Cain, Law & Peel (2000); Direr (2013); **Angelini & De Angelis (2019)** — the
> latter found the FLB **weaker** in recent European data, i.e. *temporal
> variation in the bias itself* that could mask/contaminate our invariance test.
> Worth finding and citing.

## Axis 3 — De-vigging & circularity (SUPPORT; the vulnerability)

The choice of de-vig method **moves the measured skewness directly**, and the
most common method is biased against precisely the signal we study.

| Source | Venue | Why it matters |
|---|---|---|
| **Shin (1993)** | Economic Journal 103(420):1141-1153 | Canonical structural de-vig model: endogenous spread (protection against insiders), separates true p from the margin via parameter `z`. Our primary method. [3-0] |
| **Clarke, Kovalchik & Ingram (2017)** | Am. J. Sports Science 5(6):45-49 | ⚠️ **Multiplicative ignores the FLB** (removes the overround proportionally; longshots should lose a larger share). **Power universally beats multiplicative** and equals/exceeds Shin in 3 datasets. → report **sensitivity across methods**. (Low-tier venue, but uncontradicted.) [3-0] |
| **Štrumbelj (2014)** | Int. J. Forecasting 30(4):934-943 | Shin probabilities > basic normalisation/regression, in fixed-odds **and** exchanges. ⚠️ But the strong claim "Shin dominates EVERY bookmaker/sport pair" was **REFUTED [0-3]** — Shin's advantage shrinks with market size and does not remove all of the FLB (e.g. La Liga). *Do not assert Shin's unconditional superiority.* |
| **Nash (2018)** | arXiv:1811.12516 (preprint) | Formalises: the consensus price `P_C` ~ triangular around the true frequency `P_T`; **corollary: P_T is distributed for each P_C**. → a formal defence against the tautology "odds ARE p by definition", but also a constraint: each odd is consistent with a *distribution* of true competitivenesses. [3-0] |

---

## THE GAP (our original contribution)

The verification **found no paper** that:
1. treats the **skewness (3rd moment)** of the de-vigged 1X2 distribution as the
   league-level invariant (the literature stops at the *mean* — Csató — or the
   *variance*/Noll-Scully);
2. formalises **`skewness = f(competitiveness)`** explicitly;
3. tests **cross-league constancy** with rigorous 3rd-moment / variance-ratio
   inference, facing the **circularity of de-vigging** head-on.

→ That is where the study enters. The methodological bridge (variance-ratio +
3rd-moment bootstrap applied to odds-skewness) is itself a contribution — no one
has tied that machinery to a 3rd-order moment of odds.

## Risks to shield against in the design (criticisms to anticipate)

1. **Circularity / tautology (the most serious).** If "competitiveness" comes
   from the *same* odds that yield the skewness, the corr −0.83 is partly
   tautological. **Defensible design:** measure competitiveness from a source
   **independent of the odds** (HHI\*/Noll-Scully from final standings, or Elo of
   *results* not prices) and skewness from de-vigged odds — and show that the link
   survives. **Immediate action: re-run W2 with odds-independent competitiveness.**
2. **De-vig sensitivity.** Multiplicative vs power vs Shin diverge exactly in the
   longshot tail that drives the skewness → run all 3 and show the corr is not a
   method artefact (we already have `DEVIG_METHOD` parameterised).
3. **Regime change vs invariance.** Acknowledge Lee & Fort / Basini; reposition
   the thesis as **intra-regime** invariance (see TL;DR).
4. **League selection bias + variation in the FLB itself** (Angelini & De Angelis):
   an FLB weakening over time may be confounded with skewness (in)variance.

---

## Datasets to verify (open deliverable — check coverage/licence)

> The survey did **not** validate public availability beyond
> football-data.co.uk. Candidates to check before relying on them:

- **football-data.co.uk extended** — secondary divisions (E1-E3, SP2, I2, D2,
  F2…) beyond the main ones already used; more league coverage for the cross-section.
- **`engsoccerdata` (R package)** — historical results for computing
  HHI/Gini/Noll-Scully per league-season (odds-independent source of
  competitiveness → attacks the circularity).
- **clubelo.com (API)** — per-club Elo for Csató-style ex-ante CB, independent
  of prices.
- **Kaggle "European Soccer Database"** — results + multi-bookmaker odds.
- **Opening vs closing odds** (oddsportal/archives) — enables the
  "opening→closing drift" front from CLAUDE.md (needs opening odds).

## Index of sources (quality)

Primary peer-reviewed: Utt & Fort, Owen et al., Borooah & Mangan, Basini et al.,
Goddard & Asimakopoulos, Koning, Lee & Fort, Whelan, Golec & Tamarkin (via
Snowberg & Wolfers), Snowberg & Wolfers, Shin, Štrumbelj. Preprints: Csató &
Petróczy (peer-review-track), Nash (single-author, not reviewed). Low-tier but
useful: Clarke et al.
