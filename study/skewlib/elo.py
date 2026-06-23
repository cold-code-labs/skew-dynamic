"""Elo a partir SÓ de resultados (sem odds) → competitividade odds-free por liga.

Motivação: a relação skewness ~ competitividade do Bloco E/W1 usa `p_fav`
derivada das próprias odds — circular. Aqui medimos a competitividade de cada
liga por um sistema Elo construído exclusivamente sobre resultados (W/D/L e
saldo de gols), sem nenhuma informação de mercado. Se a relação sobreviver,
ela é estrutural (esportiva), não um artefato do apreçamento.

Passo único cronológico sobre TODAS as ligas empilhadas (um time carrega seu
rating ao subir/descer de divisão). O mapa rating-diff → (P_H,P_D,P_A) é
calibrado empiricamente nos resultados (MNLogit), também sem odds.

Saídas por liga (todas odds-free):
  elo_entropy  entropia média da previsão de 3 resultados (alta = parelha)
  elo_pfav     prob. média do favorito Elo  (análogo odds-free de p_fav_dv)
  elo_disp     dispersão (sd) das forças dos times dentro de temporada
  upset_rate   fração de jogos em que o resultado mais provável (Elo) não saiu
"""
import numpy as np, pandas as pd


def run_elo(df, k=20.0, hfa=65.0, init=1500.0, gd_mult=True):
    """Passa Elo cronológico. Adiciona elo_h, elo_a (pré-jogo) e elo_diff (com HFA)."""
    d = df.sort_values("date").reset_index(drop=True)
    R = {}
    rh = np.empty(len(d)); ra = np.empty(len(d))
    home = d.HomeTeam.values; away = d.AwayTeam.values; res = d.FTResult.values
    fh = pd.to_numeric(d.FTHome, errors="coerce").values
    fa = pd.to_numeric(d.FTAway, errors="coerce").values
    for i in range(len(d)):
        Rh = R.get(home[i], init); Ra = R.get(away[i], init)
        rh[i] = Rh; ra[i] = Ra
        Eh = 1.0 / (1.0 + 10 ** (-((Rh + hfa) - Ra) / 400.0))
        Sh = 1.0 if res[i] == "H" else (0.5 if res[i] == "D" else 0.0)
        kk = k
        if gd_mult and not (np.isnan(fh[i]) or np.isnan(fa[i])):
            kk = k * (1.0 + np.log1p(max(abs(fh[i] - fa[i]) - 1.0, 0.0)))
        delta = kk * (Sh - Eh)
        R[home[i]] = Rh + delta; R[away[i]] = Ra - delta
    d["elo_h"] = rh; d["elo_a"] = ra
    d["elo_diff"] = (rh + hfa) - ra
    return d, R


def calibrate_outcomes(d):
    """Mapa odds-free rating-diff → (P_A,P_D,P_H) via MNLogit nos resultados."""
    import statsmodels.api as sm
    y = d.FTResult.map({"A": 0, "D": 1, "H": 2}).values
    z = d.elo_diff.values / 400.0
    X = sm.add_constant(np.column_stack([z, z * z]))
    m = sm.MNLogit(y, X).fit(disp=0)
    P = np.asarray(m.predict(X))               # colunas em ordem 0,1,2 = A,D,H
    out = d.copy()
    out["pA_elo"], out["pD_elo"], out["pH_elo"] = P[:, 0], P[:, 1], P[:, 2]
    return out, m


def add_elo_features(d):
    """Entropia, prob. do favorito Elo e flag de zebra por jogo."""
    P = d[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float)
    out = d.copy()
    out["elo_entropy"] = -(P * np.log(np.clip(P, 1e-12, 1.0))).sum(1)
    out["elo_pfav"] = P.max(1)
    pred = np.array(["H", "D", "A"])[P.argmax(1)]
    out["elo_upset"] = pred != d.FTResult.values
    return out


def with_elo(df, **kw):
    """Pipeline completa: Elo + calibração + features por jogo."""
    d, _ = run_elo(df, **kw)
    d, _ = calibrate_outcomes(d)
    return add_elo_features(d)


def league_competitiveness(d):
    """Tabela odds-free de competitividade por liga (Division)."""
    d = d.copy()
    d["season"] = d.date.dt.year
    long = pd.concat([
        d[["Division", "season", "elo_h"]].rename(columns={"elo_h": "elo"}),
        d[["Division", "season", "elo_a"]].rename(columns={"elo_a": "elo"}),
    ])
    disp = (long.groupby(["Division", "season"]).elo.std()
                .groupby("Division").mean().rename("elo_disp"))
    agg = d.groupby("Division").agg(
        n=("FTResult", "size"),
        elo_entropy=("elo_entropy", "mean"),
        elo_pfav=("elo_pfav", "mean"),
        upset_rate=("elo_upset", "mean"),
    )
    return agg.join(disp).reset_index()
