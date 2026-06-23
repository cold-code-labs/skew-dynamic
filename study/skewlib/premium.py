"""Decomposição do retorno do favorito (Frente C1): margem + FLB mecânico + resíduo.

O retorno esperado de uma aposta unitária no favorito decompõe-se EXATAMENTE em:
    ret = (p_dv·o − 1)          [VIG: margem das casas, sob a prob de-vigada como
                                 verdadeira — o que se perde mesmo bem calibrado]
        + ((1{win} − p_dv)·o)   [FLB: calibração outcome-vs-de-vig, monetizada]
(porque ret = 1{win}·o − 1 e os dois termos somam a isso). O termo FLB ainda se
parte em (i) NÍVEL MECÂNICO — o que a curva global FLB(p) prevê para a composição
de p da liga — e (ii) RESÍDUO específico da liga. A pergunta de C1: sobra um
"prêmio" por liga (resíduo) correlacionado com a SKEWNESS implícita, além do nível
mecânico do FLB?
"""
import numpy as np, pandas as pd


def _win(df):
    return (df.ret_fav.values > 0).astype(float)   # favorito venceu (o>1 ⇒ ret>0)


def decompose_global(df):
    """Decomposição global do retorno do favorito (identidade exata)."""
    win = _win(df); o = df.o_fav.values; p = df.p_fav_dv.values
    ret = df.ret_fav.values
    vig = float((p * o - 1.0).mean())
    flb = float(((win - p) * o).mean())
    return {"ret_mean": float(ret.mean()), "vig": vig, "flb": flb,
            "residual_check": float(ret.mean() - (vig + flb))}   # ≈0


def flb_curve(df, nbins=20):
    """Curva mecânica do FLB: contribuição (1{win}−p_dv)·o por faixa de p_dv.
    É o componente sistemático monetizado do favourite–longshot bias."""
    d = df[["p_fav_dv", "o_fav", "ret_fav"]].copy()
    d["contrib"] = ((d.ret_fav > 0).astype(float) - d.p_fav_dv) * d.o_fav
    d["b"] = pd.qcut(d.p_fav_dv, nbins, duplicates="drop")
    return (d.groupby("b", observed=True)
             .agg(p=("p_fav_dv", "mean"), flb=("contrib", "mean"), n=("contrib", "size"))
             .reset_index(drop=True))


def decompose_by_league(df, min_n=2000, nbins=20):
    """Por liga: ret = vig + flb; flb = sistemático (curva global aplicada à
    composição de p da liga) + resíduo. O resíduo é o "prêmio" candidato."""
    cur = flb_curve(df, nbins)
    order = np.argsort(cur.p.values)
    xs, ys = cur.p.values[order], cur.flb.values[order]
    d = df.copy()
    d["_pred_flb"] = np.interp(d.p_fav_dv.values, xs, ys)   # nível mecânico por jogo
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        win = (g.ret_fav.values > 0).astype(float)
        o = g.o_fav.values; p = g.p_fav_dv.values
        vig = float((p * o - 1.0).mean())
        flb = float(((win - p) * o).mean())
        syst = float(g._pred_flb.mean())
        rows.append({"Division": lg, "n": int(len(g)), "p_fav_dv": float(p.mean()),
                     "ret_mean": float(g.ret_fav.mean()), "vig": vig,
                     "flb": flb, "flb_syst": syst, "residual": flb - syst})
    return pd.DataFrame(rows)
