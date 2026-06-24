"""Front J — information arrival: half-time → full-time (HT→FT). Without opening odds
(D1 out), we use the HALF-TIME result as an information shock. For the PRE-MATCH
favourite, the win probability UPDATES with the HT score, and the implied skewness
of the "rest of the match" is again the identity (1−2q)/√(q(1−q)) in the conditional
probability q. Shows that the mechanical core (W1) is DYNAMIC: it holds at every state
of information, and the favourite's asymmetry RESOLVES as the score moves.
"""
import numpy as np, pandas as pd
from . import exante


def fav_state(df):
    """Subset with valid HT + PRE-MATCH favourite state at half-time:
    fav_is_home, favourite's HT margin, and whether the favourite won at FT."""
    d = df.dropna(subset=["HTHome", "HTAway", "HTResult"]).copy()
    P = d[["p_H", "p_D", "p_A"]].to_numpy(float)
    fav_home = P.argmax(1) == 0
    d["fav_is_home"] = fav_home
    d["ht_fav_margin"] = np.where(fav_home, d.HTHome - d.HTAway, d.HTAway - d.HTHome)
    d["ft_fav_win"] = np.where(fav_home, d.FTResult == "H", d.FTResult == "A").astype(float)
    d["p0"] = d.p_fav_dv
    return d


def ht_bucket(margin):
    """Favourite state at HT: behind / level / ahead by 1 / by 2+."""
    m = np.asarray(margin)
    return np.select([m <= -1, m == 0, m == 1, m >= 2],
                     ["atrás", "empatado", "+1", "+2 ou mais"], default="?")


def conditional_table(d, min_n=500):
    """Per HT favourite state: conditional win probability q (realised) and the
    implied skewness of the 'rest of the match' = identity in q."""
    d = d.copy()
    d["state"] = ht_bucket(d.ht_fav_margin.values)
    order = {"atrás": 0, "empatado": 1, "+1": 2, "+2 ou mais": 3}
    rows = []
    for st, g in d.groupby("state"):
        if len(g) < min_n:
            continue
        q = float(g.ft_fav_win.mean())
        rows.append({"state": st, "n": len(g), "share": len(g) / len(d),
                     "p0_mean": float(g.p0.mean()), "q_cond": q,
                     "skew_cond": float(exante.per_match_skew(np.array([q]))[0])})
    out = pd.DataFrame(rows)
    return out.sort_values("state", key=lambda s: s.map(order)).reset_index(drop=True)


def martingale_check(d, p_edges=(0.0, 0.45, 0.50, 0.55, 1.0)):
    """E[HT conditional q | p0 bin] should come back ≈ p0 (the HT info is a
    martingale refinement of the pre-match probability). Confirms dynamic calibration."""
    d = d.copy()
    d["pb"] = pd.cut(d.p0, list(p_edges))
    rows = []
    for b, g in d.groupby("pb", observed=True):
        if len(g) < 500:
            continue
        rows.append({"p_bin": str(b), "n": len(g), "p0_mean": float(g.p0.mean()),
                     "q_mean": float(g.ft_fav_win.mean())})
    return pd.DataFrame(rows)
