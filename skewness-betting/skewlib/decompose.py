"""Decomposições: por estratégia, por faixa de odds, por liga."""
import pandas as pd
from scipy.stats import skew
from .returns import strategy_return


def by_strategy(df, picks=("fav", "dog", "H", "D", "A")):
    """Skewness/retorno por estratégia fixa."""
    rows = []
    for p in picks:
        r = strategy_return(df, p)
        rows.append({"pick": p, "skew": skew(r), "ret_mean": r.mean(),
                     "sd": r.std(), "win_rate": (r > 0).mean()})
    return pd.DataFrame(rows)


def by_odds_bucket(df, edges=(0, .4, .45, .5, .55, .6, .7, 1.0)):
    """Favorite-longshot bias: retorno e skewness por faixa de prob. do favorito."""
    d = df.copy(); d["bucket"] = pd.cut(d["p_fav"], list(edges))
    rows = []
    for b, g in d.groupby("bucket", observed=True):
        if len(g) < 50: continue
        rows.append({"bucket": str(b), "n": len(g), "ret_mean": g.ret_fav.mean(),
                     "skew": skew(g.ret_fav), "win_rate": (g.ret_fav > 0).mean()})
    return pd.DataFrame(rows)


def flb_by_year(df, min_n=500):
    """Barômetro do FLB por ano: retorno do azarão (mais negativo = FLB mais
    forte), spread favorito−azarão, e erro de calibração do favorito (win% real −
    p_fav implícita). Testa se o próprio viés deriva no tempo (Angelini &
    De Angelis 2019), o que confundiria o teste de invariância da skewness."""
    d = df.copy(); d["year"] = d.date.dt.year
    rows = []
    for y, g in d.groupby("year"):
        if len(g) < min_n:
            continue
        row = {"year": int(y), "n": len(g),
               "ret_dog": float(g.ret_dog.mean()),
               "ret_fav": float(g.ret_fav.mean()),
               "flb_spread": float(g.ret_fav.mean() - g.ret_dog.mean()),
               "skew_expost": float(skew(g.ret_fav))}
        if "p_fav_dv" in g:
            row["calib_err"] = float((g.ret_fav > 0).mean() - g.p_fav_dv.mean())
        rows.append(row)
    return pd.DataFrame(rows)


def by_league(df, min_games=2000):
    """Skewness por liga + previsibilidade média (p_fav)."""
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_games: continue
        rows.append({"league": lg, "n": len(g), "skew": skew(g.ret_fav),
                     "ret_mean": g.ret_fav.mean(), "p_fav_mean": g.p_fav.mean()})
    return pd.DataFrame(rows).sort_values("skew").reset_index(drop=True)
