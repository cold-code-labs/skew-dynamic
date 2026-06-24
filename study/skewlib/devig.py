"""De-vigging: converts 1X2 odds into implied probabilities (without overround).

Methods (all return probabilities that sum to 1):
  multiplicative  p_i = (1/o_i) / Σ(1/o_j)              — proportional, baseline
  shin            Shin (1993) model; z = fraction of
                  informed money — the study's primary method
  power           p_i = (1/o_i)^k, k such that Σ p = 1   — robustness

The raw implied odd is r_i = 1/o_i; the booksum M = Σ r_i is the overround (>1 with
vig). The favourite is always argmax(p) = argmin(o), invariant to the method (all
are monotonic in r). For Shin, `shin_z` ≈ proportion of informed money and is a
useful by-product for the margin decomposition.
"""
import numpy as np
from scipy.optimize import brentq
from . import config as C


def _inv(odds):
    return 1.0 / np.asarray(odds, dtype=float)


def multiplicative(odds):
    r = _inv(odds)
    return r / r.sum()


def power(odds):
    """p_i = r_i^k with k>1 such that Σ p = 1 (unique root when there is overround)."""
    r = _inv(odds)
    if r.sum() <= 1.0:                       # no vig (e.g.: maximum odds)
        return r / r.sum()
    k = brentq(lambda k: (r ** k).sum() - 1.0, 1.0, 50.0)
    return r ** k


def _shin_p(r, bsum, z):
    return (np.sqrt(z * z + 4 * (1 - z) * r * r / bsum) - z) / (2 * (1 - z))


def shin(odds):
    """Returns (probabilities, z). z = estimated proportion of informed money."""
    r = _inv(odds); bsum = r.sum()
    if bsum <= 1.0:
        return r / bsum, 0.0
    z = brentq(lambda z: _shin_p(r, bsum, z).sum() - 1.0, 1e-9, 0.5)
    return _shin_p(r, bsum, z), z


METHODS = {"multiplicative": multiplicative,
           "power": power,
           "shin": lambda o: shin(o)[0]}


def _shin_z_vec(r, bsum, iters=80):
    """Solves Shin's z for all rows in parallel (vectorised bisection).

    g(z)=Σ p(z) − 1 is decreasing in z; g(0⁺)=√bsum−1>0 when there is vig.
    """
    lo = np.full(len(r), 1e-9)
    hi = np.full(len(r), 0.5)
    bs = bsum[:, None]
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        zc = mid[:, None]
        g = ((np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bs) - zc) / (2 * (1 - zc))).sum(1) - 1.0
        pos = g > 0
        lo = np.where(pos, mid, lo)
        hi = np.where(pos, hi, mid)
    return 0.5 * (lo + hi)


def devig_odds(O, method=None):
    """Generic de-vig for a MATRIX of odds (n_events, k_outcomes) with arbitrary
    k — the sport-agnostic version of `devig_frame`. Same maths
    (vectorised Shin / multiplicative / power); returns P (n_events, k) summing to 1
    per row. Used by the canonical layer (markets of 2, 3, … outcomes)."""
    method = method or C.DEVIG_METHOD
    O = np.asarray(O, float)
    r = 1.0 / O
    bsum = r.sum(axis=1)
    if method == "shin":
        z = np.zeros(len(r))
        vig = bsum > 1.0
        if vig.any():
            z[vig] = _shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        return np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
    if method == "multiplicative":
        return r / bsum[:, None]
    if method == "power":
        return np.array([power(row) for row in O])
    raise ValueError(f"unknown de-vig method: {method}")


def devig_frame(df, method=None, cols=("OddHome", "OddDraw", "OddAway")):
    """Adds de-vigged p_H, p_D, p_A + `overround` (and `shin_z` for Shin)."""
    method = method or C.DEVIG_METHOD
    O = df[list(cols)].to_numpy(float)
    r = 1.0 / O
    bsum = r.sum(axis=1)
    out = df.copy()
    out["overround"] = bsum

    if method == "shin":
        z = np.zeros(len(r))
        vig = bsum > 1.0                                   # only solve where there is vig
        if vig.any():
            z[vig] = _shin_z_vec(r[vig], bsum[vig])
        zc = z[:, None]
        P = (np.sqrt(zc * zc + 4 * (1 - zc) * r * r / bsum[:, None]) - zc) / (2 * (1 - zc))
        P = np.where(bsum[:, None] > 1.0, P, r / bsum[:, None])
        out["shin_z"] = z
    elif method == "multiplicative":
        P = r / bsum[:, None]
    elif method == "power":
        P = np.array([power(row) for row in O])
    else:
        raise ValueError(f"unknown de-vig method: {method}")

    out["p_H"], out["p_D"], out["p_A"] = P[:, 0], P[:, 1], P[:, 2]
    return out
