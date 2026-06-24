"""Front VAR — staggered natural experiment. VAR is an INSTITUTIONAL shock
without being a COMPETITIVENESS one: it reduces arbitrage error, but does not change the
teams' force dispersion. The thesis (skewness = f(force dispersion)) predicts that it does NOT move
the structural skewness — a placebo contrasting with COVID (W3), a REAL
competitiveness shock (HFA fell) that moved the skewness +0.42 SD.

STAGGERED difference-in-differences design: the leagues adopted VAR in different
years (2017/18, 2018/19, 2019/20); the lower English/Scottish divisions (without
VAR in league play in the sample) serve as the never-treated control. The coefficient of
the VAR indicator, under league FE + year FE, is the average effect.

Dates: first FULL calendar year under VAR (adoption at the August season turnover;
the partial start year is kept as pre, conservatively). Public sources
(IFAB/leagues): Serie A and Bundesliga 2017/18; La Liga, Ligue 1, Eredivisie, Süper Lig
2018/19; Premier League, Belgium, Portugal, Greece 2019/20.
"""
import numpy as np, pandas as pd
from . import exante

VAR_FROM_YEAR = {
    "I1": 2018, "D1": 2018,                              # 2017/18
    "SP1": 2019, "F1": 2019, "N1": 2019, "T1": 2019,     # 2018/19
    "E0": 2020, "B1": 2020, "P1": 2020, "G1": 2020,      # 2019/20
}
CONTROLS = ["E1", "E2", "E3", "SC1", "SC2", "SC3"]       # never-treated in the sample


def build_panel(df, min_n=150):
    """(league,year) panel with ex-ante skew, mean p_fav, favourite win rate
    and VAR flag. Requires add_exante + add_returns (ret_fav). Restricts to the
    treated leagues (known date) + never-treated controls."""
    d = df.copy(); d["year"] = d.date.dt.year
    d["fav_won"] = (d.ret_fav > 0).astype(float)
    d = d[d.Division.isin(set(VAR_FROM_YEAR) | set(CONTROLS))]
    rows = []
    for (lg, yr), g in d.groupby(["Division", "year"]):
        if len(g) < min_n:
            continue
        m = exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)
        rows.append({"Division": lg, "year": int(yr), "n": len(g),
                     "skew_exante": m["skew"], "p_fav": float(g.p_fav_dv.mean()),
                     "fav_win_rate": float(g.fav_won.mean()),
                     "var": int(lg in VAR_FROM_YEAR and yr >= VAR_FROM_YEAR[lg]),
                     "treated": int(lg in VAR_FROM_YEAR)})
    return pd.DataFrame(rows)


def did(panel, outcome):
    """Staggered DiD: outcome ~ VAR + league FE + year FE (league-clustered SE).
    The coefficient of `var` is the average effect of VAR on the outcome."""
    import statsmodels.formula.api as smf
    m = smf.ols(f"{outcome} ~ var + C(Division) + C(year)", data=panel).fit(
        cov_type="cluster", cov_kwds={"groups": panel.Division})
    ci = m.conf_int().loc["var"]
    return {"beta": float(m.params["var"]), "se": float(m.bse["var"]),
            "p": float(m.pvalues["var"]), "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
            "n_obs": int(m.nobs)}


def event_study(panel, span=4):
    """Mean skewness by years-since-adoption (relative time) in the treated leagues —
    to inspect for the absence of a jump/trend around VAR adoption."""
    t = panel[panel.treated == 1].copy()
    t["rel"] = t.year - t.Division.map(VAR_FROM_YEAR)
    t = t[t.rel.between(-span, span)]
    return (t.groupby("rel").skew_exante.agg(["mean", "std", "count"])
              .reset_index().rename(columns={"rel": "years_since_var"}))
