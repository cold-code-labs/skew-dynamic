"""Frente F — dentro da liga / micro:

  F1  sazonalidade intra-temporada: a skewness se move do início ao fim da
      temporada (conforme a classificação cristaliza)? Controlada por liga.
  F2  contribuição por competitividade do JOGO: que jogos carregam a skewness da
      liga? Decompõe o M₃ agrupado por faixa de p_fav (o cancelamento de caudas).
  F3  decomposição por time: clubes dominantes (Elo alto) "puxam" a assinatura da
      liga para jogos desequilibrados (skew negativa)?
"""
import numpy as np, pandas as pd
from . import exante


def add_season_phase(df, nseg=3):
    """Temporada real (Ago→Jul) + fase intra-temporada (terço por data dentro da
    liga×temporada). Evita partir uma temporada europeia em 2 anos-calendário."""
    d = df.copy()
    d["season"] = np.where(d.date.dt.month >= 7, d.date.dt.year, d.date.dt.year - 1)
    d["frac"] = d.groupby(["Division", "season"]).date.rank(pct=True)
    d["phase"] = np.clip((d.frac * nseg).astype(int), 0, nseg - 1)
    return d


# ── F1 — sazonalidade intra-temporada ────────────────────────────────────────
def skew_by_phase(d, min_n=2000):
    """Skewness ex-ante por fase intra-temporada (0=início … nseg−1=fim), global."""
    rows = []
    for ph, g in d.groupby("phase"):
        if len(g) < min_n:
            continue
        rows.append({"phase": int(ph), "n": len(g),
                     "skew": exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                     "p_fav": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)


def phase_shift_by_league(d, min_n=400):
    """Δskew (fim − início) por liga: a temporada cristaliza a assimetria?"""
    rows = []
    for lg, g in d.groupby("Division"):
        ph = {p: exante.pooled_skew(x.p_fav_dv.values, x.o_fav.values)["skew"]
              for p, x in g.groupby("phase") if len(x) >= min_n}
        if 0 in ph and (g.phase.max()) in ph:
            rows.append({"Division": lg, "skew_start": ph[0],
                         "skew_end": ph[g.phase.max()],
                         "shift": ph[g.phase.max()] - ph[0]})
    return pd.DataFrame(rows)


# ── F2 — contribuição por competitividade do jogo ────────────────────────────
def m3_contribution_by_bin(df, edges=(0.0, 0.42, 0.46, 0.50, 0.55, 0.65, 1.0)):
    """Decompõe o M₃ agrupado por faixa de p_fav: quais jogos carregam a skewness.
    Sob odds quase justas M₃≈E[m₃(p)]; reportamos a contribuição (soma de m₃) e a
    skew por faixa — o cancelamento de caudas (favoritos fracos + / fortes −)."""
    p = df.p_fav_dv.values; o = df.o_fav.values
    _, _, m3 = exante.per_match_moments(p, o)
    tot = m3.sum()
    b = pd.cut(pd.Series(p), list(edges))
    g = pd.DataFrame({"p": p, "m3": m3, "bin": b}).groupby("bin", observed=True)
    rows = []
    for key, x in g:
        rows.append({"bin": str(key), "n": len(x), "p_mid": float(x.p.mean()),
                     "skew_match": float(exante.per_match_skew(x.p.mean())),
                     "m3_share": float(x.m3.sum() / tot)})
    return pd.DataFrame(rows), float(tot)


# ── F3 — decomposição por time ───────────────────────────────────────────────
def team_long(df):
    """Formato longo: 1 linha por (jogo, time) com Elo do time, prob de vitória
    de-vigada e se foi o favorito do jogo."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    fav_is_home = (P.argmax(1) == 0)
    home = pd.DataFrame({"team": df.HomeTeam.values, "elo": df.HomeElo.values,
                         "p_win": df.p_H.values, "is_fav": fav_is_home,
                         "p_fav": df.p_fav_dv.values, "Division": df.Division.values})
    away = pd.DataFrame({"team": df.AwayTeam.values, "elo": df.AwayElo.values,
                         "p_win": df.p_A.values, "is_fav": ~fav_is_home,
                         "p_fav": df.p_fav_dv.values, "Division": df.Division.values})
    return pd.concat([home, away], ignore_index=True)


def team_dominance(df, min_games=200):
    """Por time: Elo médio (dominância) e skewness ex-ante dos jogos que disputa.
    Clubes dominantes ⇒ jogos desequilibrados ⇒ contribuição de skew negativa."""
    tl = team_long(df)
    rows = []
    for tm, g in tl.groupby("team"):
        if len(g) < min_games:
            continue
        rows.append({"team": tm, "Division": g.Division.mode().iloc[0], "n": len(g),
                     "elo": float(g.elo.mean()), "fav_rate": float(g.is_fav.mean()),
                     "skew_games": float(exante.per_match_skew(g.p_fav.values).mean())})
    return pd.DataFrame(rows)
