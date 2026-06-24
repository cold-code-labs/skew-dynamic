"""Competitive balance (CB) indices from the STANDINGS — results, without odds.
A source 100% independent of the market → a stronger attack on circularity than
the Elo itself.

We use the canonical, league-SIZE-ROBUST measures recommended by the literature,
avoiding the Gini (Utt & Fort 2002: invalid for a zero-sum game):
  - Noll-Scully  = SD(win%) / idealised SD (0.5/√G)   [dispersion of strength]
  - HHI*         = HHI of wins normalised for N teams (Owen et al. 2007)
  - Theil (GE1)  = generalised entropy of the points (Borooah & Mangan 2012)
All increase with the IMBALANCE (less competitiveness).
"""
import numpy as np, pandas as pd


def season_of(dates):
    """Football season (Aug–May): month ≥ 7 → current year, otherwise year−1."""
    d = pd.to_datetime(dates)
    return np.where(d.dt.month >= 7, d.dt.year, d.dt.year - 1)


def standings(df):
    """Per (Division, season, team): games, win-equivalents (W+0.5D), points."""
    d = df.copy()
    d["season"] = season_of(d.date)
    parts = []
    for team_col, win_res in [("HomeTeam", "H"), ("AwayTeam", "A")]:
        t = d[["Division", "season", team_col, "FTResult"]].rename(columns={team_col: "team"})
        t["w"] = (t.FTResult == win_res).astype(float)
        t["draw"] = (t.FTResult == "D").astype(float)
        parts.append(t[["Division", "season", "team", "w", "draw"]])
    long = pd.concat(parts)
    g = long.groupby(["Division", "season", "team"]).agg(
        games=("w", "size"), wins=("w", "sum"), draws=("draw", "sum")).reset_index()
    g["weq"] = g.wins + 0.5 * g.draws
    g["winpct"] = g.weq / g.games
    g["points"] = 3 * g.wins + g.draws
    return g


def cb_indices(stand, min_teams=6, min_games=10):
    """CB indices per (Division, season)."""
    rows = []
    for (lg, se), t in stand.groupby(["Division", "season"]):
        t = t[t.games >= min_games]
        N = len(t)
        if N < min_teams:
            continue
        gbar = t.games.mean()
        ns = t.winpct.std(ddof=0) / (0.5 / np.sqrt(gbar))      # Noll-Scully
        s = t.wins / t.wins.sum()
        hhi_star = ((s ** 2).sum() - 1 / N) / (1 - 1 / N)       # normalised HHI
        x = t.points.values; mu = x.mean()
        theil = float(np.mean((x / mu) * np.log(np.clip(x / mu, 1e-12, None))))
        rows.append({"Division": lg, "season": int(se), "n_teams": N,
                     "noll_scully": float(ns), "hhi_star": float(hhi_star), "theil": theil})
    return pd.DataFrame(rows)


def by_league(cb):
    """Mean of the indices per league (over seasons)."""
    return cb.groupby("Division").agg(
        seasons=("season", "size"),
        noll_scully=("noll_scully", "mean"),
        hhi_star=("hhi_star", "mean"),
        theil=("theil", "mean")).reset_index()
