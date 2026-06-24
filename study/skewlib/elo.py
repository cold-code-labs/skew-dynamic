"""Elo from results ONLY (no odds) → odds-free competitiveness per league.

Motivation: the skewness ~ competitiveness relation from Block E/W1 uses `p_fav`
derived from the odds themselves — circular. Here we measure each league's
competitiveness via an Elo system built exclusively on results (W/D/L and
goal difference), without any market information. If the relation survives, it
is structural (sporting), not an artefact of the pricing.

Single chronological pass over ALL the stacked leagues (a team carries its
rating when promoted/relegated). The map rating-diff → (P_H,P_D,P_A) is
calibrated empirically on the results (MNLogit), also without odds.

Outputs per league (all odds-free):
  elo_entropy  mean entropy of the 3-outcome prediction (high = even)
  elo_pfav     mean prob. of the Elo favourite  (odds-free analogue of p_fav_dv)
  elo_disp     dispersion (sd) of the team strengths within a season
  upset_rate   fraction of games where the most likely outcome (Elo) did not occur
"""
import numpy as np, pandas as pd


def run_elo(df, k=20.0, hfa=65.0, init=1500.0, gd_mult=True):
    """Chronological Elo pass. Adds elo_h, elo_a (pre-game) and elo_diff (with HFA)."""
    d = df.sort_values("date").reset_index(drop=True)
    R = {}
    rh = np.empty(len(d)); ra = np.empty(len(d))
    home = d.HomeTeam.values; away = d.AwayTeam.values; res = d.FTResult.values
    fh = pd.to_numeric(d.FTHome, errors="coerce").values
    fa = pd.to_numeric(d.FTAway, errors="coerce").values
    for i in range(len(d)):
        Rh = R.get(home[i], init); Ra = R.get(away[i], init)
        rh[i] = Rh; ra[i] = Ra
        Eh = 1.0 / (1.0 + 10 ** (-((Rh + hfa) - Ra) / 400.0))
        Sh = 1.0 if res[i] == "H" else (0.5 if res[i] == "D" else 0.0)
        kk = k
        if gd_mult and not (np.isnan(fh[i]) or np.isnan(fa[i])):
            kk = k * (1.0 + np.log1p(max(abs(fh[i] - fa[i]) - 1.0, 0.0)))
        delta = kk * (Sh - Eh)
        R[home[i]] = Rh + delta; R[away[i]] = Ra - delta
    d["elo_h"] = rh; d["elo_a"] = ra
    d["elo_diff"] = (rh + hfa) - ra
    return d, R


def calibrate_outcomes(d):
    """Odds-free map rating-diff → (P_A,P_D,P_H) via MNLogit on the results."""
    import statsmodels.api as sm
    y = d.FTResult.map({"A": 0, "D": 1, "H": 2}).values
    z = d.elo_diff.values / 400.0
    X = sm.add_constant(np.column_stack([z, z * z]))
    m = sm.MNLogit(y, X).fit(disp=0)
    P = np.asarray(m.predict(X))               # columns in order 0,1,2 = A,D,H
    out = d.copy()
    out["pA_elo"], out["pD_elo"], out["pH_elo"] = P[:, 0], P[:, 1], P[:, 2]
    return out, m


def add_elo_features(d):
    """Entropy, Elo favourite prob. and upset flag per game."""
    P = d[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float)
    out = d.copy()
    out["elo_entropy"] = -(P * np.log(np.clip(P, 1e-12, 1.0))).sum(1)
    out["elo_pfav"] = P.max(1)
    pred = np.array(["H", "D", "A"])[P.argmax(1)]
    out["elo_upset"] = pred != d.FTResult.values
    return out


def with_elo(df, **kw):
    """Full pipeline: Elo + calibration + per-game features."""
    d, _ = run_elo(df, **kw)
    d, _ = calibrate_outcomes(d)
    return add_elo_features(d)


def league_competitiveness(d):
    """Odds-free competitiveness table per league (Division)."""
    d = d.copy()
    d["season"] = d.date.dt.year
    long = pd.concat([
        d[["Division", "season", "elo_h"]].rename(columns={"elo_h": "elo"}),
        d[["Division", "season", "elo_a"]].rename(columns={"elo_a": "elo"}),
    ])
    disp = (long.groupby(["Division", "season"]).elo.std()
                .groupby("Division").mean().rename("elo_disp"))
    agg = d.groupby("Division").agg(
        n=("FTResult", "size"),
        elo_entropy=("elo_entropy", "mean"),
        elo_pfav=("elo_pfav", "mean"),
        upset_rate=("elo_upset", "mean"),
    )
    return agg.join(disp).reset_index()
