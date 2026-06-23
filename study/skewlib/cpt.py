"""Cumulative Prospect Theory: a ponderação de probabilidade por trás do FLB
(Frente C2). O favourite–longshot bias é a assinatura do **probability weighting**:
apostadores superponderam probabilidades pequenas (azarões) e subponderam grandes
(favoritos). Modelamos a prob implícita de-vigada `q` como o **peso de decisão** da
prob objetiva `π`:  q ≈ w(π), com a função de Tversky-Kahneman (1992)
    w(p) = p^γ / (p^γ + (1−p)^γ)^{1/γ},     γ<1 ⇒ inverse-S (overweight de azarão),
ou Prelec (1998) como alternativa. γ é um parâmetro de PREFERÊNCIA. A tese de C2: ele
é, ele próprio, um INVARIANTE — estável entre ligas e no tempo (como a skewness).

Caveat: a forma reduzida ignora a renormalização do de-vig por jogo (Σq=1, mas Σw≠1);
γ é a curva de calibração reduzida, não um estimador estrutural puro de CPT — mas é
o objeto padrão da literatura de FLB (Snowberg-Wolfers 2010; Jullien-Salanié 2000).
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar


def w_tk(p, gamma):
    """Ponderação de probabilidade de Tversky-Kahneman."""
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return p ** gamma / (p ** gamma + (1 - p) ** gamma) ** (1.0 / gamma)


def w_prelec(p, alpha, beta=1.0):
    """Ponderação de Prelec (curvatura α, elevação β)."""
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return np.exp(-beta * (-np.log(p)) ** alpha)


def implied_proportional(df, ocols=("OddHome", "OddDraw", "OddAway")):
    """Prob implícita por de-vig PROPORCIONAL (multiplicativo): q_k = (1/o_k)/Σ(1/o_j).
    Remove a margem proporcionalmente, mas PRESERVA o favourite–longshot bias (não
    o modela como o Shin) — é o objeto certo p/ revelar a ponderação de probabilidade."""
    O = df[list(ocols)].to_numpy(float)
    inv = 1.0 / O
    return inv / inv.sum(axis=1, keepdims=True)


def calibration(df, nbins=25, legs=("H", "D", "A")):
    """Diagrama de confiabilidade sobre as 3 pernas (cobre [0,1]: azarão→favorito):
    prob implícita PROPORCIONAL `q` vs taxa de acerto objetiva `π`, binado por `q`.
    Usa o implícito proporcional (não o Shin de-vigado) para não apagar o FLB que
    se quer medir."""
    q = implied_proportional(df)
    res = df.FTResult.values
    parts = [pd.DataFrame({"q": q[:, i], "hit": (res == leg).astype(float)})
             for i, leg in enumerate(legs)]
    d = pd.concat(parts, ignore_index=True)
    d["b"] = pd.qcut(d.q, nbins, duplicates="drop")
    return (d.groupby("b", observed=True)
             .agg(q=("q", "mean"), pi=("hit", "mean"), n=("hit", "size"))
             .reset_index(drop=True))


def fit_gamma(cal, bounds=(0.3, 1.6)):
    """Ajusta γ de TK por mínimos quadrados ponderados: q ≈ w_tk(π, γ)."""
    pi, q, wts = cal.pi.values, cal.q.values, cal.n.values
    r = minimize_scalar(lambda g: float(np.sum(wts * (q - w_tk(pi, g)) ** 2)),
                        bounds=bounds, method="bounded")
    return float(r.x)


def gamma_by(df, col, min_n=4000, nbins=15):
    """γ ajustado por grupo (liga ou temporada) — para testar invariância."""
    rows = []
    for k, g in df.groupby(col):
        if len(g) < min_n:
            continue
        cal = calibration(g, nbins=nbins)
        if len(cal) < 5:
            continue
        rows.append({col: k, "n": int(len(g)), "gamma": fit_gamma(cal),
                     "p_fav_dv": float(g.p_fav_dv.mean())})
    return pd.DataFrame(rows)
