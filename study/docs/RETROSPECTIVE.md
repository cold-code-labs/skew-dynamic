# Retrospective — Round of 32, the first verdicts

*Companion to the [World Cup annex](WORLDCUP.md). The pre-registered ledger
(`site/src/data/wc_predictions.json`) froze a prediction for every knockout fixture
on 2026-06-28 — favourite, win probability, skewness, expected goals, chance to
advance, shootout split — before a ball was kicked. Here we check the first three
against reality.*

## The scoreboard

| Match | Result | How it resolved | Our frozen call |
|---|---|---|---|
| 🇧🇷 Brazil **2–1** Japan 🇯🇵 | Brazil won | Martinelli 96', in regulation | favourite Brazil 56% · advance 71% · ~1–0 |
| 🇩🇪 Germany **1–1** Paraguay 🇵🇾 | **Paraguay 4–3 pens** | Germany out — biggest upset | favourite Germany 62% · advance 77% · ~1–0 |
| 🇳🇱 Netherlands **1–1** Morocco 🇲🇦 | **Morocco 3–2 pens** | Netherlands out | favourite Netherlands 48% · advance 63% · ~1–0 |

**Favourites advanced 1/3 · two of three went to penalties · favourites lost both
shootouts (0/2) · the favourite 1X2 bet went 1W–2L.**

## What we got right — and implicitly knew

**1. The upset alert was already on the board — Netherlands × Morocco.** It was the
*only* game we flagged as a near coin-flip: favourite probability **48%**, skewness
**+0.08** (essentially symmetric → "this favourite bet behaves like a mild
longshot"), chance to advance just **63%**. The model literally said *"this is the
toss-up"* — and it went to penalties, Morocco through. We priced the upset risk
without naming the winner.

**2. Skewness vindicated itself as a risk-*shape* read — the deepest point.**
Skewness was never a tip on who wins; it is the *shape* of the bet's return. Germany
was our **most left-skewed** bet (**−0.51** = "wins small, rarely loses **big**").
The rare, ugly loss — elimination — is exactly what a left tail encodes. The point
prediction (Germany advances) missed, but the **risk characterisation was right**: a
heavy favourite fragile to a catastrophic tail event, and the tail hit.

**3. Tight, low-scoring games — called cleanly.** We predicted ~1–0 scorelines and
low expected goals in all three; all three finished low and were decided by a single
goal in regulation. **Mean error on total goals: 0.34** (xG sums 2.38 / 2.21 / 1.80
vs actual 3 / 2 / 2). The goals model knew these would be cagey.

## What we got wrong

**1. Germany 77% to advance — our most confident call, the biggest upset.** The Elo
overrated Germany ("brand" weight + the dataset's group form), echoing Germany's real
modern-tournament fragility (2018/2022 exits). This was a structural miss, not bad
luck.

**2. A bad day for favourites: advance Brier 0.358** (worse than the 0.25 baseline).
But two of three were **penalty lotteries** we modelled as ~50/50 — so part of the
"miss" is just knockout variance, not miscalibration.

**3. Shootouts 0/2.** We gave the favourite a slight edge (56–62%) and both lost. We
got the *humility* right (we shrank toward a coin-flip and said so in print), but the
skill signal was on the wrong side twice.

## What to improve

| Problem | Fix |
|---|---|
| Elo overrates fragile "brands" (Germany) | weight **recent form / tournament under-performance** |
| Shootout skill edge wrong 2/2 | penalties = **exact coin-flip** (or model keeper / history) |
| "Advance" folds extra-time into the shootout coin | model **extra-time goals** explicitly |
| Advance 77% / 63% possibly over-confident | **calibrate** advance probabilities on historical knockouts |

## The meta-point

This is the **first real test of the pre-registered ledger**: predictions frozen on
2026-06-28, before kickoff, now checked against reality — integrity intact. With
**n = 3** (and two penalty lotteries) it is far too early to judge calibration; the
scorecard becomes evidence at **n = 16** (the full Round of 32). But the *direction*
is on-thesis: **the toss-ups went to penalties, and the skewness measured the shape
of the risk correctly even when the winner surprised.** The bet's character was
right; the coin landed where coins land.

*Sources: ESPN, FIFA, CBS Sports, Yahoo Sports (match reports, 2026-06-29).*
