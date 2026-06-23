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
