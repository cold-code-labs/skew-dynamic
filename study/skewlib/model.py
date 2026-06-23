"""Derivação formal: skewness = f(dispersão de força) via ordered-probit.

Template de Goddard-Asimakopoulos (2004) / Koning (2000): a força de cada time
r ~ N(0, σ_L²); num jogo a diferença d = r_i − r_j ~ N(0, 2σ_L²). A margem
latente y* = d + h + ε (ε~N(0,1), h = vantagem de casa) gera (A,D,H) por cutoffs
±c:
    P(A)=Φ(−c−μ),  P(H)=1−Φ(c−μ),  P(D)=Φ(c−μ)−Φ(−c−μ),   μ = d + h.
O favorito tem prob p = max(P_H,P_D,P_A). Sob odds JUSTAS (o=1/p) o favorito tem
média zero, então a skewness AGRUPADA da liga é
    S(σ_L) = E[m₃(p)] / E[σ²(p)]^{3/2},  com σ²=(1−p)/p, m₃=(1−p)(1−2p)/p²,
uma função monótona de σ_L. σ_L é a competitividade: pequeno = parelho.
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import fsolve


def outcome_probs(d, h, c):
    mu = d + h
    cdf_hi = norm.cdf(c - mu); cdf_lo = norm.cdf(-c - mu)
    return 1 - cdf_hi, cdf_hi - cdf_lo, cdf_lo      # pH, pD, pA


def _d(sigma_L, n, seed):
    return np.random.default_rng(seed).normal(0.0, np.sqrt(2.0) * sigma_L, n)


def _pfav(d, h, c):
    pH, pD, pA = outcome_probs(d, h, c)
    return np.clip(np.maximum.reduce([pH, pD, pA]), 1e-6, 1 - 1e-6)


def marginals(sigma_L, h, c, n=200000, seed=1):
    d = _d(sigma_L, n, seed)
    pH, pD, pA = outcome_probs(d, h, c)
    return {"home": float(pH.mean()), "draw": float(pD.mean()),
            "away": float(pA.mean()), "p_fav": float(_pfav(d, h, c).mean())}


def league_skew(sigma_L, h, c, n=200000, seed=1):
    """Skewness agrupada da liga sob odds justas — fechada em p."""
    p = _pfav(_d(sigma_L, n, seed), h, c)
    s2 = (1 - p) / p
    m3 = (1 - p) * (1 - 2 * p) / p ** 2
    return float(m3.mean() / s2.mean() ** 1.5)


def _fair_central_moments(p, max_order=6):
    """Momentos centrais por jogo sob odds JUSTAS (o=1/p ⇒ média zero):
        m_k = (1-p)/p^(k-1) · [ (1-p)^(k-1) + (-1)^k · p^(k-1) ].
    Recupera s²=(1-p)/p e m₃=(1-p)(1-2p)/p² usados em `league_skew`."""
    p = np.asarray(p, float)
    return {k: (1 - p) / p ** (k - 1) * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1))
            for k in range(2, max_order + 1)}


def league_moments(sigma_L, h, c, n=200000, seed=1, max_order=6):
    """Momentos PADRONIZADOS da liga sob odds justas — var/skew/kurtose/etc.
    fechados na distribuição de p_fav. Como todas as apostas têm média zero, não
    há termo entre-jogos: M_k = E[m_k(p)]. Generaliza `league_skew` (ordem 3) e
    permite prever a FORMA inteira (não só o 3º momento) a partir de σ_L."""
    p = _pfav(_d(sigma_L, n, seed), h, c)
    m = _fair_central_moments(p, max_order)
    M2 = float(m[2].mean())
    res = {"var": M2}
    if max_order >= 3: res["skew"] = float(m[3].mean() / M2 ** 1.5)
    if max_order >= 4: res["exkurt"] = float(m[4].mean() / M2 ** 2 - 3.0)
    if max_order >= 5: res["std5"] = float(m[5].mean() / M2 ** 2.5)
    if max_order >= 6: res["std6"] = float(m[6].mean() / M2 ** 3)
    return res


def calibrate(home=0.444, draw=0.264, pfav=0.499, n=200000):
    """Resolve (h, c, σ_ref) para casar as taxas marginais médias observadas."""
    def eqs(x):
        h, c, s = x
        m = marginals(abs(s), h, abs(c), n=n, seed=7)
        return [m["home"] - home, m["draw"] - draw, m["p_fav"] - pfav]
    h, c, s = fsolve(eqs, [0.2, 0.5, 0.4])
    return {"h": float(h), "c": float(abs(c)), "sigma_ref": float(abs(s))}


def curve(h, c, sigmas, n=200000, seed=3):
    """Traça (mean p_fav, skewness) ao longo de uma grade de σ_L."""
    pf, sk = [], []
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        sk.append(league_skew(s, h, c, n=n, seed=seed))
    return np.array(pf), np.array(sk)


def curve_moments(h, c, sigmas, n=200000, seed=3, max_order=6):
    """Traça (mean p_fav, {var, skew, exkurt, ...}) ao longo da grade de σ_L —
    a curva teórica de CADA momento, p/ prever a forma de cada liga pelo p_fav."""
    keys = ["var", "skew", "exkurt", "std5", "std6"][: max_order - 1]
    pf = []; mom = {k: [] for k in keys}
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        lm = league_moments(s, h, c, n=n, seed=seed, max_order=max_order)
        for k in keys:
            mom[k].append(lm[k])
    return np.array(pf), {k: np.array(v) for k, v in mom.items()}
