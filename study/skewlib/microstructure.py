"""Frente D — microestrutura / formação de preço (no dataset congelado):

  D2  sharp vs soft: a skewness diverge entre a odd MÉDIA (Odd*, mais soft) e a
      MELHOR odd (Max*, ~sharp/arb)? Por liga.
  D3  Shin z (fração de dinheiro informado) como SÉRIE: z por liga/ano/mercado,
      sua estabilidade e relação com competitividade/overround.
  D4  mercado de HANDICAP ASIÁTICO (Handi*): um 3º mercado (além de 1X2 e O/U)
      p/ testar a identidade (1−2p)/√(p(1−p)). Como o AH balanceia o jogo para
      ~50/50, prevê-se p_fav≈0.5 ⇒ skew≈0 — mesma identidade, outro regime de p.
"""
import numpy as np, pandas as pd
from . import devig, exante

ODD = ("OddHome", "OddDraw", "OddAway")
MAX = ("MaxHome", "MaxDraw", "MaxAway")
AH = ("HandiHome", "HandiAway")


# ── D2 — sharp vs soft ───────────────────────────────────────────────────────
def skew_by_book_league(df, min_n=2000):
    """Skewness e overround do favorito por liga, sob Odd* (soft) e Max* (sharp)."""
    ok = df[list(MAX)].notna().all(1) & (df[list(MAX)] > 1.01).all(1)
    d = df[ok]
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        ps, os_, ds = exante.market_skew(g, ODD, method="shin")
        pm, om, dm = exante.market_skew(g, MAX, method="shin")
        rows.append({"Division": lg, "n": len(g),
                     "skew_soft": ds["skew"], "skew_sharp": dm["skew"],
                     "over_soft": float((1 / g[list(ODD)]).sum(1).mean()),
                     "over_sharp": float((1 / g[list(MAX)]).sum(1).mean()),
                     "p_fav": float(g.p_fav_dv.mean())})
    out = pd.DataFrame(rows)
    out["d_skew"] = out.skew_sharp - out.skew_soft
    return out


# ── D3 — Shin z como série ───────────────────────────────────────────────────
def shin_z_frame(df):
    """Adiciona shin_z (1X2) por jogo + overround + season."""
    d = devig.devig_frame(df, method="shin", cols=ODD)
    d["season"] = d.date.dt.year
    return d


def z_by(d, col, min_n=2000):
    """Média de z (dinheiro informado) + overround + competitividade por grupo."""
    rows = []
    for key, g in d.groupby(col):
        if len(g) < min_n:
            continue
        rows.append({col: key, "n": len(g), "z": float(g.shin_z.mean()),
                     "overround": float(g.overround.mean()),
                     "p_fav": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


# ── D4 — handicap asiático (3º mercado) ──────────────────────────────────────
def prep_ah(df, method="shin"):
    """De-viga o mercado AH de 2 vias (HandiHome/HandiAway) e monta a aposta no
    favorito (menor odd). Filtra a linha sentinela -99.9 e odds inválidas.
    Devolve p_fav_ah, o_fav_ah, skew por jogo e o realizado quando inequívoco
    (linhas inteiras/meias; pula linhas de quarto, que dão meia-vitória)."""
    d = df.copy()
    d = d[(d.HandiSize > -50) & d[list(AH)].notna().all(1)
          & (d[list(AH)] > 1.01).all(1)].reset_index(drop=True)
    O = d[list(AH)].to_numpy(float)
    r = 1.0 / O; bsum = r.sum(1)
    if method == "shin":
        z = np.zeros(len(r)); vig = bsum > 1.0
        if vig.any():
            z[vig] = devig._shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        P = np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
    else:
        P = r / bsum[:, None]
    d["p_home_ah"], d["p_away_ah"] = P[:, 0], P[:, 1]
    d["overround_ah"] = bsum
    fav_home = O[:, 0] <= O[:, 1]
    d["o_fav_ah"] = np.where(fav_home, O[:, 0], O[:, 1])
    d["p_fav_ah"] = np.where(fav_home, d.p_home_ah, d.p_away_ah)
    d["skew_ah_match"] = exante.per_match_skew(d.p_fav_ah.values)

    # realizado: margem de gols ajustada pela linha (sinal: handicap do MANDANTE)
    gd = pd.to_numeric(d.FTHome, errors="coerce") - pd.to_numeric(d.FTAway, errors="coerce")
    adj = gd + d.HandiSize                     # >0 casa cobre, <0 fora cobre, 0 push
    quarter = (np.abs(d.HandiSize * 2) % 1) > 0.1      # linha de quarto → pula
    home_cover = adj > 0
    settle = (~quarter) & (adj != 0)
    win_fav = np.where(fav_home, home_cover, ~home_cover)
    d["ah_settled"] = settle
    d["ret_fav_ah"] = np.where(win_fav, d.o_fav_ah - 1.0, -1.0)
    return d


def ah_league(d, min_n=2000):
    """Skewness ex-ante agrupada do favorito AH por liga."""
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        dd = exante.pooled_skew(g.p_fav_ah.values, g.o_fav_ah.values)
        rows.append({"Division": lg, "n": len(g), "skew_ah": dd["skew"],
                     "within_frac": dd["within_frac"],
                     "p_fav_ah": float(g.p_fav_ah.mean())})
    return pd.DataFrame(rows)
