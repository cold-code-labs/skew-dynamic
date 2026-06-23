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


def by_league(df, min_games=2000):
    """Skewness por liga + previsibilidade média (p_fav)."""
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_games: continue
        rows.append({"league": lg, "n": len(g), "skew": skew(g.ret_fav),
                     "ret_mean": g.ret_fav.mean(), "p_fav_mean": g.p_fav.mean()})
    return pd.DataFrame(rows).sort_values("skew").reset_index(drop=True)
