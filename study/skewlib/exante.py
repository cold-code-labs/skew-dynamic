"""Skewness ex-ante (implícita) da aposta no favorito, a partir de
probabilidades de-vigadas — o objeto PRIMÁRIO do estudo.

Para uma aposta unitária no favorito a odd decimal o e prob. verdadeira p:
    retorno = (o-1) com prob p ;  -1 com prob (1-p)
É uma distribuição de dois pontos (Bernoulli reescalada), de momentos centrais
fechados:
    média  mu = p*o - 1
    var    s2 = p(1-p) o²
    3º     m3 = p(1-p)(1-2p) o³
A skewness POR JOGO depende só de p:   (1-2p)/√(p(1-p))  → cruza 0 em p=0.5.
A skewness AGRUPADA (liga/janela) é a da mistura desses jogos, decomposta por
lei dos cumulantes totais — separando o termo mecânico (assimetria intra-jogo,
o FLB) da dispersão entre jogos. É o que desarma a crítica de tautologia: a
skewness de mercado é, em 1ª ordem, a imagem algébrica da distribuição de p.
"""
from math import comb
import numpy as np, pandas as pd
from . import devig


def _fav(df):
    """odd e prob de-vigada do favorito (= argmax p = argmin odd)."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    O = df[["OddHome", "OddDraw", "OddAway"]].to_numpy(float)
    j = P.argmax(axis=1)
    i = np.arange(len(P))
    return P[i, j], O[i, j]


def per_match_moments(p, o):
    """Momentos centrais (média, variância, 3º) da aposta de dois pontos."""
    mu = p * o - 1.0
    s2 = p * (1 - p) * o ** 2
    m3 = p * (1 - p) * (1 - 2 * p) * o ** 3
    return mu, s2, m3


def per_match_skew(p):
    """Skewness ex-ante de um único jogo — só função de p."""
    p = np.asarray(p, float)
    return (1 - 2 * p) / np.sqrt(p * (1 - p))


def per_match_central_moments(p, o, max_order=6):
    """Momentos centrais POR JOGO da aposta de dois pontos, ordens 0..max_order.

    Forma fechada para todas as ordens (a aposta é uma Bernoulli reescalada):
        m_k = o^k · p(1-p) · [ (1-p)^(k-1) + (-1)^k · p^(k-1) ],   m_0=1, m_1=0.
    Recupera m_2 = o²p(1-p) e m_3 = o³p(1-p)(1-2p) de `per_match_moments`.
    Devolve uma lista `m` com m[k] = array por jogo (m[0]≡1, m[1]≡0).
    """
    p = np.asarray(p, float); o = np.asarray(o, float)
    pp = p * (1 - p)
    m = [np.ones_like(p), np.zeros_like(p)]
    for k in range(2, max_order + 1):
        m.append(o ** k * pp * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1)))
    return m


def pooled_moments(p, o, max_order=6):
    """Momentos da MISTURA (liga/janela) + fração mecânica por ordem.

    Generaliza `pooled_skew` para a forma inteira da distribuição implícita. Os
    momentos centrais da mistura saem da lei dos momentos totais (peso igual,
    desvio da média do jogo d_i = mu_i − M1):
        M_k = E_i[ Σ_{j=0..k} C(k,j) · m_{j,i} · d_i^(k-j) ]   (m_0=1, m_1=0)
      → M2 = E[m2]+E[d²];  M3 = E[m3]+3E[m2·d]+E[d³];
        M4 = E[m4]+4E[m3·d]+6E[m2·d²]+E[d⁴]; idem 5/6.
    A fração `within` (= E[m_k]/M_k) mede quanto de cada momento é MECÂNICO
    (assimetria/forma intra-jogo, o FLB) vs gerado pela dispersão entre jogos.
    Devolve var/skew/exkurt + padronizados 5/6, M_k, within_frac por ordem, e a
    decomposição em 3 vias do M3 (within3/cov3/between3) usada por `pooled_skew`.
    """
    p = np.asarray(p, float); o = np.asarray(o, float)
    mu = p * o - 1.0
    m = per_match_central_moments(p, o, max_order)
    M1 = mu.mean()
    d = mu - M1
    Mk, within = {}, {}
    res = {"mean": float(M1)}
    for k in range(2, max_order + 1):
        s = np.zeros_like(p)
        for j in range(0, k + 1):
            if j == 1:
                continue                       # m_1 = 0
            s = s + comb(k, j) * m[j] * d ** (k - j)
        Mk[k] = float(s.mean())
        within[k] = float(m[k].mean())
        res[f"M{k}"] = Mk[k]
        res[f"within_frac_m{k}"] = within[k] / Mk[k] if Mk[k] != 0 else float("nan")
    M2 = Mk[2]
    res["var"] = M2
    if max_order >= 3:
        res["skew"] = Mk[3] / M2 ** 1.5
        # decomposição em 3 vias do M3 (compatibilidade com pooled_skew)
        res["within3"]  = within[3]
        res["cov3"]     = float((comb(3, 2) * m[2] * d).mean())   # 3·E[m2·d]
        res["between3"] = float((d ** 3).mean())
    if max_order >= 4:
        res["exkurt"] = Mk[4] / M2 ** 2 - 3.0
    if max_order >= 5:
        res["std5"] = Mk[5] / M2 ** 2.5
    if max_order >= 6:
        res["std6"] = Mk[6] / M2 ** 3
    return res


def pooled_skew(p, o):
    """Skewness da mistura + decomposição (lei dos momentos totais).

        M3 = E[m3_i]                  (mecânico: assimetria intra-jogo / FLB)
           + 3·E[s2_i·(mu_i-mu)]      (covariância variância×média)
           + E[(mu_i-mu)³]            (dispersão entre jogos)
        V  = E[s2_i] + Var(mu_i),   skew = M3 / V^1.5.

    Caso de 3ª ordem de `pooled_moments`; mantém as formas explícitas
    de `per_match_moments` para saída bit-idêntica ao baseline congelado.
    """
    p = np.asarray(p, float); o = np.asarray(o, float)
    mu, s2, m3 = per_match_moments(p, o)
    d = mu - mu.mean()
    within  = m3.mean()
    cov     = 3.0 * (s2 * d).mean()
    between = (d ** 3).mean()
    M3 = within + cov + between
    V = s2.mean() + d.var()
    skew = M3 / V ** 1.5
    return {"skew": float(skew), "M3": float(M3), "V": float(V),
            "within": float(within), "cov": float(cov), "between": float(between),
            "within_frac": float(within / M3), "cov_frac": float(cov / M3),
            "between_frac": float(between / M3)}


def market_skew(df, odd_cols, method=None):
    """De-viga um mercado 1X2 qualquer (ex.: odds médias vs máximas) e devolve
    (p_fav, o_fav, decomposição pooled). Usado no teste de ortogonalidade da
    margem: a skewness muda entre casas/margens?"""
    dd = devig.devig_frame(df, method=method, cols=odd_cols)
    P = dd[["p_H", "p_D", "p_A"]].to_numpy(float)
    O = df[list(odd_cols)].to_numpy(float)
    j = P.argmax(axis=1); i = np.arange(len(P))
    p, o = P[i, j], O[i, j]
    return p, o, pooled_skew(p, o)


def add_exante(df, method=None):
    """De-viga, identifica o favorito e adiciona p_fav_dv, o_fav, skew_exante_match."""
    out = devig.devig_frame(df, method=method)
    p, o = _fav(out)
    out["p_fav_dv"] = p
    out["o_fav"] = o
    out["skew_exante_match"] = per_match_skew(p)
    return out


def pooled_by(df, col, min_n=50, expost_col="ret_fav"):
    """Skewness ex-ante agrupada por `col` + skew ex-post realizada lado a lado.

    Requer df já passado por add_exante (p_fav_dv, o_fav) e, se houver
    `expost_col`, por returns.add_returns. Devolve uma linha por grupo.
    """
    from scipy.stats import skew
    rows = []
    for key, g in df.groupby(col, observed=True):
        if len(g) < min_n:
            continue
        d = pooled_skew(g.p_fav_dv.values, g.o_fav.values)
        row = {col: key, "n": len(g), "skew_exante": d["skew"],
               "within_frac": d["within_frac"], "between_frac": d["between_frac"],
               "p_fav_dv_mean": float(g.p_fav_dv.mean()),
               "overround_mean": float(g.overround.mean())}
        if expost_col in g:
            row["skew_expost"] = float(skew(g[expost_col]))
        rows.append(row)
    return pd.DataFrame(rows)
