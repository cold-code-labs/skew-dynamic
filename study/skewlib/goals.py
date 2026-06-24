"""Front I — cross-validation of the MECHANISM with an independent generative model.
The law skewness=f(competitiveness) was derived from an ordered-probit on the latent
margin (P3/E). Here we use a COMPLETELY different model — goals Poisson
(Maher 1982 / Dixon-Coles without the low-score correction) — with attack/defence
per team + home advantage: goals ~ Poisson(λ), log λ_home = μ + att_i + def_j + home. The
outcome probabilities come from the goal difference (Skellam), and from there the
pooled skewness. If a GOALS model reproduces the same law as the MARGIN model, the
mechanism is model-independent — not an artefact of the ordered-probit.
"""
import warnings
import numpy as np, pandas as pd
from scipy.stats import skellam
warnings.filterwarnings("ignore")


def _long(g):
    """Long format: 2 rows per match (attack/defence/home)."""
    return pd.concat([
        pd.DataFrame({"goals": g.FTHome.astype(int).values, "att": g.HomeTeam.values,
                      "dfn": g.AwayTeam.values, "home": 1}),
        pd.DataFrame({"goals": g.FTAway.astype(int).values, "att": g.AwayTeam.values,
                      "dfn": g.HomeTeam.values, "home": 0}),
    ], ignore_index=True)


def fit_rates(g):
    """Fits the attack/defence+home Poisson on the league-season and returns (lh, la)
    per match — the expected goal rates (home, away). SHARED basis of the goal
    generators (Poisson via Skellam, Dixon-Coles, Negative-Binomial of the
    model battery). None if the fit fails or does not converge."""
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    long = _long(g)
    try:
        m = smf.glm("goals ~ C(att) + C(dfn) + home", data=long,
                    family=sm.families.Poisson()).fit()
    except Exception:
        return None
    if not m.converged:
        return None
    lh = m.predict(pd.DataFrame({"att": g.HomeTeam, "dfn": g.AwayTeam, "home": 1})).values
    la = m.predict(pd.DataFrame({"att": g.AwayTeam, "dfn": g.HomeTeam, "home": 0})).values
    return np.clip(lh, 1e-3, 12), np.clip(la, 1e-3, 12)


def fit_match_probs(g, max_goals_diff=15):
    """Fits attack/defence+home Poisson on the league-season and returns (pH,pD,pA)
    per match via Skellam. None if it fails / converges poorly."""
    r = fit_rates(g)
    if r is None:
        return None
    lh, la = r
    pH = 1 - skellam.cdf(0, lh, la)
    pD = skellam.pmf(0, lh, la)
    pA = skellam.cdf(-1, lh, la)
    s = pH + pD + pA
    return pH / s, pD / s, pA / s


# Gap p_fav(model) − p_fav(empirical) above which the fit is DEGENERATE. Under
# newer libs (pandas 3 / numpy 2 / current statsmodels) the GLM of rare pathological
# league-seasons (e.g. JAP 2017) suffers quasi-complete separation and "converges" to a
# fit where p_fav≈1 in EVERY match (vs ~0.48 empirical) — previously excluded by
# non-convergence. This blows up the fair-odds skewness (1−2p)/√(p(1−p)) → −∞ and
# poisons the league mean. The largest gap of a REAL league is ~0.08; 0.25 is a 3× margin.
SEP_GAP = 0.25


def degenerate_fit(pf_model, pf_emp, gap=SEP_GAP):
    """True if the generator fit is degenerate (separation): the model p_fav diverges
    implausibly from the empirical one. Reused by the model battery (crossmodel)."""
    return float(np.mean(pf_model)) - float(np.mean(pf_emp)) > gap


def league_season_table(df, min_games=150, min_teams=8):
    """Pooled favourite skewness under the GOALS model (Poisson) vs empirical,
    per league-season. Requires add_exante (p_fav_dv, o_fav) and a `season` column.
    Discards degenerate fits (GLM separation) via `degenerate_fit`."""
    from . import exante
    rows = []
    for (lg, yr), g in df.groupby(["Division", "season"]):
        if len(g) < min_games or g.HomeTeam.nunique() < min_teams:
            continue
        pr = fit_match_probs(g)
        if pr is None:
            continue
        pH, pD, pA = pr
        P = np.vstack([pH, pD, pA]).T
        pf = np.clip(P.max(1), 1e-6, 1 - 1e-6)
        if degenerate_fit(pf, g.p_fav_dv.values):     # rotten fit (e.g. JAP 2017)
            continue
        sk_pois = exante.pooled_skew(pf, 1.0 / pf)["skew"]
        sk_emp = exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"]
        rows.append({"Division": lg, "season": int(yr), "n": len(g),
                     "skew_poisson": sk_pois, "pfav_poisson": float(pf.mean()),
                     "skew_emp": sk_emp, "pfav_emp": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


def by_league(tab):
    """Aggregates the league-season table to the league level (means)."""
    return (tab.groupby("Division")
              .agg(n=("n", "sum"), seasons=("season", "nunique"),
                   skew_poisson=("skew_poisson", "mean"),
                   pfav_poisson=("pfav_poisson", "mean"),
                   skew_emp=("skew_emp", "mean"), pfav_emp=("pfav_emp", "mean"))
              .reset_index())
