"""Painel liga×temporada da skewness ex-ante — invariância temporal (W3).

Tratar cada (liga, temporada) como uma observação separada resolve, por
construção, o confound de composição que gerou o "blip" de 2012 (Bloco F): a
mistura de ligas deixa de importar quando a liga é a própria unidade. Testes:
  - tendência secular: FE de liga + ano linear (β≈0, SE cluster por liga);
  - decomposição de variância: between-liga (o invariante) vs within-liga (ruído);
  - quebras/tendências por liga individual;
  - vinheta COVID: estádios vazios 2020/21 derrubaram a vantagem de casa —
    a skewness se moveu?
"""
import numpy as np, pandas as pd
from . import exante


def league_season_panel(df, min_n=150):
    """Skewness ex-ante por (Division, season). Requer add_exante já aplicado."""
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
    """FE de liga + ano linear; SE cluster-robusto por liga. H0: β_ano = 0."""
    import statsmodels.formula.api as smf
    p = panel.copy()
    p["yr"] = p.season - p.season.mean()
    m = smf.ols("skew_exante ~ yr + C(Division)", data=p).fit(
        cov_type="cluster", cov_kwds={"groups": p.Division})
    ci = m.conf_int().loc["yr"]
    return {"beta_year": float(m.params["yr"]), "se": float(m.bse["yr"]),
            "p": float(m.pvalues["yr"]), "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
            "n_obs": int(m.nobs)}


def variance_decomp(panel):
    """Var total = between-liga + within-liga. ICC = between/(between+within)."""
    g = panel.groupby("Division").skew_exante
    between = float(g.mean().var(ddof=1))
    within = float((panel.skew_exante - g.transform("mean")).var(ddof=1))
    return {"between": between, "within": within,
            "icc": between / (between + within),
            "sd_between": between ** .5, "sd_within": within ** .5}


def sampling_se(df, n_boot=200, min_n=150, seed=42):
    """SE amostral média da skew ex-ante por (liga,temporada), via bootstrap dos
    jogos. Se ≈ sd within-liga, a 'flutuação temporal' é puro ruído amostral."""
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
    """Slope skew~ano por liga + nº de quebras estruturais na série da liga."""
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


def covid_vignette(panel, year=2020):
    """Desvio da skewness de `year` vs a média da própria liga (em SD da liga)."""
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
    """Contexto da vinheta: taxa de vitória do mandante por ano (choque de HFA)."""
    d = df.copy()
    d["season"] = d.date.dt.year
    return (d.assign(home_win=(d.FTResult == "H").astype(float))
              .groupby("season").home_win.mean())
