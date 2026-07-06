# Spike O0 — third-observer source audit (Transfermarkt)

> 2026-07-06. Verdict: **GO**. Source: `dcaribou/transfermarkt-datasets`
> (Kaggle mirror `davidcariboo/player-scores`), **CC0-1.0** (public domain),
> weekly refresh, OSS pipeline. Direct download, **no account needed**:
> `https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/transfermarkt-datasets.duckdb`
> (~200 MB DuckDB; keep in `data/`, gitignored — same posture as every raw dump).

## Coverage

- **Games:** 88,943 across 70 competitions, seasons 2005–2025; dense from 2012.
- **Lineups (`game_lineups`):** usable from **2013** — ≥95% of games carry a full
  starting XI per side from 2013-14 onward. This sets the evaluation era.
- **Valuations (`player_valuations`):** 400k+ rows, dense from ~2011;
  20k+ players covered per recent year.
- **Scope caveat:** **first tiers only** (31 domestic leagues). None of our
  second/third tiers (E1–E3, EC, SP2, I2, F2, D2, SC1–SC3) nor IRL/FIN/CHN.

## Join vs the frozen archive (matches.csv, 2013+)

24 of our 38 divisions map to a TM first tier (`DIV2COMP` below) = **84,091
frozen matches** in the lineup era. Naive-normalised name match rates:

- **79–100%**: E0, SP1, I1 (100%), F1, D1, N1, P1, B1, T1, G1, SC0, USA, DEN, SUI
  → a small hand-curated mapping table (the `fdcanon.py` precedent) closes these
  to ~100%.
- **28–73%** (ARG, BRA, JAP, MEX, RUS, SWE, NOR, POL, ROM, AUT): mostly an
  artifact — `clubs.domestic_competition_id` reflects *current* membership, so
  relegated clubs drop out of the per-league pool (e.g. RO1 shows 19 clubs vs
  40 frozen teams). **O1 must match against the full `clubs` table**, league
  used only as a tiebreaker.

Realistic O2 sample: the ~14 strong divisions ≈ **45–50k matches** — far above
the per-bucket noise floor (SE(skew) ≈ 0.1 needs ~500/bucket).

## End-to-end sanity

Starting-lineup market value at match date via
`game_lineups → player_valuations` (latest valuation ≤ match date):
Man City **€799M** vs Newcastle **€398M** (2023-08-19), 22/22 starters valued.

## O3 hook (World Cup)

`national_teams` (124 teams) carries `total_market_value` + `fifa_ranking`
directly — the prospective third `p` column for the WC ledger needs no squad
reconstruction for *current* values. Historical national squads would need
Wikipedia squad lists + player join (only if we backtest past WCs).

## DIV2COMP (frozen division → TM competition)

```python
DIV2COMP = {'E0':'GB1','SP1':'ES1','I1':'IT1','F1':'FR1','D1':'L1','N1':'NL1',
 'P1':'PO1','B1':'BE1','T1':'TR1','G1':'GR1','SC0':'SC1','ARG':'ARG1',
 'USA':'MLS1','BRA':'BRA1','JAP':'JAP1','MEX':'MEX1','RUS':'RU1','DEN':'DK1',
 'SWE':'SE1','NOR':'NO1','POL':'PL1','ROM':'RO1','SUI':'C1','AUT':'A1'}
```

## Decisions fixed for O1

1. **State = log matchday starting-lineup market value** (coverage confirmed);
   season squad value only as fallback for pre-2013 or missing lineups.
2. **Evaluation era 2013+**; link (ordered probit) trained on an earlier,
   disjoint slice of the era split — exact split decided in O1.
3. Match clubs globally (not per-league); commit the curated name map,
   never the raw dump.
