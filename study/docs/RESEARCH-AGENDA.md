# Research Agenda — open fronts of the thesis

> Technical handoff for future sessions. The central thesis is already **proven
> and reproducible** (see `FINDINGS.md`, blocks 00–16). This doc lists the
> **unexplored** fronts that deepen/attack the thesis, prioritised by payoff×cost.
> Marked `[dataset]` = runs on the current frozen data; `[new data]` = needs an
> external source.

## Proven state (do not re-derive)
- **Mechanical core (W1):** market skewness = E[m₃] of the mixture of two-point
  bets; the law of total cumulants gives **within-match ≈ 100%**, between ≈ 0.
  Per-match identity: `(1−2p)/√(p(1−p))`. Code: `exante.py`.
- **Structural law (W2/P2/P3):** skew_league = f(competitiveness), survives
  odds-free proxies (Elo `elo.py`, standings indices `balance.py`) and is
  **derived** by ordered-probit (`model.py`, predicts the 3rd moment from the 1st, r=0.90).
- **Invariance (W3/P1):** league×season panel with no trend (β≈0), ICC 0.70,
  1 break across 38 leagues (COVID). `panel.py`.
- **Margin orthogonality (W4)** + **binary O/U market (W5)** + **FLB
  stable over time (P4)**.

## Data available in the frozen archive
1X2 (`Odd*` average, `Max*` best), **O/U 2.5** (`Over25/Under25/Max*`),
**Asian handicap** (`HandiSize/HandiHome/HandiAway`), goals (`FTHome/FTAway`,
`HT*`), teams, **pre-computed Elo** (`HomeElo/AwayElo`), form, shots/corners/
cards, `C_*` columns (derived features). **No opening odds** nor other sports —
those fronts need a new source.

---

## Front A — External validity / generalisation  ⭐ biggest payoff
**Hypothesis:** the law skewness=f(competitiveness) and the invariance hold in ANY
sport; the level is a function of the sporting generator's parameters (h, c, σ_L).

- **A1 [new data] Tennis** — clean binary market (no draw), mature Elo, Pinnacle
  odds. The sharpest test of the identity `(1−2p)/√(p(1−p))` and of the invariance.
  Predict the tennis "constant" a priori from `model.py` (h≈0, c=0) and validate.
- **A2 [new data] Basketball** — near 50/50, point spread; the skewness should be
  ~0 and barely variable → a falsification test (high competitiveness ⇒ skew↑?).
- **A3 [dataset+new] Cross-sport meta-law** — collapse all sports onto a SINGLE
  reparametrised curve S(σ_L). If they collapse, the law is universal, not football-only.
- **Build:** a per-sport I/O adapter (`io_<sport>.py`), reusing
  `exante/elo/model` intact (they are sport-agnostic). Source: tennis-data.co.uk,
  basketball odds (Kaggle), Pinnacle archives.

## Front B — Moment structure / full distribution  ✅ DONE (2026-06-23)
**Hypothesis:** not only the 3rd moment — the ENTIRE shape of the implied
distribution is invariant after controlling for competitiveness.
> **Completed** (Phases B1/B2 in `FINDINGS.md`): B1 multi-moment + B2 collapse.
> within_frac ≈1 at all orders; the model predicts var/skew/kurtosis (r=0.99/0.90/0.89);
> collapse conditional on competitiveness (KS 0.47→0.06, −87%). B3 (theorem) in the paper.
> Artefacts: `skewlib/{exante,model,collapse}.py`, `analysis/17_moments.py`,
> `analysis/18_collapse.py`. **Pending in B:** KS adjustment for discretisation (bootstrap
> bands), and collapse of the observed−model RESIDUAL (not only the raw returns).
- **B1** Extend `pooled_skew` → `pooled_moments` (var, skew, **kurtosis**, and
  cumulants 5–6). The ordered-probit (`model.py`) predicts ALL moments; test
  moments 2–4 against the derived curve (multi-moment invariance > skew alone).
- **B2** Distribution collapse: standardise (z-score) the returns per league and
  test whether the standardised distribution is the SAME across leagues
  (pairwise KS/Anderson-Darling) → strong "stylised fact" (statistical-physics style).
- **B3** Formalise the "tail cancellation" (B3 of FINDINGS) as a theorem:
  why within dominates and between→0 in mixtures of two-point distributions.

## Front C — Risk premium / asset-pricing  ✅ C1+C2 DONE (2026-06-23) [dataset]
**Hypothesis:** a skewness premium exists BEYOND the mechanical FLB level, and the
preference parameters (CPT) are themselves invariant.
> **C1+C2 completed** (Phases C1/C2 in `FINDINGS.md`): C1 = return = vig + mechanical
> FLB + residual; the residual does NOT correlate with skewness (r=+0.11, CI includes 0) ⇒
> no per-league premium beyond the mechanical. C2 = TK weighting γ=0.96 (inverse-S),
> **temporally invariant** (β≈0, Δ20yr +0.006) and tight across leagues (sd 0.04).
> Artefacts: `skewlib/{premium,cpt}.py`, `analysis/{19_premium,20_cpt}.py`.
> **Pending in C:** C3 (optimal Kelly/staking under the skewness/CPT structure).
- **C1** Decompose the expected return into: margin (overround) + mechanical FLB
  level + mispricing residual. How much pure "premium" is left over?
- **C2** Fit **Cumulative Prospect Theory** (Barberis-Huang / probability
  weighting) to the per-league FLB curve; test whether the probability-weighting
  params are invariant over time and across leagues (stable preference).
- **C3** ✅ DONE (2026-06-23, Phase C3): Kelly = 0% EV>0 after the margin (no
  growth, echoes C1); the longshot skew term +0.60 vs +0.01 for the favourite = the
  channel through which the FLB survives being EV-negative. `analysis/33_kelly_staking.py`,
  `skewlib/staking.py`.

## Front D — Microstructure / price formation  ✅ D2+D3+D4 DONE (2026-06-23)
> **D2+D3+D4 completed** (Phases D2/D3/D4 in `FINDINGS.md`): D2 = sharp(Max) vs
> soft(Odd) — skew +0.218→+0.238 (Δ +0.020 uniform, leagues corr +0.993, law
> survives −0.876); D3 = Shin z 3.4% global, ≈margin (corr +0.999) and orthogonal
> to competitiveness (−0.04); D4 = Asian handicap (150k matches) p_fav 0.533 →
> skew −0.104 (ex-post −0.117), on the identity r=+0.80 — 3rd independent market.
> Artefacts: `skewlib/microstructure.py`, `analysis/{26_sharp_soft,27_shin_z_series,28_asian_handicap}.py`.
- **D1 [new data] Opening→closing drift** — OUT (needs opening odds).
- **D2** ✅ Sharp vs soft (Odd* average vs Max* best price).
- **D3** ✅ Shin z as a series (league/year vs competitiveness/overround).
- **D4** ✅ Asian handicap market as a 3rd test of the identity.

## Front E — Hardening the derivation (theory)  ✅ E1+E2 DONE (2026-06-23) [dataset]
> **E1+E2 completed** (Phases E1/E2 in `FINDINGS.md`): E1 = `S(σ_L)` by QUADRATURE
> of the Gaussian integral (closed form, max|MC−exact|=0.0015), analytic balanced
> limit `S₀=(1−2p₀)/√(p₀(1−p₀))` with `p₀=Φ(h−c)`, exact peak σ*=0.123, non-monotone
> curve; honest about global non-analyticity (p_fav kinks ⇒ the closed form is the
> integral, not an elementary series); predicts 38 leagues r=+0.903 without noise.
> E2 = law robust to the force (t-Student/skew-normal/uniform): max|ΔS|≤0.032 vs league-sd
> 0.051; `d=rᵢ−rⱼ` symmetric for iid force ⇒ only the tail (kurtosis of d) moves, and little.
> Artefacts: `skewlib/model.py` (league_*_exact, smallsigma_*, force_diff, curve_*),
> `analysis/{21_closed_form,22_force_robustness}.py`. **Pending:** E3.
- **E1** ✅ Closed form of S(σ_L) via the Gaussian integral (quadrature) + near-balance
  expansion. (Was via simulation in `model.league_skew`.)
- **E2** ✅ Robustness of the force distribution (t-Student / skew-normal / uniform).
- **E3** ✅ DONE (2026-06-23, Phase E3): (h,c,σ) calibration PER league, endogenous
  draw cutoff c (corr c↔draw rate +0.91; σ_L↔competitiveness +0.87); the law
  survives (per-league skew r=+0.90). `model.calibrate_by_league`,
  `analysis/34_per_league_calibration.py`.

## Front F — Within league / micro  ✅ F1+F2+F3 DONE (2026-06-23) [dataset]
> **F1+F2+F3 completed** (Phases F1/F2/F3 in `FINDINGS.md`): F1 = mild
> intra-season drift (+0.243→+0.229, shift −0.008 ~3–4× < league-sd, predicted by
> p_fav rising at the end); F2 = M₃ by p_fav band (weak favourite +126%, strong −26%;
> per-match skew +0.47→−1.05 on the identity); F3 = dominant clubs pull skew negative
> (Barcelona −1.10), corr(league Elo dispersion, skew) = −0.60. Artefacts:
> `skewlib/intraleague.py`, `analysis/{29_intraseason,30_game_contribution,31_team_decomposition}.py`.
- **F1** ✅ Intra-season seasonality (controlled per league).
- **F2** ✅ Contribution by match competitiveness (decomposition of M₃ by p_fav).
  (Note: "importance" via derby/relegation would require live standings; done
  via match competitiveness, which is the direct mechanical channel.)
- **F3** ✅ Per-team decomposition (Elo dominance → league signature).

## Front G — Adversarial robustness  ✅ G1+G2+G3 DONE (2026-06-23) [dataset]
> **G1+G2+G3 completed** (Phases G1/G2/G3 in `FINDINGS.md`): G1 = Shin de-vig
> calibrated almost perfectly (REL global 0.0000, sd across leagues 0.0003) + skew
> invariant to method/bookmaker (∈[+0.224,+0.263], range 0.039); G2 = strictly
> balanced panel (15 leagues in all 21 seasons) → global series with no
> trend (β=−0.00013/year, level +0.243±0.014, composition confound killed);
> G3 = block-bootstrap over seasons → skew +0.236 CI95 [+0.232,+0.239], law
> corr(skew,p_fav)=−0.90 CI95 [−0.922,−0.876]. Artefacts: `skewlib/adversarial.py`,
> `analysis/{23_devig_reliability,24_balanced_panel,25_block_bootstrap}.py`.
- **G1** ✅ Reliable de-vig (reliability/Brier per league/year) + method/bookmaker invariance.
- **G2** ✅ Strictly BALANCED panel for the GLOBAL series (composition killed).
- **G3** ✅ Block-bootstrap over seasons for CIs of the headline numbers.

## Front H — Natural experiments
- **H1** [new data] Rule changes as competitiveness shocks: adoption of
  3-points-per-win (dates per league), VAR, format/playoff change. OUT (data).
- **H2** ✅ DONE (2026-06-23, Phase H2) [dataset]: MLS (USA, closed) is the most
  balanced by Noll-Scully (1/38), skew at the balanced extreme (+0.16 vs +0.22 for
  open leagues); curve residual −0.06 (~1 sd). Supports open-vs-closed; a full test
  needs + closed leagues (external data). `analysis/32_open_vs_closed.py`.

---

# 2nd ROUND — new fronts on the frozen dataset (2026-06-23)

> The 1st round (A–H) is closed. These fronts explore veins of the SAME dataset
> still untouched (goals `FT*`, half-time `HT*`, portfolio structure, realised
> tail), without any sport or external data. Priority by payoff×cost.

## Front I — Cross-validation of the mechanism (goals model)  ✅ DONE (2026-06-23)
> **Completed** (Phase I): a Poisson of GOALS (attack/defence+home by league-season,
> Skellam→result) reproduces the law. Across 38 leagues: corr(p_fav Poisson, empirical)
> +0.972, corr(skew Poisson, empirical) +0.925; Poisson on the ordered-probit curve
> r=+0.85. Three independent models (latent margin, goals-Poisson, market) on the
> SAME curve ⇒ model-independent mechanism. `skewlib/goals.py`,
> `analysis/35_poisson_crossmodel.py`.

## Front J — Information arrival: half-time → full-time (HT→FT)  ✅ DONE (2026-06-23)
> **Completed** (Phase J): the skewness of the "rest of the match" is the identity in
> the probability conditional on the HT scoreline — favourite behind q=0.14 skew +2.08,
> +2 goals q=0.95 skew −3.91; martingale calibration |p0−q|=0.0035. The mechanical
> core is DYNAMIC (holds at every information state). `skewlib/inplay.py`, `analysis/36_inplay_resolution.py`.

## Front K — Diversification / portfolio  ✅ DONE (2026-06-23)
> **Completed** (Phase K): single-bet skew favourite +0.230 / longshot +2.254; the
> mean return of N bets decays as skew/√N → ~Gaussian in ~6 bets (favourite) /
> ~509 (longshot). The asymmetry is a SINGLE-bet phenomenon; the FLB survives via
> the concentrated recreational bettor. `skewlib/portfolio.py`, `analysis/37_diversification.py`.

## Front L — Secular home advantage vs invariance  ✅ DONE (2026-06-23)
> **Completed** (Phase L): HFA falls (home win 0.449→0.431, Δ20yr −0.027) but the
> skew stays flat (Δ20yr −0.002); corr(HFA,skew) −0.24 (CI includes 0). Home-advantage
> confound closed. `skewlib/extras.py:hfa_and_skew_by_year`, `analysis/38_home_advantage.py`.

## Front M — Realised tail risk (VaR/CVaR/drawdown)  ✅ DONE (2026-06-23)
> **Completed** (Phase M): favourite maxDD −9.9k (skew +0.23, exkurt −1.7); longshot
> maxDD −20.9k (skew +2.25, exkurt +8.2) — the lottery in concrete bankroll risk.
> `skewlib/extras.py:{tail_metrics,max_drawdown}`, `analysis/39_tail_risk.py`.

## Front N — Entropy + cross-market co-moment structure  ✅ DONE (2026-06-23)
> **Completed** (Phase N): 1X2 entropy ↔ skew +0.83 (robust alternative index);
> but the 1X2×O/U co-moment only +0.15 (CI includes 0) = honest NULL — the two
> asymmetries measure different dimensions (who-wins vs goals), not a single latent.
> `skewlib/extras.py:{shannon_entropy,entropy_by_league}`, `analysis/40_entropy_comoment.py`.

---

## How to extend (architecture)
New logic → a function in `skewlib/`, then a thin script `analysis/NN_*.py` that
uses it (do NOT duplicate logic in the script). Parameters only in `config.py`. Run:
`cd study && ./run.sh` (or an isolated block with `PYTHONPATH=. python analysis/NN_*.py`).
After touching the data/result, run `analysis/export_site_data.py` to update the
site. Rigour: non-overlapping windows for inference, bootstrap for the 3rd-order
moment, double ADF+KPSS, report sensitivity.

## Suggested order (payoff×cost)
1. ~~**B1+B2** (multi-moment + collapse)~~ ✅ DONE 2026-06-23 (Phases B1/B2).
2. ~~**C1+C2** (skew premium + invariant CPT)~~ ✅ DONE 2026-06-23 (Phases C1/C2).
3. ~~**E1+E2** (closed form + force robustness)~~ ✅ DONE 2026-06-23 (Phases E1/E2).
4. ~~**G1–G3** (adversarial robustness)~~ ✅ DONE 2026-06-23 (Phases G1/G2/G3).
5. ~~**F1–F3 / D2–D4 / H2 / C3 / E3**~~ ✅ DONE 2026-06-23 (micro/microstructure/
   Kelly/per-league-calibration/open-vs-closed).

> **DATASET EXHAUSTED** (2026-06-23): all fronts that run on the frozen archive
> are DONE (W·P·B·C·E·D·F·G·H2 — 29 phases; see `docs/LINEAGE.md`). Only those
> requiring **external data** remain: Front A (tennis/cross-sport), D1 (opening→closing),
> H1 (rule changes). Vitor's decision: football on the frozen dataset first — fulfilled.
