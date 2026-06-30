# Annex — The structural skewness law at the World Cup

*Live spin-off of the main study. Block `analysis/52_worldcup.py`, library
`skewlib/worldcup.py`. Updates during the 2026 tournament.*

## The question

The study proves, on **clubs** and with **market odds**, that the return-skewness
of a 1X2 bet on the favourite is fixed by a single quantity — the favourite's
probability `p` — through the closed form `(1−2p)/√(p(1−p))`. This annex takes the
law **out of its own population**: from clubs to **national teams**, from league
to **knockout tournament**, and from odds to **no odds at all**.

It is an out-of-sample test in three senses at once (population, structure,
probability source) — and, with the 2026 World Cup under way, a **live** one.

## How

- **Data:** `martj42/international_results` (public, ~49k international games,
  1872→today). No odds — only scores. Includes the 2026 World Cup in near real time.
- **Model (no odds):** the `skewlib/elo.py` engine from Block W2 — a chronological
  Elo over **all** internationals (each team's rating travels across friendlies,
  qualifiers and World Cups) + an MNLogit map `rating-diff → (P_home, P_draw,
  P_away)`, calibrated on results. Home advantage is **zeroed at neutral venues**
  (`neutral=True`), the norm at the World Cup.
- **The bet:** 1 unit on the Elo favourite (the most likely outcome). With no
  market we use **fair** odds `o = 1/p` (zero EV) — so the predicted skewness is
  purely the two-point shape, and the realised one is the empirical skew of the
  return.

## The result (the main validation)

**Predicted** skewness (structural, via the Elo `p_fav`) × **realised**, by
`p_fav` bucket, over all World Cups (large N per bucket → the 3rd moment stabilises):

| favourite p | games | win rate | predicted skew | realised skew |
|---|---|---|---|---|
| 0.39 | 200 | 43% | +0.46 | +0.29 |
| 0.45 | 170 | 49% | +0.22 | +0.06 |
| 0.51 | 151 | 54% | −0.03 | −0.16 |
| 0.58 | 200 | 59% | −0.30 | −0.33 |
| 0.71 | 316 | 71% | −0.83 | −0.84 |

**`corr(predicted, realised) = +0.998`.** Monotonic, crossing zero at `p ≈ ½`
exactly where `(1−2p)=0`, and in the most lopsided bucket −0.827 predicted against
−0.837 realised. No fitting, no odds. The **win rate ≈ p** column attests that the
odds-free Elo is well calibrated on real World Cup outcomes — that is what sustains
the skewness prediction.

Overall pool: predicted **+0.129**, realised **+0.051** (bootCI [−0.056, +0.152] —
contains the predicted value). Across editions, `corr(p_fav, predicted skew) =
−0.688` (the more lopsided the tournament, the more negative the skew). Skewness
**by edition** is noisy by construction (N=17–73 per cup → the 3rd moment is
dominated by sampling); that is why the serious validation is by `p_fav` bucket,
not by edition.

## The forecast (out-of-time)

The honest test: train the Elo **only on games before** the knockout and predict
the bracket's skew without seeing a single result. In the **2022** hold-out (train
through 2022-12-03, 16 knockout games): predicted **+0.065** × realised **−0.125**,
with **44% upsets** — Qatar 2022 was an extremely high-variance tournament, and the
prediction is the structural baseline the chaos departs from (N=16, noisy). It is
exactly the mechanism the cron applies to the **2026 knockout** as soon as it begins.

## The live demonstration

`analysis/predict_worldcup.py` predicts the **next** World Cup games (fixtures
with no score in the dump) and freezes each into an append-only, pre-registered
ledger (`site/src/data/wc_predictions.json`): favourite, `p_fav`, predicted
skewness, fair odds. When the score arrives the row is reconciled (realised filled
in, **prediction never rewritten**). The `/worldcup` page renders an interactive
"next match" card + a live scorecard from `wc_live.json`.

## Market overlay — model vs market (Box A / Box B), page `/odds`

The odds-free Elo gives a probability for each favourite bet *without ever seeing a
price*. A real bookmaker gives one too. `/odds` puts them side by side:

- **Box A — observer-invariance (descriptive, on-thesis).** De-vig a real published
  3-way line (Shin) → the market's fair `p` for the *same* bet (the model's favourite
  pick). Apply the law `(1−2p)/√(p(1−p))` to each. The claim: **both** the model's
  `(p, skew)` and the market's land on the *same* curve — they differ only in *where*.
  Agreement (rank corr of the two `p`'s, **0.998** over the first three) is the
  headline: the odds-free engine reconstructs what a sportsbook priced. The WC
  analogue of the realised-skew `+0.998`, now against a second *observer*, not frequency.
- **Box B — calibration (honest, weak at small n).** Whose `p` was better calibrated
  vs the outcome: model vs book Brier / log-loss (model 0.272 / 0.740 vs book
  0.300 / 0.813 so far — our humility on the upsets paid). With n = 3, two of them
  penalty lotteries, it is noise; real at n = 16.
- **Box C — value/edge — deliberately NOT crossed.** The gap `p_model − p_book` is a
  betting signal; we display it as a *diagnostic* and stop. Staking it would turn a
  structural law into an alpha claim with a different burden of proof. The thesis's
  credibility rests on it being descriptive history, not a tip sheet.

Book odds are **hand-recorded, sourced, frozen** in `study/wc_book_odds.json`
(American moneyline → decimal at load) — a pre-match snapshot, same discipline as
`wc_manual_results.json`. **No API, no feed.** `skewlib/worldcup.py`: `load_book_odds`
+ `book_pfav`; `predict_worldcup.py` freezes a `book` block per ledger entry (never
rewritten) and emits `triangulation` + `model_vs_book` into `wc_live.json`.

## Reproduce & provenance

```bash
python analysis/52_worldcup.py            # full analysis (stdout + outputs/wc_*.csv)
python analysis/export_worldcup_data.py   # regenerate site/src/data/worldcup.json
python analysis/predict_worldcup.py       # predict next games + reconcile the ledger
```

No API key, no scraping. Each run stamps `outputs/_provenance/52_worldcup.json`
with the git sha + the **dump's sha256** + the date of the last game — provenance
that travels with the live data.

> **Versioning note.** This is a **live** annex: the dataset changes while the cup
> runs. So it stays **out** of the study's frozen drift ledger
> (`build_lineage.py --check`, which is for the frozen `matches.csv`) — instead it
> carries its own fingerprint (sha256 + date) embedded in every regeneration and on
> the `/worldcup` page. The `evidence/worldcup` tag freezes the code + JSON snapshot
> of the publication day. It reuses the football `elo`/`exante` path (still a
> football 1X2 contract, just national teams and results-not-odds), not the
> multi-sport canonical adapter layer.
