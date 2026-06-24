"""League×season panel of ex-ante skewness — temporal invariance (W3).

Treating each (league, season) as a separate observation resolves, by
construction, the composition confound that produced the 2012 "blip" (Block F): the
league mix stops mattering when the league is itself the unit. Tests:
  - secular trend: league FE + linear year (β≈0, league-clustered SE);
  - variance decomposition: between-league (the invariant) vs within-league (noise);
  - per-league breaks/trends;
  - COVID vignette: empty stadiums 2020/21 knocked down the home advantage —
    did the skewness move?
"""
import numpy as np, pandas as pd
from . import exante


def league_season_panel(df, min_n=150):
    """Ex-ante skewness by (Division, season). Requires add_exante already applied."""
    d = df.copy()
    d["season"] = d.date.dt.year
    rows = []
    for (lg, yr), g in d.groupby(["Division", "season"]):
        if len(g) < min_n:
            continue
        m = exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)
        rows.append({"Division": lg, "season": int(yr), "n": len(g),
                     "skew_exante": m["skew"], "p_fav_dv": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


def trend_test(panel):
    """League FE + linear year; league-clustered robust SE. H0: β_year = 0."""
    import statsmodels.formula.api as smf
    p = panel.copy()
    p["yr"] = p.season - p.season.mean()
    m = smf.ols("skew_exante ~ yr + C(Division)", data=p).fit(
        cov_type="cluster", cov_kwds={"groups": p.Division})
    ci = m.conf_int().loc["yr"]
    return {"beta_year": float(m.params["yr"]), "se": float(m.bse["yr"]),
            "p": float(m.pvalues["yr"]), "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
            "n_obs": int(m.nobs)}


def trend_boot(panel, B=2000, seed=42):
    """Bootstrap CI of β_year by resampling LEAGUES (cluster bootstrap, consistent
    with the cluster-robust SE of `trend_test`). Refits the fixed-effects estimator
    on each resample via the within transformation (fast and exact for the slope): demeans
    skew and year within each drawn cluster and regresses. Returns SE and 90/95% CI."""
    p = panel.copy()
    p["yr"] = p.season - p.season.mean()
    groups = [(g.skew_exante.to_numpy(float), g.yr.to_numpy(float))
              for _, g in p.groupby("Division")]
    k = len(groups)
    rng = np.random.default_rng(seed)
    betas = np.empty(B)
    for b in range(B):
        ys, xs = [], []
        for idx in rng.integers(0, k, k):
            y, x = groups[idx]
            ys.append(y - y.mean()); xs.append(x - x.mean())
        y_dm = np.concatenate(ys); x_dm = np.concatenate(xs)
        d = (x_dm * x_dm).sum()
        betas[b] = (x_dm * y_dm).sum() / d if d > 0 else np.nan
    betas = betas[~np.isnan(betas)]
    return {"se": float(betas.std(ddof=1)), "B": int(betas.size),
            "ci90_lo": float(np.percentile(betas, 5)), "ci90_hi": float(np.percentile(betas, 95)),
            "ci95_lo": float(np.percentile(betas, 2.5)), "ci95_hi": float(np.percentile(betas, 97.5))}


def variance_decomp(panel):
    """Total var = between-league + within-league. ICC = between/(between+within)."""
    g = panel.groupby("Division").skew_exante
    between = float(g.mean().var(ddof=1))
    within = float((panel.skew_exante - g.transform("mean")).var(ddof=1))
    return {"between": between, "within": within,
            "icc": between / (between + within),
            "sd_between": between ** .5, "sd_within": within ** .5}


def sampling_se(df, n_boot=200, min_n=150, seed=42):
    """Mean sampling SE of the ex-ante skew per (league,season), via bootstrap of the
    matches. If ≈ within-league sd, the 'temporal fluctuation' is pure sampling noise."""
    d = df.copy(); d["season"] = d.date.dt.year
    rng = np.random.default_rng(seed)
    ses = []
    for (_, _), g in d.groupby(["Division", "season"]):
        if len(g) < min_n:
            continue
        p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
        vals = [exante.pooled_skew(p[i], o[i])["skew"]
                for i in (rng.integers(0, n, n) for _ in range(n_boot))]
        ses.append(np.std(vals))
    return float(np.mean(ses))


def per_league_trends(panel, min_seasons=8):
    """Slope skew~year per league + number of structural breaks in the league series."""
    from .stats import breakpoints
    rows = []
    for lg, g in panel.groupby("Division"):
        g = g.sort_values("season")
        if len(g) < min_seasons:
            continue
        b = np.polyfit(g.season, g.skew_exante, 1)[0]
        try:
            ser = pd.Series(g.skew_exante.values,
                            index=pd.PeriodIndex(g.season, freq="Y").to_timestamp())
            nbk = len(breakpoints(ser, min_size=3))
        except Exception:
            nbk = -1
        rows.append({"Division": lg, "seasons": len(g),
                     "slope_per_year": float(b), "n_breaks": nbk})
    return pd.DataFrame(rows)


def league_breaks(panel, min_seasons=10, pen_mult=3.0):
    """Structural breaks (PELT) in EACH league's skewness series + the level
    jump. Conservative penalty so as not to over-segment short series (~20
    points). Used to distinguish a real regime change from idiosyncratic noise."""
    import ruptures as rpt
    rows = []
    for lg, g in panel.groupby("Division"):
        g = g.sort_values("season")
        if len(g) < min_seasons:
            continue
        y = g.skew_exante.values
        bk = rpt.Pelt(model="l2", min_size=4).fit(y).predict(
            pen=np.log(len(y)) * y.var() * pen_mult)[:-1]
        for b in bk:
            rows.append({"Division": lg, "break_season": int(g.season.values[b]),
                         "shift": float(y[b:].mean() - y[:b].mean()),
                         "seasons": len(g)})
    return pd.DataFrame(rows)


def covid_vignette(panel, year=2020):
    """Deviation of `year`'s skewness vs the league's own mean (in league SD)."""
    rows = []
    for lg, g in panel.groupby("Division"):
        base = g[g.season != year].skew_exante
        cur = g[g.season == year].skew_exante
        if len(cur) == 0 or len(base) < 3 or base.std() == 0:
            continue
        rows.append({"Division": lg, "skew_year": float(cur.values[0]),
                     "league_mean": float(base.mean()),
                     "z": float((cur.values[0] - base.mean()) / base.std())})
    return pd.DataFrame(rows)


def home_win_rate_by_year(df):
    """Vignette context: home win rate per year (HFA shock)."""
    d = df.copy()
    d["season"] = d.date.dt.year
    return (d.assign(home_win=(d.FTResult == "H").astype(float))
              .groupby("season").home_win.mean())
