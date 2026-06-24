"""CANONICAL, sport-agnostic layer — measures and compares the asymmetries of any
betting market (2, 3, … outcomes), of any sport.

The study's core (Bernoulli identity, decomposition, skew-meter) only needs, per
bet, (de-vigged p, market o, won). This layer consumes a CANONICAL table in long
form (one row per event×outcome; see docs/DATA-SCHEMA.md) and exposes betting
object selection + signature, reusing `exante` without duplicating the maths. The
sport-specific part (per-market de-vig, outcome taxonomy, odds-free
competitiveness) lives in the adapters (`skewlib/adapters/`).
"""
import numpy as np
import pandas as pd
from . import exante
from . import devig as _devig

SCHEMA = ["event_id", "sport", "market", "competition", "date",
          "outcome", "role", "odds", "p", "won"]


def validate(df):
    """Checks the canonical contract: columns + per-event invariants (Σp≈1, exactly
    one winner, odds≥1, p∈(0,1)). Raises AssertionError on the 1st violation."""
    miss = [c for c in SCHEMA if c not in df.columns]
    assert not miss, f"missing canonical columns: {miss}"
    assert (df.odds >= 1.0).all(), "there are odds < 1"
    g = df.groupby("event_id")
    psum = g.p.sum()
    bad = psum[(psum - 1.0).abs() > 1e-6]
    assert bad.empty, f"Σp ≠ 1 in {len(bad)} events (e.g.: {bad.index[:3].tolist()})"
    wins = g.won.sum()
    assert (wins == 1).all(), "every event needs exactly one winning outcome"
    assert df.p.between(0, 1).all(), "there are p outside (0,1)"
    return True


def devig(df, method=None):
    """Fills/overwrites `p` by de-vigging the odds per event (vectorised by
    fixed-width market). For the football adapter, the de-vig is delegated to
    `devig.devig_frame` (frozen numbers); here is the generic path for the others."""
    wide = df.pivot(index="event_id", columns="outcome", values="odds")
    P = _devig.devig_odds(wide.to_numpy(float), method)
    pwide = pd.DataFrame(P, index=wide.index, columns=wide.columns)
    pl = pwide.reset_index().melt(id_vars="event_id", var_name="outcome", value_name="p")
    out = df.drop(columns=[c for c in ("p",) if c in df.columns]).merge(
        pl, on=["event_id", "outcome"], how="left")
    return out


# ── betting object selection ─────────────────────────────────────────────────
def select(df, kind, draw_role="draw"):
    """Returns one row per event (competition, date, p, o, won) for the object:
    'fav' = argmax p, 'dog' = argmin p, 'draw' = role == draw_role (empty if the
    sport has no draw)."""
    if kind == "draw":
        sel = df[df.role == draw_role].copy()
    elif kind in ("fav", "dog"):
        idx = (df.groupby("event_id").p.idxmax() if kind == "fav"
               else df.groupby("event_id").p.idxmin())
        sel = df.loc[idx].copy()
    else:
        raise ValueError(f"unknown kind: {kind}")
    return sel.rename(columns={"odds": "o"})[
        ["event_id", "competition", "date", "p", "o", "won"]].reset_index(drop=True)


def signature(sel, label=None):
    """Asymmetry signature (skew/var/exkurt + competitiveness) of an already-made
    selection, via the ex-ante mixture. Reuses exante.pooled_moments (same numbers)."""
    p = sel.p.to_numpy(float); o = sel.o.to_numpy(float)
    if len(p) == 0:
        return None
    m = exante.pooled_moments(p, o, max_order=4)
    return {"label": label, "n": int(len(p)), "skew": m["skew"], "var": m["var"],
            "exkurt": m["exkurt"], "comp": float(p.mean())}


def bettype_by(df, by="competition", kinds=("fav", "draw", "dog"),
               draw_role="draw", min_n=2000):
    """Ex-ante skewness of each betting object, per group (league/tournament) — the
    sport-agnostic generalisation of `exante.bettype_by`. One row per group."""
    rows = []
    for key, g in df.groupby(by, observed=True):
        n_events = g.event_id.nunique()
        if n_events < min_n:
            continue
        row = {by: key, "n": int(n_events)}
        fav = select(g, "fav", draw_role)
        row["p_fav_mean"] = float(fav.p.mean())
        for kind in kinds:
            sel = select(g, kind, draw_role)
            row[f"skew_{kind}"] = (exante.pooled_skew(sel.p.values, sel.o.values)["skew"]
                                   if len(sel) else float("nan"))
        rows.append(row)
    return pd.DataFrame(rows)
