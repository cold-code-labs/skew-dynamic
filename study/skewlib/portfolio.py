"""Front K — diversification / portfolio. Is skewness a SINGLE-bet phenomenon?
For N (nearly) independent bets, the MEAN return has standardised skewness
skew(X)/√N (sum of iid) — a diversified bankroll tends to Gaussian, while the
isolated bet is strongly asymmetric. Implication: the preference for skewness (the
FLB) bites the RECREATIONAL bettor (few concentrated bets), not the diversified
syndicate — the channel that sustains the bias.
"""
import numpy as np
from scipy.stats import skew, kurtosis


def skew_decay(returns, sizes, B=4000, seed=42):
    """Skewness of the mean return of N bets, by bootstrap of portfolios of
    size N, vs the iid prediction skew(X)/√N."""
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
    """How many bets for the skewness to fall below `thresh` (≈ Gaussian)."""
    return int(np.ceil((abs(base_skew) / thresh) ** 2))
