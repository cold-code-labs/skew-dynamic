"""Frente VAR — experimento natural escalonado. O VAR é um choque INSTITUCIONAL
sem ser de COMPETITIVIDADE: reduz erro de arbitragem, mas não muda a dispersão de
força dos times. A tese (skewness = f(dispersão de força)) prevê que ele NÃO move
a skewness estrutural — placebo que contrasta com a COVID (W3), choque REAL de
competitividade (HFA caiu) que moveu a skewness +0.42 SD.

Desenho diferenças-em-diferenças ESCALONADO: as ligas adotaram o VAR em anos
distintos (2017/18, 2018/19, 2019/20); divisões inferiores inglesas/escocesas (sem
VAR em jogo de liga no recorte) servem de controle nunca-tratado. O coeficiente do
indicador de VAR, sob FE de liga + FE de ano, é o efeito médio.

Datas: primeiro ano-calendário INTEIRO sob VAR (adoção na virada de temporada de
agosto; o ano de início parcial fica como pré, conservador). Fontes públicas
(IFAB/ligas): Serie A e Bundesliga 2017/18; La Liga, Ligue 1, Eredivisie, Süper Lig
2018/19; Premier League, Bélgica, Portugal, Grécia 2019/20.
"""
import numpy as np, pandas as pd
from . import exante

VAR_FROM_YEAR = {
    "I1": 2018, "D1": 2018,                              # 2017/18
    "SP1": 2019, "F1": 2019, "N1": 2019, "T1": 2019,     # 2018/19
    "E0": 2020, "B1": 2020, "P1": 2020, "G1": 2020,      # 2019/20
}
CONTROLS = ["E1", "E2", "E3", "SC1", "SC2", "SC3"]       # nunca-tratados no recorte


def build_panel(df, min_n=150):
    """Painel (liga,ano) com skew ex-ante, p_fav médio, taxa de vitória do favorito
    e flag de VAR. Requer add_exante + add_returns (ret_fav). Restringe às ligas
    tratadas (data conhecida) + controles nunca-tratados."""
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
    """DiD escalonado: outcome ~ VAR + FE de liga + FE de ano (SE cluster por liga).
    O coeficiente de `var` é o efeito médio do VAR sobre o outcome."""
    import statsmodels.formula.api as smf
    m = smf.ols(f"{outcome} ~ var + C(Division) + C(year)", data=panel).fit(
        cov_type="cluster", cov_kwds={"groups": panel.Division})
    ci = m.conf_int().loc["var"]
    return {"beta": float(m.params["var"]), "se": float(m.bse["var"]),
            "p": float(m.pvalues["var"]), "ci_lo": float(ci[0]), "ci_hi": float(ci[1]),
            "n_obs": int(m.nobs)}


def event_study(panel, span=4):
    """Skewness média por anos-desde-adoção (tempo relativo) nas ligas tratadas —
    para inspecionar ausência de salto/tendência em torno da adoção do VAR."""
    t = panel[panel.treated == 1].copy()
    t["rel"] = t.year - t.Division.map(VAR_FROM_YEAR)
    t = t[t.rel.between(-span, span)]
    return (t.groupby("rel").skew_exante.agg(["mean", "std", "count"])
              .reset_index().rename(columns={"rel": "years_since_var"}))
