"""Construção de retornos ex-post (stake unitário)."""
import numpy as np


def _ret(row, pick, h="OddHome", d="OddDraw", a="OddAway"):
    """Retorno de uma aposta unitária. pick ∈ {'fav','dog','H','D','A'}."""
    o = {"H": row[h], "D": row[d], "A": row[a]}
    if   pick == "fav": k = min(o, key=o.get)
    elif pick == "dog": k = max(o, key=o.get)
    else:               k = pick
    return (o[k] - 1) if row["FTResult"] == k else -1.0


def add_returns(df):
    """Adiciona ret_fav, ret_dog, p_fav, ret_dm (league-demeaned) e ret_fav_max."""
    df = df.copy()
    df["ret_fav"] = df.apply(lambda r: _ret(r, "fav"), axis=1)
    df["ret_dog"] = df.apply(lambda r: _ret(r, "dog"), axis=1)
    df["o_fav"]   = df[["OddHome", "OddDraw", "OddAway"]].min(axis=1)
    df["p_fav"]   = 1.0 / df["o_fav"]
    # league-demeaned: remove o efeito-fixo de liga antes de empilhar
    df["ret_dm"]  = df["ret_fav"] - df.groupby("Division")["ret_fav"].transform("mean")
    # versão com a melhor odd do mercado (Max*) para o teste cross-casa
    mask = df[["MaxHome", "MaxDraw", "MaxAway"]].notna().all(axis=1)
    df["ret_fav_max"] = np.nan
    df.loc[mask, "ret_fav_max"] = df[mask].apply(
        lambda r: _ret(r, "fav", "MaxHome", "MaxDraw", "MaxAway"), axis=1)
    return df


def strategy_return(df, pick):
    """Série de retornos de uma estratégia fixa."""
    return df.apply(lambda r: _ret(r, pick), axis=1)
