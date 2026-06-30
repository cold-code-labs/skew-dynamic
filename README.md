<div align="center">

# skew-dynamic

### Structural Invariance of Return Skewness in Football Betting Markets

**An open research study by [Cold Code Labs](https://coldcodelabs.com)**

[![site](https://img.shields.io/badge/site-skew--dynamic.coldcodelabs.com-0b1f3a)](https://skew-dynamic.coldcodelabs.com)
[![license](https://img.shields.io/badge/code-Apache--2.0-blue)](LICENSE)
[![paper](https://img.shields.io/badge/paper-CC--BY--4.0-green)](study/docs/paper/draft.md)
[![reproducible](https://img.shields.io/badge/pipeline-reproducible-brightgreen)](study/run.sh)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20822121-blue)](https://doi.org/10.5281/zenodo.20822121)

</div>

---

## The thesis

The skewness of returns implied by football betting markets is **not a temporal
process — it is a structural invariant.** Three results, one principle:

1. **Mechanical core.** Market skewness is, to within sampling error, **≈100% the
   within-match Bernoulli asymmetry** of the win-probability distribution — the
   algebraic image of the favourite–longshot bias, not an emergent pooling effect
   (ex-ante +0.236 ≈ ex-post +0.230; within-match term +102.6% of the 3rd moment).
2. **Structural law.** A league's skewness level is fixed by its competitiveness —
   and the relation **survives a competitiveness measure built without odds**
   (results-only Elo: skewness vs upset rate *r* = +0.83; standings indices
   −0.48…−0.63). Odds- and results-based structure agree at *r* = 0.91: the market
   merely *reads* the sport.
3. **Invariance.** A league×season panel shows **no secular trend** within the
   modern competitive regime (β = +0.00015/yr, *p* = 0.73; one structural break
   across 38 leagues — COVID-19), and the law is *derived* from an ordered-probit
   strength model (predicts the 3rd moment from the 1st at *r* = +0.90).

> The market's risk asymmetry is **inherited from the competitive structure of the
> sport, not produced by pricing.**

Sample: **205,435 matches · 38 leagues · 2005–2025** (football-data.co.uk),
frozen by content hash.

## Repository

```
study/        the research — fully reproducible Python pipeline
  skewlib/    reusable library (de-vig, ex-ante skewness, Elo, panel, model…)
  analysis/   thin scripts, one per block (00–51)
  docs/       FINDINGS (phase log), METHODOLOGY, LITERATURA, paper/ (draft)
  data/PROVENANCE.json   frozen dataset hash + scope
  run.sh      one command: venv + deps + fetch + all blocks
site/         the showcase frontend (Astro) — skew-dynamic.coldcodelabs.com
```

## Reproduce

```bash
cd study
./run.sh            # venv + deps + dataset + all blocks (figures in outputs/fig)
```

Every reported number regenerates from the frozen dataset (sha256 in
`study/data/PROVENANCE.json`). See [`study/docs/FINDINGS.md`](study/docs/FINDINGS.md)
for the full per-phase log and [`study/docs/METHODOLOGY.md`](study/docs/METHODOLOGY.md)
for methods.

## Annex — the World Cup, live

The same law, taken **out of its own population**: from clubs to national teams,
from market odds to **no odds at all**. A results-only Elo over ~49k internationals
predicts the favourite-bet skewness of every World Cup from 1930 to 2026 — and
**predicted vs realised correlate at +0.998** across favourite-probability buckets,
crossing zero at `p = ½` exactly as `(1−2p)/√(p(1−p))` requires. A pre-registered
ledger freezes the prediction for each upcoming match and reconciles it when the
result lands. It updates during the 2026 tournament. Annex:
[`study/docs/WORLDCUP.md`](study/docs/WORLDCUP.md) · page:
[skew-dynamic.coldcodelabs.com/worldcup](https://skew-dynamic.coldcodelabs.com/worldcup).

```bash
python study/analysis/52_worldcup.py            # the analysis
python study/analysis/export_worldcup_data.py   # regenerate the page data
python study/analysis/predict_worldcup.py       # predict next games + reconcile ledger
```

## Annex — Goals: the over/under ladder

The same law, dialled by the **line** instead of by who's playing. Each total-goals
line is a two-point Over bet with `p = P(total > L)`; sweeping the line sweeps
`(1−2p)/√(p(1−p))` across its **full range** (skew −3.0 → +3.6), far past the
1X2 favourite. The over-probability comes **odds-free** from a Poisson goals model;
the one line with real odds (2.5) anchors it — model **48%** ≈ market **49%** ≈
reality **49%**, calibrated within a point at every line. Annex:
[`study/docs/GOALS.md`](study/docs/GOALS.md) · page:
[skew-dynamic.coldcodelabs.com/goals](https://skew-dynamic.coldcodelabs.com/goals).

```bash
python study/analysis/53_goals_ladder.py        # the ladder + 2.5 anchor
python study/analysis/export_goals_data.py      # regenerate the page data
```

## The paper

Working draft (RSOS target): [`study/docs/paper/draft.md`](study/docs/paper/draft.md).
Literature review: [`study/docs/LITERATURA.md`](study/docs/LITERATURA.md).

## Cite

See [`CITATION.cff`](CITATION.cff), or:

```bibtex
@misc{alves2026skewdynamic,
  title  = {Structural Invariance of Return Skewness in Football Betting Markets},
  author = {Alves, Vitor},
  year   = {2026},
  note   = {Cold Code Labs},
  doi    = {10.5281/zenodo.20822121},
  url    = {https://doi.org/10.5281/zenodo.20822121}
}
```

## License

Code is [Apache-2.0](LICENSE). The paper, figures and written findings are
[CC-BY-4.0](LICENSE-PAPER). Match data is © football-data.co.uk under their terms.

<div align="center">

Made with rigour by **Cold Code Labs** · [coldcodelabs.com](https://coldcodelabs.com)

</div>
