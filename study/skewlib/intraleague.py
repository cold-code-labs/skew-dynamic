"""Front F — within-league / micro:

  F1  intra-season seasonality: does the skewness move from the start to the end of
      the season (as the standings crystallise)? Controlled by league.
  F2  contribution by MATCH competitiveness: which matches carry the league's
      skewness? Decomposes the pooled M₃ by p_fav bin (the tail cancellation).
  F3  per-team decomposition: do dominant clubs (high Elo) "pull" the league's
      signature towards unbalanced matches (negative skew)?
"""
import numpy as np, pandas as pd
from . import exante


def add_season_phase(df, nseg=3):
    """Real season (Aug→Jul) + intra-season phase (tertile by date within the
    league×season). Avoids splitting a European season across 2 calendar years."""
    d = df.copy()
    d["season"] = np.where(d.date.dt.month >= 7, d.date.dt.year, d.date.dt.year - 1)
    d["frac"] = d.groupby(["Division", "season"]).date.rank(pct=True)
    d["phase"] = np.clip((d.frac * nseg).astype(int), 0, nseg - 1)
    return d


# ── F1 — intra-season seasonality ────────────────────────────────────────────
def skew_by_phase(d, min_n=2000):
    """Ex-ante skewness by intra-season phase (0=start … nseg−1=end), global."""
    rows = []
    for ph, g in d.groupby("phase"):
        if len(g) < min_n:
            continue
        rows.append({"phase": int(ph), "n": len(g),
                     "skew": exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                     "p_fav": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


def phase_shift_by_league(d, min_n=400):
    """Δskew (end − start) per league: does the season crystallise the asymmetry?"""
    rows = []
    for lg, g in d.groupby("Division"):
        ph = {p: exante.pooled_skew(x.p_fav_dv.values, x.o_fav.values)["skew"]
              for p, x in g.groupby("phase") if len(x) >= min_n}
        if 0 in ph and (g.phase.max()) in ph:
            rows.append({"Division": lg, "skew_start": ph[0],
                         "skew_end": ph[g.phase.max()],
                         "shift": ph[g.phase.max()] - ph[0]})
    return pd.DataFrame(rows)


# ── F2 — contribution by match competitiveness ───────────────────────────────
def m3_contribution_by_bin(df, edges=(0.0, 0.42, 0.46, 0.50, 0.55, 0.65, 1.0)):
    """Decomposes the pooled M₃ by p_fav bin: which matches carry the skewness.
    Under near-fair odds M₃≈E[m₃(p)]; we report the contribution (sum of m₃) and the
    skew per bin — the tail cancellation (weak favourites + / strong −)."""
    p = df.p_fav_dv.values; o = df.o_fav.values
    _, _, m3 = exante.per_match_moments(p, o)
    tot = m3.sum()
    b = pd.cut(pd.Series(p), list(edges))
    g = pd.DataFrame({"p": p, "m3": m3, "bin": b}).groupby("bin", observed=True)
    rows = []
    for key, x in g:
        rows.append({"bin": str(key), "n": len(x), "p_mid": float(x.p.mean()),
                     "skew_match": float(exante.per_match_skew(x.p.mean())),
                     "m3_share": float(x.m3.sum() / tot)})
    return pd.DataFrame(rows), float(tot)


# ── F3 — per-team decomposition ───────────────────────────────────────────────
def team_long(df):
    """Long format: 1 row per (match, team) with the team's Elo, de-vigged win
    probability and whether it was the match favourite."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    fav_is_home = (P.argmax(1) == 0)
    home = pd.DataFrame({"team": df.HomeTeam.values, "elo": df.HomeElo.values,
                         "p_win": df.p_H.values, "is_fav": fav_is_home,
                         "p_fav": df.p_fav_dv.values, "Division": df.Division.values})
    away = pd.DataFrame({"team": df.AwayTeam.values, "elo": df.AwayElo.values,
                         "p_win": df.p_A.values, "is_fav": ~fav_is_home,
                         "p_fav": df.p_fav_dv.values, "Division": df.Division.values})
    return pd.concat([home, away], ignore_index=True)


def team_dominance(df, min_games=200):
    """Per team: mean Elo (dominance) and ex-ante skewness of the matches it plays.
    Dominant clubs ⇒ unbalanced matches ⇒ negative skew contribution."""
    tl = team_long(df)
    rows = []
    for tm, g in tl.groupby("team"):
        if len(g) < min_games:
            continue
        rows.append({"team": tm, "Division": g.Division.mode().iloc[0], "n": len(g),
                     "elo": float(g.elo.mean()), "fav_rate": float(g.is_fav.mean()),
                     "skew_games": float(exante.per_match_skew(g.p_fav.values).mean())})
    return pd.DataFrame(rows)
