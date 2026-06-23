"""Mercado over/under 2.5 gols — teste binário LIMPO da identidade mecânica.

Mercado de 2 resultados (sem empate): a skewness de uma aposta unitária depende
SÓ da probabilidade p do lado apostado — exatamente (1-2p)/√(p(1-p)). É o caso
mais nítido do núcleo do W1, sem a complicação de 3 vias do 1X2. O resultado é
observável dos gols (over = FTHome+FTAway ≥ 3), então ex-ante e ex-post podem
ser confrontados diretamente.
"""
import numpy as np, pandas as pd
from . import devig

OU = ("Over25", "Under25")
OU_MAX = ("MaxOver25", "MaxUnder25")


def prep(df, cols=OU, method="shin"):
    """De-viga o mercado O/U 2.5 e monta a aposta no favorito (lado de menor odd).

    Adiciona: p_over, p_under, overround, over (realizado), p_fav_ou, o_fav_ou,
    ret_fav_ou (retorno ex-post). De-vig vetorizado (Shin ou multiplicativo).
    """
    d = df.copy()
    d["goals"] = pd.to_numeric(d.FTHome, errors="coerce") + pd.to_numeric(d.FTAway, errors="coerce")
    d = d.dropna(subset=[*cols, "goals"])
    d = d[(d[cols[0]] > 1.01) & (d[cols[1]] > 1.01)].reset_index(drop=True)

    O = d[list(cols)].to_numpy(float)
    r = 1.0 / O
    bsum = r.sum(1)
    if method == "shin":
        z = np.zeros(len(r)); vig = bsum > 1.0
        if vig.any():
            z[vig] = devig._shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        P = np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
        d["shin_z"] = z
    else:
        P = r / bsum[:, None]

    d["p_over"], d["p_under"] = P[:, 0], P[:, 1]
    d["overround"] = bsum
    d["over"] = (d.goals >= 3).astype(int)

    fav_over = O[:, 0] <= O[:, 1]                       # favorito = menor odd
    d["o_fav_ou"] = np.where(fav_over, O[:, 0], O[:, 1])
    d["p_fav_ou"] = np.where(fav_over, d.p_over, d.p_under)
    win = np.where(fav_over, d.over == 1, d.over == 0)
    d["ret_fav_ou"] = np.where(win, d.o_fav_ou - 1.0, -1.0)
    return d
