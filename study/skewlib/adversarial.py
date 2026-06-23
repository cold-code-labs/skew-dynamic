"""Frente G — robustez adversarial (pré-submissão). Três ataques ao achado:

  G1  o de-vig é confiável e estável? Reliability diagram + decomposição de Brier
      (Murphy) do favorito por liga/ano; e a skewness é invariante ao MÉTODO de
      de-vig e à casa (Odd média vs Max melhor preço, + consenso multi-casa).
  G2  painel BALANCEADO estrito: refaz a série GLOBAL usando só ligas presentes
      em TODOS os anos — mata 100% o confound de composição (P1 fez por-liga).
  G3  block-bootstrap sobre TEMPORADAS (reamostra anos inteiros, respeitando
      dependência intra-ano) → IC honesto de todos os números-título.
"""
import numpy as np, pandas as pd
from . import exante, devig

OUTCOMES = np.array(["H", "D", "A"])


# ── G1 — confiabilidade do de-vig ────────────────────────────────────────────
def fav_won(df):
    """1.0 se o favorito (argmax p de-vigado) venceu o jogo, 0.0 caso contrário."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    j = P.argmax(1)
    return (OUTCOMES[j] == df["FTResult"].to_numpy()).astype(float)


def reliability(p, y, nbins=12, min_bin=40):
    """Diagrama de confiabilidade: prob média prevista vs frequência observada."""
    p = np.asarray(p, float); y = np.asarray(y, float)
    edges = np.linspace(p.min(), p.max(), nbins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, nbins - 1)
    rows = []
    for b in range(nbins):
        m = idx == b
        if m.sum() < min_bin:
            continue
        rows.append({"p_pred": float(p[m].mean()), "freq_obs": float(y[m].mean()),
                     "n": int(m.sum())})
    return pd.DataFrame(rows)


def brier_decomp(p, y, nbins=12):
    """Decomposição de Murphy do Brier score: BS = REL − RES + UNC.
    REL = erro de calibração (↓ melhor); RES = resolução; UNC = incerteza base."""
    p = np.asarray(p, float); y = np.asarray(y, float)
    N = len(y); obar = y.mean()
    edges = np.linspace(p.min(), p.max(), nbins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, nbins - 1)
    rel = res = 0.0
    for b in range(nbins):
        m = idx == b; nk = int(m.sum())
        if nk == 0:
            continue
        fk = p[m].mean(); ok = y[m].mean()
        rel += nk * (fk - ok) ** 2
        res += nk * (ok - obar) ** 2
    rel /= N; res /= N; unc = obar * (1 - obar)
    return {"brier": float(np.mean((p - y) ** 2)), "rel": float(rel),
            "res": float(res), "unc": float(unc), "obar": float(obar)}


def reliability_by(df, col, min_n=3000, nbins=10):
    """REL (erro de calibração) do favorito por grupo (liga ou ano). Estável e
    pequeno ⇒ o de-vig de Shin é confiável de forma homogênea."""
    rows = []
    for key, g in df.groupby(col):
        if len(g) < min_n:
            continue
        d = brier_decomp(g.p_fav_dv.values, fav_won(g), nbins=nbins)
        rows.append({col: key, "n": len(g), "rel": d["rel"], "res": d["res"],
                     "brier": d["brier"]})
    return pd.DataFrame(rows)


def skew_by_devig(df):
    """Skewness agrupada do favorito sob vários de-vigs e casas (consenso
    multi-casa = média das probs de-vigadas de Odd e Max). Invariância ⇒ o achado
    não depende do método nem da casa."""
    odd = ("OddHome", "OddDraw", "OddAway")
    mx = ("MaxHome", "MaxDraw", "MaxAway")
    out = {}
    # Max* (melhor preço) tem faltantes/inválidos — restringe à amostra limpa e
    # COMUM p/ comparar maçãs com maçãs (mesmas linhas em todos os métodos).
    has_max = all(c in df for c in mx)
    base = df
    if has_max:
        ok = df[list(mx)].notna().all(1) & (df[list(mx)] > 1.01).all(1)
        base = df[ok]
    for name, cols, meth in [("shin·odd", odd, "shin"), ("shin·max", mx, "shin"),
                             ("mult·odd", odd, "multiplicative"),
                             ("power·odd", odd, "power")]:
        if not all(c in base for c in cols):
            continue
        _, _, d = exante.market_skew(base, cols, method=meth)
        out[name] = d["skew"]
    # consenso multi-casa: média das probabilidades de-vigadas (Shin) das 2 casas
    if has_max and len(base):
        po = devig.devig_frame(base, method="shin", cols=odd)[["p_H", "p_D", "p_A"]].to_numpy()
        pm = devig.devig_frame(base, method="shin", cols=mx)[["p_H", "p_D", "p_A"]].to_numpy()
        pc = 0.5 * (po + pm); pc = pc / pc.sum(1, keepdims=True)
        j = pc.argmax(1); i = np.arange(len(pc))
        oc = 1.0 / pc[i, j]                       # odd justa do consenso
        out["consenso"] = exante.pooled_skew(pc[i, j], oc)["skew"]
    return out


# ── G2 — painel balanceado estrito ───────────────────────────────────────────
def balanced_leagues(panel, min_frac=1.0):
    """Ligas presentes em ≥ min_frac das temporadas do painel (1.0 = todas)."""
    nseasons = panel.season.nunique()
    cnt = panel.groupby("Division").season.nunique()
    return list(cnt[cnt >= np.ceil(min_frac * nseasons)].index)


def global_series_balanced(df, leagues):
    """Série GLOBAL de skewness ex-ante por ano, restrita às ligas balanceadas."""
    d = df[df.Division.isin(leagues)].copy()
    d["season"] = d.date.dt.year
    rows = []
    for yr, g in d.groupby("season"):
        rows.append({"season": int(yr), "n": len(g),
                     "skew_exante": exante.pooled_skew(g.p_fav_dv.values,
                                                       g.o_fav.values)["skew"]})
    return pd.DataFrame(rows).sort_values("season").reset_index(drop=True)


# ── G3 — block-bootstrap sobre temporadas ────────────────────────────────────
def season_block_bootstrap(df, stat_fn, B=400, seed=42):
    """IC de `stat_fn(boot_df)` reamostrando TEMPORADAS inteiras com reposição
    (preserva a dependência intra-ano que a reamostragem de jogos quebraria)."""
    d = df.copy()
    d["season"] = d.date.dt.year
    seasons = sorted(d.season.unique())
    groups = {s: d[d.season == s] for s in seasons}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        pick = rng.choice(seasons, len(seasons), replace=True)
        vals.append(stat_fn(pd.concat([groups[s] for s in pick], ignore_index=True)))
    vals = np.array([v for v in vals if v == v])      # descarta NaN
    return {"mean": float(vals.mean()), "ci_lo": float(np.percentile(vals, 2.5)),
            "ci_hi": float(np.percentile(vals, 97.5)), "se": float(vals.std())}


def stat_global_skew(d):
    return exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)["skew"]


def stat_league_corr(d, min_n=1500):
    """corr(skew_liga, p_fav_liga) entre ligas — a lei estrutural transversal."""
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        rows.append((exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                     float(g.p_fav_dv.mean())))
    if len(rows) < 5:
        return float("nan")
    a = np.array(rows)
    return float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])
