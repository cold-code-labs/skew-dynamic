"""Fronts L/M/N — terminal utilities over the SAME dataset:

  L  secular home advantage (HFA) vs skewness invariance.
  M  realised tail risk (VaR/CVaR/max drawdown) of the strategies.
  N  entropy (competitiveness index) + co-moment across markets (1X2×O/U).
"""
import numpy as np, pandas as pd
from scipy.stats import skew, kurtosis
from . import exante


# ── L — secular home advantage ───────────────────────────────────────────────
def hfa_and_skew_by_year(df):
    """Per year: home win rate (HFA), fraction of favourites that are home teams,
    and the pooled ex-ante skewness. Requires add_exante."""
    d = df.copy(); d["year"] = d.date.dt.year
    P = d[["p_H", "p_D", "p_A"]].to_numpy(float)
    d["fav_home"] = (P.argmax(1) == 0).astype(float)
    rows = []
    for y, g in d.groupby("year"):
        if len(g) < 1000:
            continue
        rows.append({"year": int(y), "n": len(g),
                     "home_win": float((g.FTResult == "H").mean()),
                     "fav_home_rate": float(g.fav_home.mean()),
                     "skew": exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"]})
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


# ── M — realised tail risk ───────────────────────────────────────────────────
def tail_metrics(returns, alpha=0.05):
    """Moments + VaR/CVaR (left tail) of a per-bet return series."""
    r = np.asarray(returns, float); r = r[np.isfinite(r)]
    var = float(np.quantile(r, alpha))
    cvar = float(r[r <= var].mean())
    return {"mean": float(r.mean()), "std": float(r.std()), "skew": float(skew(r)),
            "exkurt": float(kurtosis(r)), "var5": var, "cvar5": cvar, "n": len(r)}


def max_drawdown(returns_in_order):
    """Max drawdown of the cumulative P&L (sequential unit bet, given order)."""
    pnl = np.cumsum(np.asarray(returns_in_order, float))
    peak = np.maximum.accumulate(pnl)
    dd = pnl - peak
    i = int(np.argmin(dd))
    return {"max_drawdown": float(dd[i]), "final_pnl": float(pnl[-1]),
            "n": len(pnl)}


# ── N — entropy + cross-market co-moment ──────────────────────────────────────
def shannon_entropy(P):
    """Shannon entropy (nats) of each game's 1X2 distribution (rows of P)."""
    P = np.clip(np.asarray(P, float), 1e-12, 1)
    return -(P * np.log(P)).sum(1)


def entropy_by_league(df, min_n=2000):
    """Mean league entropy (competitiveness: high = more uncertain games) +
    ex-ante skewness of the league."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    d = df.copy(); d["entropy"] = shannon_entropy(P)
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        rows.append({"Division": lg, "n": len(g), "entropy": float(g.entropy.mean()),
                     "skew": exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                     "p_fav": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)
