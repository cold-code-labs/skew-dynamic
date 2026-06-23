"""Índices de balanço competitivo (CB) a partir da CLASSIFICAÇÃO — resultados,
sem odds. Fonte 100% independente do mercado → ataque mais forte à circularidade
que o próprio Elo.

Usamos as medidas canônicas e ROBUSTAS A TAMANHO de liga recomendadas pela
literatura, evitando o Gini (Utt & Fort 2002: inválido para jogo de soma-zero):
  - Noll-Scully  = SD(win%) / SD idealizada (0.5/√G)   [dispersão de força]
  - HHI*         = HHI de vitórias normalizado p/ N times (Owen et al. 2007)
  - Theil (GE1)  = entropia generalizada dos pontos (Borooah & Mangan 2012)
Todas crescem com o DESEQUILÍBRIO (menos competitividade).
"""
import numpy as np, pandas as pd


def season_of(dates):
    """Temporada de futebol (Ago–Mai): mês ≥ 7 → ano corrente, senão ano−1."""
    d = pd.to_datetime(dates)
    return np.where(d.dt.month >= 7, d.dt.year, d.dt.year - 1)


def standings(df):
    """Por (Division, season, team): jogos, vitórias-equivalentes (W+0.5D), pontos."""
    d = df.copy()
    d["season"] = season_of(d.date)
    parts = []
    for team_col, win_res in [("HomeTeam", "H"), ("AwayTeam", "A")]:
        t = d[["Division", "season", team_col, "FTResult"]].rename(columns={team_col: "team"})
        t["w"] = (t.FTResult == win_res).astype(float)
        t["draw"] = (t.FTResult == "D").astype(float)
        parts.append(t[["Division", "season", "team", "w", "draw"]])
    long = pd.concat(parts)
    g = long.groupby(["Division", "season", "team"]).agg(
        games=("w", "size"), wins=("w", "sum"), draws=("draw", "sum")).reset_index()
    g["weq"] = g.wins + 0.5 * g.draws
    g["winpct"] = g.weq / g.games
    g["points"] = 3 * g.wins + g.draws
    return g


def cb_indices(stand, min_teams=6, min_games=10):
    """Índices de CB por (Division, season)."""
    rows = []
    for (lg, se), t in stand.groupby(["Division", "season"]):
        t = t[t.games >= min_games]
        N = len(t)
        if N < min_teams:
            continue
        gbar = t.games.mean()
        ns = t.winpct.std(ddof=0) / (0.5 / np.sqrt(gbar))      # Noll-Scully
        s = t.wins / t.wins.sum()
        hhi_star = ((s ** 2).sum() - 1 / N) / (1 - 1 / N)       # HHI normalizado
        x = t.points.values; mu = x.mean()
        theil = float(np.mean((x / mu) * np.log(np.clip(x / mu, 1e-12, None))))
        rows.append({"Division": lg, "season": int(se), "n_teams": N,
                     "noll_scully": float(ns), "hhi_star": float(hhi_star), "theil": theil})
    return pd.DataFrame(rows)


def by_league(cb):
    """Média dos índices por liga (sobre temporadas)."""
    return cb.groupby("Division").agg(
        seasons=("season", "size"),
        noll_scully=("noll_scully", "mean"),
        hhi_star=("hhi_star", "mean"),
        theil=("theil", "mean")).reset_index()
