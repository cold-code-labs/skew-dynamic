"""Frente J — chegada de informação: intervalo → fim (HT→FT). Sem odds de abertura
(D1 fora), usamos o RESULTADO do intervalo como choque de informação. Para o
favorito PRÉ-JOGO, a prob de vitória se ATUALIZA com o placar do HT, e a skewness
implícita do "resto do jogo" é de novo a identidade (1−2q)/√(q(1−q)) na prob
condicional q. Mostra que o núcleo mecânico (W1) é DINÂMICO: vale a cada estado de
informação, e a assimetria do favorito se RESOLVE conforme o placar anda.
"""
import numpy as np, pandas as pd
from . import exante


def fav_state(df):
    """Subconjunto com HT válido + estado do favorito PRÉ-JOGO no intervalo:
    fav_is_home, margem do favorito no HT, e se o favorito venceu no FT."""
    d = df.dropna(subset=["HTHome", "HTAway", "HTResult"]).copy()
    P = d[["p_H", "p_D", "p_A"]].to_numpy(float)
    fav_home = P.argmax(1) == 0
    d["fav_is_home"] = fav_home
    d["ht_fav_margin"] = np.where(fav_home, d.HTHome - d.HTAway, d.HTAway - d.HTHome)
    d["ft_fav_win"] = np.where(fav_home, d.FTResult == "H", d.FTResult == "A").astype(float)
    d["p0"] = d.p_fav_dv
    return d


def ht_bucket(margin):
    """Estado do favorito no HT: atrás / empatado / à frente por 1 / por 2+."""
    m = np.asarray(margin)
    return np.select([m <= -1, m == 0, m == 1, m >= 2],
                     ["atrás", "empatado", "+1", "+2 ou mais"], default="?")


def conditional_table(d, min_n=500):
    """Por estado do favorito no HT: prob condicional de vitória q (realizada) e a
    skewness implícita do 'resto do jogo' = identidade em q."""
    d = d.copy()
    d["state"] = ht_bucket(d.ht_fav_margin.values)
    order = {"atrás": 0, "empatado": 1, "+1": 2, "+2 ou mais": 3}
    rows = []
    for st, g in d.groupby("state"):
        if len(g) < min_n:
            continue
        q = float(g.ft_fav_win.mean())
        rows.append({"state": st, "n": len(g), "share": len(g) / len(d),
                     "p0_mean": float(g.p0.mean()), "q_cond": q,
                     "skew_cond": float(exante.per_match_skew(np.array([q]))[0])})
    out = pd.DataFrame(rows)
    return out.sort_values("state", key=lambda s: s.map(order)).reset_index(drop=True)


def martingale_check(d, p_edges=(0.0, 0.45, 0.50, 0.55, 1.0)):
    """E[q condicional do HT | faixa de p0] deve voltar ≈ p0 (a info do HT é um
    refinamento martingale da prob pré-jogo). Confirma calibração dinâmica."""
    d = d.copy()
    d["pb"] = pd.cut(d.p0, list(p_edges))
    rows = []
    for b, g in d.groupby("pb", observed=True):
        if len(g) < 500:
            continue
        rows.append({"p_bin": str(b), "n": len(g), "p0_mean": float(g.p0.mean()),
                     "q_mean": float(g.ft_fav_win.mean())})
    return pd.DataFrame(rows)
