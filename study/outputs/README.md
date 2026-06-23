# Data dictionary — derived tables (`study/outputs/`)

This directory holds the **derived, aggregated tables** that underpin every figure
and number in the paper. They are computed by the versioned analysis scripts
(`study/analysis/NN_*.py`) from the frozen match dataset and are **safe to
redistribute** (they contain no row-level licensed data).

## Provenance & how to reproduce

- **Raw source (not redistributed).** Match results and 1X2/Asian/over-under
  closing odds from **football-data.co.uk** (via a normalised mirror), 2000–2025.
  Redistribution of the raw file is restricted by the source's terms of use, so
  `data/matches.csv` is **not** included. Fetch it with `python analysis/00_fetch_data.py`.
- **Frozen snapshot.** The exact analysis snapshot is pinned in
  `study/data/PROVENANCE.json`: SHA256 `6905ca5324df9528…`, 205,435 matches
  (≥2005), 38 leagues, 2005-01-01…2025-06-01. The fetch script **verifies this
  hash** and refuses to proceed if the upstream mirror has drifted.
- **One command.** `cd study && ./run.sh` rebuilds every table here, the
  consolidated `findings.json`, the figures, and the evidence ledger, then audits
  for result drift (`build_lineage.py --check`).
- **Consolidated artifact.** `../../site/src/data/findings.json` is the single
  audited JSON from which all paper statistics and the live widget/API read; its
  blocks mirror the tables below (`leagues`, `moments`, `skewmeter`, `bettype`,
  `diversification`, `collapse`, `premium`, `cpt`, `closed_form`, …).

## Shared conventions

- **`Division`** — football-data league code (e.g. `E0` = England Premier League,
  `F2` = France Ligue 2). See `analysis/export_site_data.py:LEAGUE_NAMES` for names.
- **`n`** — number of matches in the group (count).
- **`season` / `year`** — calendar year of the season start (integer).
- **`skew*` / `exkurt` / `var`** — standardised central moments of the *ex-ante*
  (de-vigged) favourite-bet return distribution; dimensionless. `skew_exante` uses
  Shin de-vigging; `skew_expost` is the realised-return skewness.
- **`p_fav*`** — mean de-vigged favourite win probability (∈ (0,1)); the
  competitiveness axis. **`upset_rate`** — odds-free competitiveness (Elo), ∈ (0,1).
- **`within_frac` / `between_frac` / `wf_m*`** — fraction of a moment contributed
  by the within-match (mechanical) term vs between-match dispersion; dimensionless.
- **`overround` / `over*`** — bookmaker overround (sum of implied probs; 1.0 = fair).
- Probabilities, fractions and correlations are dimensionless; returns are in units
  of stake (a unit bet returns `o−1` on a win, `−1` on a loss).

## Files

| File | Block / figure | Columns (units where non-obvious) |
|---|---|---|
| `exante_by_league.csv` | core, Fig 1 | Division, n, skew_exante, within_frac, between_frac, p_fav_dv_mean, overround_mean, skew_expost |
| `mechanism_elo.csv` | structural law, Fig 2 | + elo_entropy, elo_pfav, **upset_rate** (odds-free comp.), elo_disp (Elo strength dispersion) |
| `moments_by_league.csv` | shape invariance, Fig 6 | var, skew, exkurt, std5, std6, wf_m2…wf_m6 (within fractions), var_pred/skew_pred/exkurt_pred (ordered-probit prediction) |
| `balance_indices.csv` | competitive balance | noll_scully, hhi_star, theil (standings-based balance indices); seasons (count) |
| `panel_league_season.csv` | temporal panel, Fig 4 | Division, season, n, skew_exante, p_fav_dv |
| `balanced_global_series.csv` | balanced panel, Fig 13 | season, n, skew_exante (15 always-present leagues) |
| `var_panel.csv` | VAR experiment, Fig 16 | year, n, skew_exante, p_fav, fav_win_rate, var, **treated** (0/1 VAR-adopted) |
| `collapse_ks.csv` | distribution collapse, Fig 7 | pbin, p_mid, n_leagues, reject_frac, ks_stat_med (KS statistic) |
| `return_decomp.csv` | premium, Fig 8 | ret_mean, vig, flb, flb_syst, residual (return components, units of stake), skew_exante |
| `flb_by_year.csv` | FLB stability | year, ret_dog, ret_fav, flb_spread, skew_expost, calib_err |
| `cpt_by_league.csv`, `cpt_by_season.csv` | preference, Fig 9 | gamma (Tversky–Kahneman probability-weighting γ), p_fav_dv |
| `closed_form_curve.csv` | mechanism, Fig 10 | sigma_L (strength sd), p_fav_exact, skew_exact, skew_mc, skew_smallsigma |
| `force_robustness.csv` | mechanism, Fig 11 | family, max_dS, rms_dS (max/RMS skew shift across strength laws) |
| `model_battery_by_league.csv` | model independence, Fig 14 | skew/pfav for poisson, dixoncoles, btd, elo, emp (each generator) |
| `poisson_crossmodel_by_league.csv` | model independence | skew_poisson, pfav_poisson, skew_emp, pfav_emp |
| `per_league_calibration.csv` | mechanism | home, draw, p_fav (rates), h, c, sigma_L (fitted ordered-probit), skew_model, skew_exante |
| `reliability_by_league.csv` | de-vig reliability, Fig 12 | rel (reliability term), res (resolution), brier (Brier score) |
| `sharp_soft_by_league.csv` | microstructure | skew_soft, skew_sharp, over_soft, over_sharp, d_skew |
| `shin_z_by_league.csv`, `shin_z_by_season.csv` | microstructure | z (Shin insider-trading fraction), overround, p_fav |
| `open_close_by_league.csv` | price discovery, Fig 15 | skew/within/pfav/over at open & close |
| `asian_handicap_by_league.csv` | third market | skew_ah, within_frac, p_fav_ah |
| `overunder.csv` | binary market | p_fav_ou, o_fav_ou, ret_fav_ou, over |
| `entropy_comoment.csv` | co-moment | entropy, skew, p_fav, skew_ou |
| `intraseason_shift_by_league.csv` | within-season | skew_start, skew_end, shift |
| `m3_contribution_by_bin.csv` | tail cancellation | bin, p_mid, skew_match, m3_share (share of aggregate M₃) |
| `team_dominance.csv` | team structure | team, Division, elo, fav_rate, skew_games |
| `hfa_by_year.csv` | home advantage | home_win, fav_home_rate, skew |
| `open_vs_closed.csv` | open vs closed | skew_exante, p_fav_dv_mean, noll_scully, **closed** (0/1) |
| `pre2005_by_league.csv` | pre-2005 regime | pre2005, modern, delta (skew levels), n_pre |
| `bettype_by_league.csv` | every side (Fig f34) | p_fav_mean, **skew_fav / skew_draw / skew_dog** (ex-ante skew of each bet object) |
| `diversification.csv` | portfolio decay | N (bets in portfolio), skew, skew_pred (≈skew/√N), exkurt, std, bet (fav/dog) |
| `inplay_conditional.csv` | in-play resolution | state, share, p0_mean, q_cond, skew_cond |
| `skew_series.csv` | raw realised returns | per-match favourite return (units of stake) |

> Units: all `skew*`, `exkurt`, `var`, `within_frac`, `gamma`, correlations,
> probabilities and balance indices are **dimensionless**; returns and return
> components are in **units of stake**; counts (`n`, `seasons`) are integers.
