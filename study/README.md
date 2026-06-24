# Skewness Stability in Football Betting Markets

Empirical study on the **temporal stability of the asymmetry (skewness)** of the
distribution of implied returns in football betting markets.

**Thesis:** market skewness is not a dynamic process — it is a **structural
invariant**. Each league has its own skewness level, fixed in time, determined
by its competitiveness. The observed fluctuation is pure sampling noise. The
asymmetry is a property of the sporting generator, exogenous to the bookmakers'
pricing.

## Data

Multi-league dataset 2000–2025 (~230k matches, 38 leagues) with average and
maximum market 1X2 odds. Study window: ≥2005 (odds coverage ~100%),
205,435 matches. See `analysis/00_fetch_data.py`. The canonical source is
football-data.co.uk — on your own infra, stack all seasons/leagues.

> `data/` is not versioned (see `.gitignore`). Run the fetcher or point
> `skewlib/config.py:DATA_PATH` to your dump.

## Structure

```
skewlib/              reusable module
  config.py           parameters (window, step, study window, de-vig, paths)
  io.py               loading + cleaning
  returns.py          ex-post returns (favourite, underdog, Max*, demeaned)
  series.py           sliding skewness series + bootstrap
  stats.py            stationarity, i.i.d., breaks, bootstrap_corr, ols
  decompose.py        decomposition by strategy / odds band / league
  devig.py            1X2 de-vigging (multiplicative / Shin / power)
  exante.py           ex-ante (implied) skewness + total cumulants [primary object]
  elo.py              results-only Elo → odds-free competitiveness
  panel.py            league×season panel, trend, variance, COVID, breaks
  overunder.py        over/under 2.5 binary market
  balance.py          standings-based CB indices (Noll-Scully/HHI*/Theil)
  model.py            ordered-probit: derivation skewness=f(strength dispersion)
analysis/             thin scripts that import skewlib (one per block)
  00_fetch_data.py    fetches the dataset
  01..06              original Blocks A–F (see docs/FINDINGS.md)
  07_devig_exante.py  W1 — ex-ante skewness + mechanical decomposition
  08_mechanism_elo.py W2 — ODDS-FREE skewness~competitiveness law
  09_panel_temporal.py W3 — temporal invariance (panel, COVID)
  10_overunder.py     W5 — over/under 2.5 binary market
  11_margin_robustness.py W4 — orthogonal margin + de-vig robustness
  13_regimes.py       P1 — intra-regime invariance (breaks, EPL)
  14_balance_indices.py P2 — odds-independent standings-based CB
  15_model.py         P3 — formal derivation + figure F5
  16_flb_stability.py P4 — temporal stability of the FLB (Angelini)
  12_figures.py       paper figures (F1–F4)
docs/                 methodology, findings (phase log), outline + abstract + draft
  LITERATURA.md       literature review (deep-research, verified)
outputs/              generated series, tables, figures (not versioned)
data/PROVENANCE.json  hash + window of the frozen dataset (versioned)
```

## How to run

Full pipeline in one command (creates venv, installs deps, fetches the data and
runs blocks 00→06 in order):

```bash
./run.sh                # everything; --no-fetch skips the download, --no-venv uses the current python
```

Or step by step:

```bash
pip install -r requirements.txt
python analysis/00_fetch_data.py            # fetches data/matches.csv
PYTHONPATH=. python analysis/01_baseline.py # or any 0X_*
```

## Findings (summary)

| Front | Result |
|---|---|
| A–F (original) | hardened stationarity; FLB; white noise; margin=spread; skew=f(league) |
| W1 mechanical | ex-ante skewness ≈ ex-post (+0.236/+0.230); M₃ **+102.6% within-match** (= image of the FLB) |
| W2 odds-free | the law survives: skew~upset +0.83, ~entropy +0.72; corr(Elo,odds)=0.91 |
| W3 temporal | panel with no trend (β=+0.0002/yr, p=0.73); ICC 0.70; COVID corroborates the cause |
| W4 margin | overround 1.067→1.009, skewness +0.236→+0.254 (orthogonal); robust to the de-vig |
| W5 binary | over/under 2.5: the identity holds outside the 1X2 (within 99.6%) |
| P1 regime | only 1 break across 38 leagues (COVID); EPL 0 → **intra-regime** invariance |
| P2 standings CB | odds-independent law: skew~Noll-Scully −0.63, ~HHI* −0.59, ~Theil −0.48 |
| P3 derivation | ordered-probit predicts the 3rd moment from the 1st: r=+0.90, RMSE 0.024 (F5) |
| P4 stable FLB | no drift in the bias (yearly corr +0.27 n.s.); year-on-year calibration intact |

Details and phase log in `docs/FINDINGS.md`; methodology in `docs/METHODOLOGY.md`;
literature in `docs/LITERATURA.md`; paper draft in `docs/paper/draft.md`.
