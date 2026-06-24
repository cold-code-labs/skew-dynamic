"""Favourite return decomposition (Front C1): margin + mechanical FLB + residual.

The expected return of a unit bet on the favourite decomposes EXACTLY into:
    ret = (p_dv·o − 1)          [VIG: bookmaker margin, under the de-vigged probability
                                 as the truth — what is lost even when well calibrated]
        + ((1{win} − p_dv)·o)   [FLB: outcome-vs-de-vig calibration, monetised]
(because ret = 1{win}·o − 1 and the two terms add up to that). The FLB term further
splits into (i) MECHANICAL LEVEL — what the global FLB(p) curve predicts for the
league's p composition — and (ii) league-specific RESIDUAL. The C1 question: is there
a leftover per-league "premium" (residual) correlated with the implied SKEWNESS, beyond
the FLB's mechanical level?
"""
import numpy as np, pandas as pd


def _win(df):
    return (df.ret_fav.values > 0).astype(float)   # favourite won (o>1 ⇒ ret>0)


def decompose_global(df):
    """Global decomposition of the favourite return (exact identity)."""
    win = _win(df); o = df.o_fav.values; p = df.p_fav_dv.values
    ret = df.ret_fav.values
    vig = float((p * o - 1.0).mean())
    flb = float(((win - p) * o).mean())
    return {"ret_mean": float(ret.mean()), "vig": vig, "flb": flb,
            "residual_check": float(ret.mean() - (vig + flb))}   # ≈0


def flb_curve(df, nbins=20):
    """Mechanical FLB curve: contribution (1{win}−p_dv)·o per p_dv bin.
    It is the systematic monetised component of the favourite–longshot bias."""
    d = df[["p_fav_dv", "o_fav", "ret_fav"]].copy()
    d["contrib"] = ((d.ret_fav > 0).astype(float) - d.p_fav_dv) * d.o_fav
    d["b"] = pd.qcut(d.p_fav_dv, nbins, duplicates="drop")
    return (d.groupby("b", observed=True)
             .agg(p=("p_fav_dv", "mean"), flb=("contrib", "mean"), n=("contrib", "size"))
             .reset_index(drop=True))


def decompose_by_league(df, min_n=2000, nbins=20):
    """Per league: ret = vig + flb; flb = systematic (global curve applied to the
    league's p composition) + residual. The residual is the candidate "premium"."""
    cur = flb_curve(df, nbins)
    order = np.argsort(cur.p.values)
    xs, ys = cur.p.values[order], cur.flb.values[order]
    d = df.copy()
    d["_pred_flb"] = np.interp(d.p_fav_dv.values, xs, ys)   # mechanical level per match
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        win = (g.ret_fav.values > 0).astype(float)
        o = g.o_fav.values; p = g.p_fav_dv.values
        vig = float((p * o - 1.0).mean())
        flb = float(((win - p) * o).mean())
        syst = float(g._pred_flb.mean())
        rows.append({"Division": lg, "n": int(len(g)), "p_fav_dv": float(p.mean()),
                     "ret_mean": float(g.ret_fav.mean()), "vig": vig,
                     "flb": flb, "flb_syst": syst, "residual": flb - syst})
    return pd.DataFrame(rows)
