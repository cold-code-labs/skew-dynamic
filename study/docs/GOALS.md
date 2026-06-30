# Annex — Goals: the over/under ladder

*Spin-off of the main study. Block `analysis/53_goals_ladder.py`, library
`skewlib/goals_ladder.py`. Frozen club dataset.*

## The idea

The study's law `(1−2p)/√(p(1−p))` is dialled, in the main paper, by *who is
playing* (the favourite's strength). The **over/under goals market** dials the same
law by a different knob: **the line**. Each total-goals line L is a two-point Over
bet — you win if `total > L`, with probability `p = P(total > L)`. Sweep the line
and you sweep the law:

- **Low lines** (Over 0.5/1.5) are near-certain — the *favourite* side, deeply
  **negative** skew (a small win almost every match, a rare painful −1).
- **High lines** (Over 4.5/5.5) are longshots — **positive** skew (rarely hits, pays
  big). The market spans p from ~0.92 down to ~0.05, hitting the law's **tails**
  that backing a team never reaches (the 1X2 favourite only spans p ≈ 0.39–0.71).

## How (no extra odds)

We never touch a betting odd for the ladder. The over-probability at each line comes
from a **Poisson goals model**: a per-league-season attack/defence + home Poisson
(`skewlib.goals.fit_rates`, reused from Block 35) gives expected goal rates λ_home,
λ_away per match; the total is `Poisson(λ_home+λ_away)`, so
`p_over(L) = 1 − Poisson.cdf(⌊L⌋, λ_total)`. This is the goals analogue of the World
Cup's Elo→p substitution. The realised side comes straight from actual scores.

## The result

The odds-free model **predicts the over-rate within ≤1.6 percentage points at every
line**, and the bet skewness follows the law from **−3.0** (Over 0.5) to **+3.6**
(Over 5.5); `corr(predicted, realised) = +1.000` across lines.

| line | chance of Over | model says | skew |
|---|---|---|---|
| Over 0.5 | 92% | 92% | −3.1 |
| Over 1.5 | 74% | 72% | −1.1 |
| Over 2.5 | 49% | 48% | +0.0 |
| Over 3.5 | 27% | 28% | +1.0 |
| Over 4.5 | 13% | 14% | +2.2 |
| Over 5.5 | 5% | 6% | +3.9 |

**The anchor.** The only line with real odds — Over/Under 2.5 — confirms the
odds-free model: **model 48% ≈ de-vigged market 49% ≈ realised 49%** (overround
1.067). The model is built from scores alone yet recovers the market's probability.

**A freebie.** The goal-count distribution itself is structurally right-skewed —
mean ≈ 2.64 goals/match, skewness ≈ +0.61 ≈ `1/√mean` (Poisson). The sport's scoring
is skewed by construction, and league scoring rate λ sets how much.

## Reproduce

```bash
python analysis/53_goals_ladder.py        # the ladder + 2.5 anchor (stdout + CSV)
python analysis/export_goals_data.py       # regenerate site/src/data/goals.json
```

The per-league-season Poisson fit takes a couple of minutes; the export caches
per-match λ to `outputs/goals_lambda.csv` so re-runs are instant. The `/goals` page
renders an interactive line slider + the ladder from `goals.json`. Sister annex:
[the World Cup](WORLDCUP.md).
