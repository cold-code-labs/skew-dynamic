# Canonical data schema — multi-sport / multi-market

## Why

The core machinery of this study — the ex-ante Bernoulli identity, the
law-of-total-cumulants decomposition, the skew-meter (`measure`, `residual`,
`similar`, the sufficiency ladder) — needs only, **per bet**:

- `p` — the de-vigged (fair) probability of the chosen outcome,
- `o` — the decimal odds offered for it,
- `won` — whether it realized (for ex-post returns).

That triple is **sport-agnostic**. Everything football-specific lives in three
places, which become the *adapter*:

1. **De-vigging** — turning raw odds into fair probabilities. The Shin / power /
   multiplicative math already generalizes to any number of mutually-exclusive
   outcomes (`devig.devig_odds`).
2. **Outcome taxonomy** — which outcomes exist and which is "draw"-like.
   Football 1X2 has three (`home`/`draw`/`away`); tennis match-odds has two
   (`p1`/`p2`, no draw); over/under has two (`over`/`under`).
3. **Odds-free competitiveness** — a results-only competitiveness measure (the
   football Elo upset rate). Optional per sport.

Adding a sport = writing one adapter that emits the canonical table below and
declares its taxonomy. The core never changes.

## The canonical table (tidy long form)

One row per **(event, outcome)**. A canonical frame holds a single *market* (a
fixed set of mutually-exclusive outcomes per event).

| column | type | meaning | constraint |
|---|---|---|---|
| `event_id` | str/int | unique event (match) | — |
| `sport` | str | `football`, `tennis`, … | — |
| `market` | str | `1x2`, `match_odds`, `ou25`, … | one market per frame |
| `competition` | str | league/tournament code (was `Division`) | — |
| `date` | datetime64 | event date | — |
| `outcome` | str | canonical outcome key (`H`/`D`/`A`, `over`/`under`, …) | unique within event |
| `role` | str | semantic role (`home`/`draw`/`away`, `over`/`under`, …) | used for taxonomy/odds-free |
| `odds` | float | decimal odds offered (vig-laden) | ≥ 1 |
| `p` | float | de-vigged fair probability | per event: Σ p ≈ 1, p ∈ (0,1) |
| `won` | int 0/1 | 1 if this outcome realized | exactly one per event |

Units: `p`/`won` dimensionless; `odds` decimal; returns derived as `o−1` on a win,
`−1` on a loss (units of stake).

## The selection layer (`skewlib/canonical.py`)

Sport-agnostic, consumes a canonical frame:

- `validate(df)` — schema + per-event invariants (Σp≈1, one winner, odds≥1).
- `devig(df, method)` — fills `p` per event (vectorized Shin/power/multiplicative).
- `select(df, kind, draw_role="draw")` → per-event `(competition, date, p, o, won)`
  for `kind ∈ {fav, dog, draw}`: **fav** = argmax p, **dog** = argmin p, **draw** =
  the row whose `role == draw_role` (empty if the sport has no draw).
- `signature(sel)` → pooled skew/var/exkurt/competitiveness via `exante.pooled_skew`.
- `bettype_by(df, by="competition", kinds=...)` → per-group skew of each bet object
  (the sport-agnostic generalization of `exante.bettype_by`).

The skew-meter (`skewmeter.measure/residual/similar/...`) already takes `(p, o)`,
so it is reused unchanged on any adapter's output.

## Adapters (`skewlib/adapters/`)

An adapter module exposes:

```python
SPORT      = "football"
MARKET     = "1x2"
OUTCOMES   = ["H", "D", "A"]          # canonical keys, in a stable order
ROLES      = {"H": "home", "D": "draw", "A": "away"}
DRAW_ROLE  = "draw"                    # or None for sports without a draw

def to_canonical(df=None, method=None) -> pd.DataFrame: ...   # emits the table above
def competitiveness(df) -> pd.DataFrame | None: ...           # odds-free, optional
```

**Football (`adapters/football.py`)** delegates de-vigging to the existing
`devig.devig_frame`, so its `p` is **bit-identical to the frozen pipeline** — the
canonical path reproduces `exante.bettype_by` exactly (asserted in
`analysis/47_canonical.py` and `tests/test_canonical.py`). It ships two markets:
1X2 (3 outcomes) and over/under-2.5 (2 outcomes), proving the core handles n ≠ 3.

**Tennis (`adapters/tennis.py`, implemented).** Source: tennis-data.co.uk (ATP/WTA;
fetch with `analysis/00b_fetch_tennis.py`, raw not redistributed). Match-odds market,
two outcomes, no draw:

```python
SPORT="tennis"; MARKET="match_odds"; OUTCOMES=["winner","loser"]
ROLES={"winner":"won","loser":"lost"}; DRAW_ROLE=None
```

Odds are labelled by the realised winner/loser (`B365W`/`B365L`, …), so each match
yields a *winner* outcome (won=1) and a *loser* outcome (won=0); the **favourite**
falls out of `select(...,"fav")` as the lower-odds side — sometimes the winner,
sometimes the loser (an upset). `competition` defaults to the tournament tier
(`Series`/`Tier`) or `Surface`. Draw bets return empty (`DRAW_ROLE is None`).

**Basketball (`adapters/basketball.py`, implemented).** Source:
sportsbookreviewsonline.com (NBA; fetch with `analysis/00c_fetch_basketball.py` via the
stdlib `html.parser`, no extra deps, raw not redistributed). Moneyline market, two
outcomes, no draw:

```python
SPORT="basketball"; MARKET="moneyline"; OUTCOMES=["away","home"]
ROLES={"away":"away","home":"home"}; DRAW_ROLE=None
```

Each game is two source rows (visitor/home); American moneylines are converted to
decimal odds, `won` comes from the final score, and a sane-overround filter drops dirty
rows (spreads that leaked into the ML column, sub-100% books). `competition` defaults to
the NBA `season` (competitive balance varies year to year). Draw bets return empty.

**Adding any sport** is the same three things: a `to_canonical` that emits the table,
a taxonomy (`OUTCOMES`/`ROLES`/`DRAW_ROLE`), and a registry entry — the core never
changes.

## What stays sport-specific (not in the canonical core)

The **mechanism** — the ordered-probit strength model and the closed-form
`skew = f(competitiveness)` law (`model.py`) — is football's 3-outcome structure
(home advantage `h`, draw cutoff `c`). A new sport re-derives or re-fits its own
law; the skew-meter then conditions on that law identically. The canonical layer
is about *measuring and comparing* asymmetries across sports; the generative law
is a per-sport object.
