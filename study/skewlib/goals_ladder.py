"""Goals spin-off — the over/under ladder: the same skewness law, dialled by the line.

Each total-goals line L is a two-point Over bet with p = P(total > L). Sweeping L
sweeps the law (1−2p)/√(p(1−p)) within a FIXED match population — the line is the
knob, not competitiveness. We source p WITHOUT extra odds via a Poisson goals model
(reusing skewlib.goals: total ~ Poisson(λ_home+λ_away)), exactly as the World Cup
used Elo instead of odds. The one line with real odds (2.5) anchors model-vs-market.
The realised side comes straight from actual scores. Goals reach p from 0.92 (line
0.5) to 0.13 (line 4.5) — far wider than the 1X2 favourite, hitting the law's tails.
"""
import numpy as np
import pandas as pd
from scipy.stats import poisson, skew

from . import goals, overunder

LINES = (0.5, 1.5, 2.5, 3.5, 4.5, 5.5)


def match_total_lambda(df, min_games=150, min_teams=8):
    """Per-match expected total goals λ = λ_home+λ_away, from a per-league-season
    attack/defence+home Poisson (reuses goals.fit_rates). Returns the matches that
    got a valid fit, with lam_tot and tot (actual total goals)."""
    df = df.copy()
    df["season"] = df.date.dt.year
    out = []
    for (lg, yr), g in df.groupby(["Division", "season"]):
        if len(g) < min_games or g.HomeTeam.nunique() < min_teams:
            continue
        r = goals.fit_rates(g)
        if r is None:
            continue
        lh, la = r
        gg = g.copy()
        gg["lam_tot"] = lh + la
        gg["tot"] = (pd.to_numeric(gg.FTHome, errors="coerce")
                     + pd.to_numeric(gg.FTAway, errors="coerce"))
        out.append(gg[["Division", "season", "lam_tot", "tot"]])
    return pd.concat(out, ignore_index=True).dropna(subset=["tot"])


def _law(p):
    return (1 - 2 * p) / np.sqrt(p * (1 - p))


def ladder(ml, lines=LINES):
    """Per line: the Over bet's skewness, dialled by the line.

    The model PREDICTS the over-probability at each line (Poisson over the matches);
    realised is the actual over-rate. The bet skewness follows the law (1−2p)/√(p(1−p))
    on each side — a stable, bounded object (unlike the per-match fair-odds pool, which
    blows up as p→0 at high lines). The honest test is calibration: does the odds-free
    model recover the over-rate at every line? The skewness then follows."""
    lam = ml.lam_tot.values
    tot = ml.tot.values
    rows = []
    for L in lines:
        k = int(np.floor(L))
        p = np.clip(1.0 - poisson.cdf(k, lam), 1e-9, 1 - 1e-9)   # per-match P(total>L)
        pm = float(p.mean())                                     # model over-rate
        pr = float((tot > L).mean())                             # realised over-rate
        rows.append({"line": L, "n": int(len(p)),
                     "p_model": pm, "p_real": pr,
                     "calib_err": pm - pr,
                     "skew_pred": float(_law(pm)), "skew_real": float(_law(pr))})
    return pd.DataFrame(rows)


def anchor_25(df):
    """The only line with real odds: O/U 2.5. Compares the model p_over (Poisson)
    with the de-vigged MARKET p_over and the realised over-rate, plus the realised
    skew of the real Over-2.5 bet (true odds payoff). Validates the odds-free ladder
    at its one observable point."""
    ml = match_total_lambda(df)
    p_model = float(np.clip(1.0 - poisson.cdf(2, ml.lam_tot.values), 1e-6, 1 - 1e-6).mean())
    ou = overunder.prep(df, method="shin")
    ret_over = np.where(ou.over.values == 1, ou.Over25.values - 1.0, -1.0)  # real odds
    return {"p_model": round(p_model, 4),
            "p_market": round(float(ou.p_over.mean()), 4),
            "p_real": round(float(ou.over.mean()), 4),
            "skew_real_market": round(float(skew(ret_over)), 4),
            "overround": round(float(ou.overround.mean()), 4),
            "n": int(len(ou))}


def law_curve(p_lo=0.06, p_hi=0.95, n=60):
    """The theoretical curve (1−2p)/√(p(1−p)) for the site overlay."""
    ps = np.linspace(p_lo, p_hi, n)
    return [{"p": float(p), "skew": float((1 - 2 * p) / np.sqrt(p * (1 - p)))} for p in ps]
