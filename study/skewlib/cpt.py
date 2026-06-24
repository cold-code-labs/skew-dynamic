"""Cumulative Prospect Theory: the probability weighting behind the FLB
(Front C2). The favourite–longshot bias is the signature of **probability
weighting**: bettors overweight small probabilities (longshots) and underweight
large ones (favourites). We model the de-vigged implied prob `q` as the
**decision weight** of the objective prob `π`:  q ≈ w(π), with the
Tversky-Kahneman (1992) function
    w(p) = p^γ / (p^γ + (1−p)^γ)^{1/γ},     γ<1 ⇒ inverse-S (longshot overweight),
or Prelec (1998) as an alternative. γ is a PREFERENCE parameter. The C2 thesis: it
is, itself, an INVARIANT — stable across leagues and over time (like skewness).

Caveat: the reduced form ignores the per-game de-vig renormalisation (Σq=1, but
Σw≠1); γ is the reduced calibration curve, not a pure structural CPT estimator —
but it is the standard object of the FLB literature (Snowberg-Wolfers 2010;
Jullien-Salanié 2000).
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar


def w_tk(p, gamma):
    """Tversky-Kahneman probability weighting."""
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return p ** gamma / (p ** gamma + (1 - p) ** gamma) ** (1.0 / gamma)


def w_prelec(p, alpha, beta=1.0):
    """Prelec weighting (curvature α, elevation β)."""
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return np.exp(-beta * (-np.log(p)) ** alpha)


def implied_proportional(df, ocols=("OddHome", "OddDraw", "OddAway")):
    """Implied prob by PROPORTIONAL (multiplicative) de-vig: q_k = (1/o_k)/Σ(1/o_j).
    Removes the margin proportionally, but PRESERVES the favourite–longshot bias
    (does not model it like Shin) — it is the right object to reveal the probability
    weighting."""
    O = df[list(ocols)].to_numpy(float)
    inv = 1.0 / O
    return inv / inv.sum(axis=1, keepdims=True)


def calibration(df, nbins=25, legs=("H", "D", "A")):
    """Reliability diagram over the 3 legs (covers [0,1]: longshot→favourite):
    PROPORTIONAL implied prob `q` vs objective hit rate `π`, binned by `q`.
    Uses the proportional implied prob (not the Shin de-vigged one) so as not to
    erase the FLB being measured."""
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
    """Fits TK's γ by weighted least squares: q ≈ w_tk(π, γ)."""
    pi, q, wts = cal.pi.values, cal.q.values, cal.n.values
    r = minimize_scalar(lambda g: float(np.sum(wts * (q - w_tk(pi, g)) ** 2)),
                        bounds=bounds, method="bounded")
    return float(r.x)


def gamma_by(df, col, min_n=4000, nbins=15):
    """γ fitted per group (league or season) — to test invariance."""
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
