"""Frente K — diversificação / portfólio. A skewness é um fenômeno de aposta ÚNICA?
Para N apostas (quase) independentes, o retorno MÉDIO tem skewness padronizada
skew(X)/√N (soma de iid) — uma banca diversificada tende ao gaussiano, enquanto a
aposta isolada é fortemente assimétrica. Implicação: a preferência por skewness (o
FLB) morde o apostador RECREATIVO (poucas apostas concentradas), não o sindicato
diversificado — o canal que sustenta o viés.
"""
import numpy as np
from scipy.stats import skew, kurtosis


def skew_decay(returns, sizes, B=4000, seed=42):
    """Skewness do retorno médio de N apostas, por bootstrap de carteiras de
    tamanho N, vs a previsão iid skew(X)/√N."""
    r = np.asarray(returns, float)
    r = r[np.isfinite(r)]
    base = float(skew(r))
    rng = np.random.default_rng(seed)
    rows = []
    for N in sizes:
        means = r[rng.integers(0, len(r), size=(B, N))].mean(axis=1)
        rows.append({"N": int(N), "skew": float(skew(means)),
                     "skew_pred": base / np.sqrt(N),
                     "exkurt": float(kurtosis(means)), "std": float(means.std())})
    return base, rows


def n_to_gaussian(base_skew, thresh=0.1):
    """Quantas apostas para a skewness cair abaixo de `thresh` (≈ gaussiano)."""
    return int(np.ceil((abs(base_skew) / thresh) ** 2))
