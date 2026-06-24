"""Tests for the tennis adapter — synthetic, NO dataset (run in CI).

Validate the winner/loser → canonical mapping and the favourite-longshot semantics
(favourite = lowest odd; won when the winner was the favourite).
    cd study && python -m pytest tests/test_tennis_adapter.py -q
"""
import sys
import pathlib
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from skewlib import canonical            # noqa: E402
from skewlib.adapters import tennis      # noqa: E402


def _raw():
    """Raw tennis-data-like data. Match 0: favourite won (low W odd).
    Match 1: UPSET — the winner was the longshot (high W odd)."""
    return pd.DataFrame({
        "Date": ["2020-01-06", "2020-01-07"],
        "Series": ["ATP250", "Grand Slam"],
        "Surface": ["Hard", "Clay"],
        "Winner": ["Player A", "Player D"],
        "Loser": ["Player B", "Player C"],
        "B365W": [1.30, 4.50],     # winner's odd
        "B365L": [3.50, 1.22],     # loser's odd
    })


def test_to_canonical_schema_and_invariants():
    can = tennis.to_canonical(_raw())
    assert canonical.validate(can)
    assert set(can.outcome) == {"winner", "loser"}
    assert can.market.iloc[0] == "match_odds" and can.sport.iloc[0] == "tennis"
    # 2 events × 2 outcomes
    assert len(can) == 4 and can.event_id.nunique() == 2


def test_favourite_longshot_semantics():
    can = tennis.to_canonical(_raw())
    fav = canonical.select(can, "fav")        # lowest odd per event
    # event 0: favourite = winner (odd 1.30) → favourite bet WON (won=1)
    e0 = fav[fav.event_id == 0].iloc[0]
    assert e0.o == 1.30 and e0.won == 1
    # event 1: favourite = loser (odd 1.22) → favourite LOST (upset, won=0)
    e1 = fav[fav.event_id == 1].iloc[0]
    assert e1.o == 1.22 and e1.won == 0
    # no draw object
    assert tennis.DRAW_ROLE is None
    assert canonical.signature(canonical.select(can, "draw", draw_role="draw")) is None


def test_signature_runs_on_two_outcomes():
    can = tennis.to_canonical(_raw())
    sig = canonical.signature(canonical.select(can, "fav"), "fav")
    assert sig is not None and np.isfinite(sig["skew"]) and sig["n"] == 2
