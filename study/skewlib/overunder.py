"""Over/under 2.5 goals market — CLEAN binary test of the mechanical identity.

A 2-outcome market (no draw): the skewness of a unit bet depends ONLY on the
probability p of the side bet — exactly (1-2p)/√(p(1-p)). It is the sharpest case
of the W1 core, without the 3-way complication of the 1X2. The outcome is
observable from goals (over = FTHome+FTAway ≥ 3), so ex-ante and ex-post can be
compared directly.
"""
import numpy as np, pandas as pd
from . import devig

OU = ("Over25", "Under25")
OU_MAX = ("MaxOver25", "MaxUnder25")


def prep(df, cols=OU, method="shin"):
    """De-vigs the O/U 2.5 market and builds the bet on the favourite (lowest-odd side).

    Adds: p_over, p_under, overround, over (realised), p_fav_ou, o_fav_ou,
    ret_fav_ou (ex-post return). Vectorised de-vig (Shin or multiplicative).
    """
    d = df.copy()
    d["goals"] = pd.to_numeric(d.FTHome, errors="coerce") + pd.to_numeric(d.FTAway, errors="coerce")
    d = d.dropna(subset=[*cols, "goals"])
    d = d[(d[cols[0]] > 1.01) & (d[cols[1]] > 1.01)].reset_index(drop=True)

    O = d[list(cols)].to_numpy(float)
    r = 1.0 / O
    bsum = r.sum(1)
    if method == "shin":
        z = np.zeros(len(r)); vig = bsum > 1.0
        if vig.any():
            z[vig] = devig._shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        P = np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
        d["shin_z"] = z
    else:
        P = r / bsum[:, None]

    d["p_over"], d["p_under"] = P[:, 0], P[:, 1]
    d["overround"] = bsum
    d["over"] = (d.goals >= 3).astype(int)

    fav_over = O[:, 0] <= O[:, 1]                       # favourite = lowest odd
    d["o_fav_ou"] = np.where(fav_over, O[:, 0], O[:, 1])
    d["p_fav_ou"] = np.where(fav_over, d.p_over, d.p_under)
    win = np.where(fav_over, d.over == 1, d.over == 0)
    d["ret_fav_ou"] = np.where(win, d.o_fav_ou - 1.0, -1.0)
    return d
