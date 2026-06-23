"""De-vigging: converte odds 1X2 em probabilidades implícitas (sem overround).

Métodos (todos devolvem probabilidades que somam 1):
  multiplicative  p_i = (1/o_i) / Σ(1/o_j)              — proporcional, baseline
  shin            modelo de Shin (1993); z = fração de
                  dinheiro informado — método primário do estudo
  power           p_i = (1/o_i)^k, k tal que Σ p = 1     — robustez

A odd implícita crua é r_i = 1/o_i; o booksum M = Σ r_i é o overround (>1 com
vig). O favorito é sempre argmax(p) = argmin(o), invariante ao método (todos
são monotônicos em r). Para o Shin, `shin_z` ≈ proporção de dinheiro informado
e é um subproduto útil para a decomposição da margem.
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
    """p_i = r_i^k com k>1 tal que Σ p = 1 (raiz única quando há overround)."""
    r = _inv(odds)
    if r.sum() <= 1.0:                       # sem vig (ex.: odds máximas)
        return r / r.sum()
    k = brentq(lambda k: (r ** k).sum() - 1.0, 1.0, 50.0)
    return r ** k


def _shin_p(r, bsum, z):
    return (np.sqrt(z * z + 4 * (1 - z) * r * r / bsum) - z) / (2 * (1 - z))


def shin(odds):
    """Devolve (probabilidades, z). z = proporção estimada de dinheiro informado."""
    r = _inv(odds); bsum = r.sum()
    if bsum <= 1.0:
        return r / bsum, 0.0
    z = brentq(lambda z: _shin_p(r, bsum, z).sum() - 1.0, 1e-9, 0.5)
    return _shin_p(r, bsum, z), z


METHODS = {"multiplicative": multiplicative,
           "power": power,
           "shin": lambda o: shin(o)[0]}


def _shin_z_vec(r, bsum, iters=80):
    """Resolve o z do Shin para todas as linhas em paralelo (bisseção vetorizada).

    g(z)=Σ p(z) − 1 é decrescente em z; g(0⁺)=√bsum−1>0 quando há vig.
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
    """De-vig genérico para uma MATRIZ de odds (n_eventos, k_resultados) com k
    arbitrário — a versão sport-agnóstica de `devig_frame`. Mesma matemática
    (Shin vetorizado / multiplicative / power); devolve P (n_eventos, k) somando 1
    por linha. Usado pela camada canônica (mercados de 2, 3, … resultados)."""
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
    raise ValueError(f"método de-vig desconhecido: {method}")


def devig_frame(df, method=None, cols=("OddHome", "OddDraw", "OddAway")):
    """Adiciona p_H, p_D, p_A de-vigadas + `overround` (e `shin_z` no Shin)."""
    method = method or C.DEVIG_METHOD
    O = df[list(cols)].to_numpy(float)
    r = 1.0 / O
    bsum = r.sum(axis=1)
    out = df.copy()
    out["overround"] = bsum

    if method == "shin":
        z = np.zeros(len(r))
        vig = bsum > 1.0                                   # só resolve onde há vig
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
        raise ValueError(f"método de-vig desconhecido: {method}")

    out["p_H"], out["p_D"], out["p_A"] = P[:, 0], P[:, 1], P[:, 2]
    return out
