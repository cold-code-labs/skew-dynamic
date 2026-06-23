"""Frente I — validação cruzada do MECANISMO com um modelo gerador independente.
A lei skewness=f(competitividade) foi derivada de um ordered-probit sobre a margem
latente (P3/E). Aqui usamos um modelo COMPLETAMENTE diferente — Poisson de gols
(Maher 1982 / Dixon-Coles sem a correção de placares baixos) — com ataque/defesa
por time + mando: gols ~ Poisson(λ), log λ_casa = μ + att_i + def_j + mando. As
probabilidades de resultado saem da diferença de gols (Skellam), e daí a skewness
agrupada. Se um modelo de GOLS reproduz a mesma lei que o modelo de MARGEM, o
mecanismo é independente do modelo — não um artefato do ordered-probit.
"""
import warnings
import numpy as np, pandas as pd
from scipy.stats import skellam
warnings.filterwarnings("ignore")


def _long(g):
    """Formato longo: 2 linhas por jogo (ataque/defesa/mando)."""
    return pd.concat([
        pd.DataFrame({"goals": g.FTHome.astype(int).values, "att": g.HomeTeam.values,
                      "dfn": g.AwayTeam.values, "home": 1}),
        pd.DataFrame({"goals": g.FTAway.astype(int).values, "att": g.AwayTeam.values,
                      "dfn": g.HomeTeam.values, "home": 0}),
    ], ignore_index=True)


def fit_match_probs(g, max_goals_diff=15):
    """Ajusta Poisson ataque/defesa+mando na liga-temporada e devolve (pH,pD,pA)
    por jogo via Skellam. None se falhar/converge mal."""
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
    lh = np.clip(lh, 1e-3, 12); la = np.clip(la, 1e-3, 12)
    pH = 1 - skellam.cdf(0, lh, la)
    pD = skellam.pmf(0, lh, la)
    pA = skellam.cdf(-1, lh, la)
    s = pH + pD + pA
    return pH / s, pD / s, pA / s


def league_season_table(df, min_games=150, min_teams=8):
    """Skewness agrupada do favorito sob o modelo de GOLS (Poisson) vs empírico,
    por liga-temporada. Requer add_exante (p_fav_dv, o_fav) e coluna `season`."""
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
        sk_pois = exante.pooled_skew(pf, 1.0 / pf)["skew"]
        sk_emp = exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"]
        rows.append({"Division": lg, "season": int(yr), "n": len(g),
                     "skew_poisson": sk_pois, "pfav_poisson": float(pf.mean()),
                     "skew_emp": sk_emp, "pfav_emp": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


def by_league(tab):
    """Agrega a tabela liga-temporada para o nível de liga (médias)."""
    return (tab.groupby("Division")
              .agg(n=("n", "sum"), seasons=("season", "nunique"),
                   skew_poisson=("skew_poisson", "mean"),
                   pfav_poisson=("pfav_poisson", "mean"),
                   skew_emp=("skew_emp", "mean"), pfav_emp=("pfav_emp", "mean"))
              .reset_index())
