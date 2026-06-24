"""Front D — microstructure / price formation (in the frozen dataset):

  D2  sharp vs soft: does the skewness diverge between the MEAN odd (Odd*, softer)
      and the BEST odd (Max*, ~sharp/arb)? Per league.
  D3  Shin z (fraction of informed money) as a SERIES: z per league/year/market,
      its stability and relation to competitiveness/overround.
  D4  ASIAN HANDICAP market (Handi*): a 3rd market (beyond 1X2 and O/U)
      to test the identity (1−2p)/√(p(1−p)). Since the AH balances the match to
      ~50/50, p_fav≈0.5 is predicted ⇒ skew≈0 — same identity, another p regime.
"""
import numpy as np, pandas as pd
from . import devig, exante

ODD = ("OddHome", "OddDraw", "OddAway")
MAX = ("MaxHome", "MaxDraw", "MaxAway")
AH = ("HandiHome", "HandiAway")


# ── D2 — sharp vs soft ───────────────────────────────────────────────────────
def skew_by_book_league(df, min_n=2000):
    """Favourite skewness and overround per league, under Odd* (soft) and Max* (sharp)."""
    ok = df[list(MAX)].notna().all(1) & (df[list(MAX)] > 1.01).all(1)
    d = df[ok]
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        ps, os_, ds = exante.market_skew(g, ODD, method="shin")
        pm, om, dm = exante.market_skew(g, MAX, method="shin")
        rows.append({"Division": lg, "n": len(g),
                     "skew_soft": ds["skew"], "skew_sharp": dm["skew"],
                     "over_soft": float((1 / g[list(ODD)]).sum(1).mean()),
                     "over_sharp": float((1 / g[list(MAX)]).sum(1).mean()),
                     "p_fav": float(g.p_fav_dv.mean())})
    out = pd.DataFrame(rows)
    out["d_skew"] = out.skew_sharp - out.skew_soft
    return out


# ── D3 — Shin z as a series ───────────────────────────────────────────────────
def shin_z_frame(df):
    """Adds shin_z (1X2) per match + overround + season."""
    d = devig.devig_frame(df, method="shin", cols=ODD)
    d["season"] = d.date.dt.year
    return d


def z_by(d, col, min_n=2000):
    """Mean z (informed money) + overround + competitiveness per group."""
    rows = []
    for key, g in d.groupby(col):
        if len(g) < min_n:
            continue
        rows.append({col: key, "n": len(g), "z": float(g.shin_z.mean()),
                     "overround": float(g.overround.mean()),
                     "p_fav": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


# ── D4 — Asian handicap (3rd market) ──────────────────────────────────────────
def prep_ah(df, method="shin"):
    """De-vigs the 2-way AH market (HandiHome/HandiAway) and builds the bet on the
    favourite (lowest odd). Filters the -99.9 sentinel line and invalid odds.
    Returns p_fav_ah, o_fav_ah, per-match skew and the realised outcome when
    unambiguous (whole/half lines; skips quarter lines, which give a half-win)."""
    d = df.copy()
    d = d[(d.HandiSize > -50) & d[list(AH)].notna().all(1)
          & (d[list(AH)] > 1.01).all(1)].reset_index(drop=True)
    O = d[list(AH)].to_numpy(float)
    r = 1.0 / O; bsum = r.sum(1)
    if method == "shin":
        z = np.zeros(len(r)); vig = bsum > 1.0
        if vig.any():
            z[vig] = devig._shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        P = np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
    else:
        P = r / bsum[:, None]
    d["p_home_ah"], d["p_away_ah"] = P[:, 0], P[:, 1]
    d["overround_ah"] = bsum
    fav_home = O[:, 0] <= O[:, 1]
    d["o_fav_ah"] = np.where(fav_home, O[:, 0], O[:, 1])
    d["p_fav_ah"] = np.where(fav_home, d.p_home_ah, d.p_away_ah)
    d["skew_ah_match"] = exante.per_match_skew(d.p_fav_ah.values)

    # realised: goal margin adjusted by the line (sign: HOME handicap)
    gd = pd.to_numeric(d.FTHome, errors="coerce") - pd.to_numeric(d.FTAway, errors="coerce")
    adj = gd + d.HandiSize                     # >0 home covers, <0 away covers, 0 push
    quarter = (np.abs(d.HandiSize * 2) % 1) > 0.1      # quarter line → skip
    home_cover = adj > 0
    settle = (~quarter) & (adj != 0)
    win_fav = np.where(fav_home, home_cover, ~home_cover)
    d["ah_settled"] = settle
    d["ret_fav_ah"] = np.where(win_fav, d.o_fav_ah - 1.0, -1.0)
    return d


def ah_league(d, min_n=2000):
    """Pooled ex-ante AH favourite skewness per league."""
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        dd = exante.pooled_skew(g.p_fav_ah.values, g.o_fav_ah.values)
        rows.append({"Division": lg, "n": len(g), "skew_ah": dd["skew"],
                     "within_frac": dd["within_frac"],
                     "p_fav_ah": float(g.p_fav_ah.mean())})
    return pd.DataFrame(rows)
