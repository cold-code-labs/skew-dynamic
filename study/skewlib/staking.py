"""Front C3 — Kelly / optimal staking under the skewness/CPT structure. What does
the asymmetry imply for optimal bankroll growth?

For a unit bet on the outcome with TRUE probability p at decimal odd o:
  return X = (o−1) with prob p, −1 with prob (1−p);  EV = p·o − 1.
The Kelly fraction maximises E[log(1+f·X)]:
  f* = (p·o − 1)/(o − 1)   (clipped to [0,1]; 0 if EV≤0).
The optimal growth rate g* = p·log(1+f*(o−1)) + (1−p)·log(1−f*) and the
moment APPROXIMATION g ≈ μ − σ²/2 + skew·σ³/3 show the ROLE of skewness:
under fair prices (o=1/p) everyone has EV 0 and f*=0; under the real margin (o<1/p) the EV is
negative and Kelly says DO NOT bet — the structure offers no growth. The skewness
term explains why the longshot bettor (skew +) tolerates negative EV:
positive asymmetry ADDS to log utility/growth.
"""
import numpy as np


def kelly_fraction(p, o):
    """Kelly f* (clipped to [0,1]); 0 when EV ≤ 0."""
    p = np.asarray(p, float); o = np.asarray(o, float)
    b = o - 1.0
    f = (p * o - 1.0) / b
    return np.clip(f, 0.0, 1.0)


def growth_rate(p, o, f):
    """Expected log growth rate of betting the fraction f."""
    p = np.asarray(p, float); o = np.asarray(o, float); f = np.asarray(f, float)
    win = np.log1p(f * (o - 1.0))
    lose = np.log1p(-f)
    return p * win + (1 - p) * lose


def moment_growth_terms(p, o, f):
    """Moment decomposition of g(f) ≈ f·μ − f²σ²/2 + f³·m₃/3 (Taylor of
    E[log(1+fX)]): isolates the SKEWNESS contribution to growth."""
    p = np.asarray(p, float); o = np.asarray(o, float); f = np.asarray(f, float)
    mu = p * o - 1.0
    s2 = p * (1 - p) * o ** 2
    m3 = p * (1 - p) * (1 - 2 * p) * o ** 3
    return {"mean": f * mu, "var": -0.5 * f ** 2 * s2, "skew": (f ** 3) * m3 / 3.0}


def fair_odds(p):
    return 1.0 / np.asarray(p, float)
