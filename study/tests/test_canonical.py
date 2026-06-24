"""Tests for the canonical layer — synthetic, NO dataset (run in CI).

Validate the contract and the sport-agnostic core on 3- and 2-outcome markets.
    cd study && python -m pytest tests/test_canonical.py -q
"""
import sys
import pathlib
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from skewlib import canonical  # noqa: E402


def _frame(events, outcomes, roles, sport="x", market="m"):
    """events: list of (odds_dict, winner_outcome). Returns a de-vigged canonical frame."""
    rows = []
    for i, (odds, win) in enumerate(events):
        for oc in outcomes:
            rows.append({"event_id": i, "sport": sport, "market": market,
                         "competition": "L1", "date": pd.Timestamp("2020-01-01"),
                         "outcome": oc, "role": roles[oc], "odds": odds[oc],
                         "p": np.nan, "won": int(oc == win)})
    return canonical.devig(pd.DataFrame(rows), method="shin")


THREE = (["H", "D", "A"], {"H": "home", "D": "draw", "A": "away"})
TWO = (["over", "under"], {"over": "over", "under": "under"})


def test_devig_and_validate_three():
    df = _frame([({"H": 1.5, "D": 4.0, "A": 7.0}, "H"),
                 ({"H": 2.5, "D": 3.2, "A": 2.8}, "A")], *THREE)
    assert canonical.validate(df)
    # Σp ≈ 1 per event; the favourite has the lowest odd
    psum = df.groupby("event_id").p.sum()
    assert np.allclose(psum.values, 1.0, atol=1e-6)


def test_select_fav_dog_draw():
    df = _frame([({"H": 1.5, "D": 4.0, "A": 7.0}, "H"),
                 ({"H": 6.0, "D": 3.5, "A": 1.6}, "A")], *THREE)
    fav = canonical.select(df, "fav")
    dog = canonical.select(df, "dog")
    draw = canonical.select(df, "draw")
    assert len(fav) == len(dog) == 2 and len(draw) == 2
    # event 0: fav=H (lowest odd), dog=A (highest odd)
    assert fav.o.iloc[0] == 1.5 and dog.o.iloc[0] == 7.0
    # event 1: fav=A, dog=H
    assert fav.o.iloc[1] == 1.6 and dog.o.iloc[1] == 6.0


def test_two_outcome_market_no_draw():
    df = _frame([({"over": 1.8, "under": 2.1}, "over"),
                 ({"over": 2.4, "under": 1.6}, "under")], *TWO)
    assert canonical.validate(df)
    sig = canonical.signature(canonical.select(df, "fav"), "fav")
    assert sig is not None and np.isfinite(sig["skew"])
    # no draw role → empty selection → None signature
    assert canonical.signature(canonical.select(df, "draw", draw_role="draw")) is None


def test_validate_catches_bad_frame():
    df = _frame([({"H": 1.5, "D": 4.0, "A": 7.0}, "H")], *THREE)
    bad = df.copy()
    bad.loc[bad.outcome == "D", "won"] = 1          # two winners
    with pytest.raises(AssertionError):
        canonical.validate(bad)
