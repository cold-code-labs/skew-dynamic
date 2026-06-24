"""Formal derivation: skewness = f(force dispersion) via ordered-probit.

Goddard-Asimakopoulos (2004) / Koning (2000) template: each team's force
r ~ N(0, σ_L²); in a match the difference d = r_i − r_j ~ N(0, 2σ_L²). The latent
margin y* = d + h + ε (ε~N(0,1), h = home advantage) generates (A,D,H) by cutoffs
±c:
    P(A)=Φ(−c−μ),  P(H)=1−Φ(c−μ),  P(D)=Φ(c−μ)−Φ(−c−μ),   μ = d + h.
The favourite has probability p = max(P_H,P_D,P_A). Under FAIR odds (o=1/p) the
favourite has zero mean, so the league's POOLED skewness is
    S(σ_L) = E[m₃(p)] / E[σ²(p)]^{3/2},  with σ²=(1−p)/p, m₃=(1−p)(1−2p)/p²,
where the expectation is over p = p_fav(d), d ~ N(0, 2σ_L²). σ_L is the competitiveness:
small = balanced.

Front E (hardening the derivation) adds two pieces:
  E1 — closed form: the expectation E[·] is a 1-D Gaussian integral in d, so
       `league_*_exact` evaluates it by QUADRATURE (deterministic, no MC noise),
       and `smallsigma_skew` gives the analytic near-balance expansion
       S(σ_L) = S₀ + S₂·σ_L² + O(σ_L⁴), with S₀ = (1−2p₀)/√(p₀(1−p₀)) the identity
       at the balanced favourite p₀ = p_fav(0). (The curve is NOT monotone: it is concave,
       peaking near balance and crossing 0 when the favourite becomes strong.)
  E2 — force robustness: `force_diff` swaps N(0,σ²) for Student-t / skew-normal /
       uniform. Since d = rᵢ − rⱼ is SYMMETRIC for any iid force, the force's asymmetry
       does not bias the law; only the tail (kurtosis of d) can move it — testable.
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import fsolve
from scipy.integrate import quad


def outcome_probs(d, h, c):
    mu = d + h
    cdf_hi = norm.cdf(c - mu); cdf_lo = norm.cdf(-c - mu)
    return 1 - cdf_hi, cdf_hi - cdf_lo, cdf_lo      # pH, pD, pA


def force_diff(sigma_L, n, seed, family="normal", nu=5.0, alpha=4.0):
    """Force difference d = rᵢ − rⱼ of a match, for several force families
    (Front E2). Each team has force r of variance σ_L²; d has variance 2σ_L².
    `normal` reproduces exactly `np.random.default_rng(seed).normal(0,√2·σ,n)`
    (1 draw) — frozen path, bit-identical to the baseline. The others draw
    two legs (rᵢ, rⱼ) and difference them, so d is symmetric by construction:
      t        — Student-t force (heavy tail), scaled to variance σ_L²;
      skewnormal[_neg] — force with asymmetry ±α (skew-normal), variance σ_L²;
      uniform  — uniform force, variance σ_L².
    """
    rng = np.random.default_rng(seed)
    s = float(sigma_L)
    if family == "normal":
        return rng.normal(0.0, np.sqrt(2.0) * s, n)
    if family == "t":
        scale = s * np.sqrt((nu - 2.0) / nu)          # Var(t_ν)=ν/(ν−2) → σ_L²
        return (rng.standard_t(nu, n) - rng.standard_t(nu, n)) * scale
    if family in ("skewnormal", "skewnormal_neg"):
        from scipy.stats import skewnorm
        a = alpha if family == "skewnormal" else -alpha
        delta = a / np.sqrt(1.0 + a * a)
        omega = s / np.sqrt(1.0 - 2.0 * delta * delta / np.pi)   # Var=σ_L²
        xi = -omega * delta * np.sqrt(2.0 / np.pi)               # mean 0
        r1 = skewnorm.rvs(a, loc=xi, scale=omega, size=n, random_state=rng)
        r2 = skewnorm.rvs(a, loc=xi, scale=omega, size=n, random_state=rng)
        return r1 - r2
    if family == "uniform":
        hw = np.sqrt(3.0) * s                          # Var(U[-hw,hw])=hw²/3=σ_L²
        return rng.uniform(-hw, hw, n) - rng.uniform(-hw, hw, n)
    raise ValueError(f"unknown force family: {family}")


def _d(sigma_L, n, seed, family="normal", **fkw):
    return force_diff(sigma_L, n, seed, family=family, **fkw)


def _pfav(d, h, c):
    pH, pD, pA = outcome_probs(d, h, c)
    return np.clip(np.maximum.reduce([pH, pD, pA]), 1e-6, 1 - 1e-6)


def marginals(sigma_L, h, c, n=200000, seed=1, family="normal", **fkw):
    d = _d(sigma_L, n, seed, family=family, **fkw)
    pH, pD, pA = outcome_probs(d, h, c)
    return {"home": float(pH.mean()), "draw": float(pD.mean()),
            "away": float(pA.mean()), "p_fav": float(_pfav(d, h, c).mean())}


def league_skew(sigma_L, h, c, n=200000, seed=1, family="normal", **fkw):
    """Pooled league skewness under fair odds — closed in p (MC over d)."""
    p = _pfav(_d(sigma_L, n, seed, family=family, **fkw), h, c)
    s2 = (1 - p) / p
    m3 = (1 - p) * (1 - 2 * p) / p ** 2
    return float(m3.mean() / s2.mean() ** 1.5)


def _fair_central_moments(p, max_order=6):
    """Per-match central moments under FAIR odds (o=1/p ⇒ zero mean):
        m_k = (1-p)/p^(k-1) · [ (1-p)^(k-1) + (-1)^k · p^(k-1) ].
    Recovers s²=(1-p)/p and m₃=(1-p)(1-2p)/p² used in `league_skew`."""
    p = np.asarray(p, float)
    return {k: (1 - p) / p ** (k - 1) * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1))
            for k in range(2, max_order + 1)}


# ── Front E1 — closed form: the Gaussian integral, no Monte Carlo ─────────────
# E[g(p_fav(d))] = ∫ g(p_fav(d)) φ(d; 0, 2σ_L²) dd is a 1-D integral. p_fav(d) is
# continuous but has KINKS where the favourite switches (max of pH,pD,pA); we evaluate
# the integral by adaptive quadrature, partitioning at the switch points → exact
# (deterministic) up to tolerance, recovering `league_*` without MC noise.

def _pfav_scalar(d, h, c):
    mu = d + h
    pH = 1.0 - norm.cdf(c - mu); pD = norm.cdf(c - mu) - norm.cdf(-c - mu)
    pA = norm.cdf(-c - mu)
    return min(max(max(pH, pD, pA), 1e-12), 1.0 - 1e-12)


def _fair_mk(p, k):
    """k-th per-match central moment under fair odds (scalar)."""
    return (1 - p) / p ** (k - 1) * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1))


def fav_switch_points(h, c, span=14.0, ngrid=2801):
    """Values of d where the favourite (argmax of pH,pD,pA) switches identity —
    the kinks of p_fav(d). Used as partition nodes in the quadrature."""
    from scipy.optimize import brentq
    g = np.linspace(-span, span, ngrid)
    arg = np.vstack(outcome_probs(g, h, c)).argmax(0)
    pts = []
    for i in np.where(np.diff(arg) != 0)[0]:
        a, b = int(arg[i]), int(arg[i + 1])
        f = lambda d: outcome_probs(d, h, c)[a] - outcome_probs(d, h, c)[b]
        try:
            pts.append(float(brentq(f, g[i], g[i + 1])))
        except ValueError:
            pass
    return sorted(pts)


def mean_pfav_exact(sigma_L, h, c):
    """Exact E[p_fav] (Gaussian integral), no MC — observable competitiveness."""
    tau = np.sqrt(2.0) * float(sigma_L)
    if tau < 1e-9:
        return _pfav_scalar(0.0, h, c)
    pts = [p for p in fav_switch_points(h, c) if abs(p) < 8 * tau]
    val, _ = quad(lambda d: _pfav_scalar(d, h, c) * norm.pdf(d, 0.0, tau),
                  -8 * tau, 8 * tau, points=pts, limit=200)
    return float(val)


def league_moments_exact(sigma_L, h, c, max_order=6):
    """STANDARDISED league moments by QUADRATURE of the Gaussian integral in d —
    exact version (no MC noise) of `league_moments`. Closed form of S(σ_L)
    in the sense of the integral evaluated to machine precision."""
    tau = np.sqrt(2.0) * float(sigma_L)
    if tau < 1e-9:                                   # degenerate league: single p₀
        p0 = _pfav_scalar(0.0, h, c)
        M = {k: _fair_mk(p0, k) for k in range(2, max_order + 1)}
    else:
        pts = [p for p in fav_switch_points(h, c) if abs(p) < 8 * tau]
        def Ek(k):
            v, _ = quad(lambda d: _fair_mk(_pfav_scalar(d, h, c), k)
                        * norm.pdf(d, 0.0, tau), -8 * tau, 8 * tau,
                        points=pts, limit=200)
            return v
        M = {k: Ek(k) for k in range(2, max_order + 1)}
    M2 = M[2]
    res = {"var": M2}
    if max_order >= 3: res["skew"] = M[3] / M2 ** 1.5
    if max_order >= 4: res["exkurt"] = M[4] / M2 ** 2 - 3.0
    if max_order >= 5: res["std5"] = M[5] / M2 ** 2.5
    if max_order >= 6: res["std6"] = M[6] / M2 ** 3
    return res


def league_skew_exact(sigma_L, h, c):
    """Exact league skewness (quadrature). Replaces the MC of `league_skew`."""
    return float(league_moments_exact(sigma_L, h, c, max_order=3)["skew"])


def smallsigma_coeffs(h, c):
    """Coefficients of the analytic near-balance expansion of S(σ_L):
        S(σ_L) = S₀ + S₂·σ_L² + O(σ_L⁴).
    Around σ_L→0, d→0 and p_fav is the smooth branch of the balanced favourite, with
    p₀=p_fav(0), p₁=p_fav'(0), p₂=p_fav''(0). By the Taylor expansion + symmetry
    of d (odd term vanishes), for any g(p):  E[g] = g(p₀) + σ_L²·[g''(p₀)p₁²
    + g'(p₀)p₂] + O(σ_L⁴) (since Var(d)=2σ_L²). Applying to σ²(p)=(1−p)/p and
    m₃(p)=(1−p)(1−2p)/p²:
        S₀ = m₃(p₀)/σ²(p₀)^{3/2} = (1−2p₀)/√(p₀(1−p₀))      (per-match identity)
        S₂ = B₂/A₀^{3/2} − (3/2)·B₀·A₂/A₀^{5/2}.
    On the home branch (favourite = home), p₀=Φ(h−c), p₁=φ(h−c), p₂=−(h−c)φ(h−c)
    in closed form; we use central differences so it holds on any branch."""
    eps = 1e-3
    f = lambda d: _pfav_scalar(d, h, c)
    p0 = f(0.0)
    p1 = (f(eps) - f(-eps)) / (2 * eps)
    p2 = (f(eps) - 2 * p0 + f(-eps)) / eps ** 2
    A0 = (1 - p0) / p0                                   # σ²(p₀)
    A2 = (2 / p0 ** 3) * p1 ** 2 + (-1 / p0 ** 2) * p2   # g=σ²: g''=2/p³, g'=−1/p²
    B0 = (1 - p0) * (1 - 2 * p0) / p0 ** 2               # m₃(p₀)
    m3p = -2 / p0 ** 3 + 3 / p0 ** 2                     # m₃'(p)
    m3pp = 6 / p0 ** 4 - 6 / p0 ** 3                     # m₃''(p)
    B2 = m3pp * p1 ** 2 + m3p * p2
    S0 = B0 / A0 ** 1.5
    S2 = B2 / A0 ** 1.5 - 1.5 * B0 * A2 / A0 ** 2.5
    return {"S0": float(S0), "S2": float(S2), "p0": float(p0),
            "p1": float(p1), "p2": float(p2)}


def smallsigma_skew(sigma_L, h, c):
    """Analytic expansion S₀ + S₂·σ_L² (near-balance closed form)."""
    cf = smallsigma_coeffs(h, c)
    s = np.asarray(sigma_L, float)
    return cf["S0"] + cf["S2"] * s ** 2


def league_moments(sigma_L, h, c, n=200000, seed=1, max_order=6, family="normal", **fkw):
    """STANDARDISED league moments under fair odds — var/skew/kurtosis/etc.
    closed in the distribution of p_fav. Since every bet has zero mean, there is
    no between-match term: M_k = E[m_k(p)]. Generalises `league_skew` (order 3) and
    allows predicting the whole SHAPE (not just the 3rd moment) from σ_L."""
    p = _pfav(_d(sigma_L, n, seed, family=family, **fkw), h, c)
    m = _fair_central_moments(p, max_order)
    M2 = float(m[2].mean())
    res = {"var": M2}
    if max_order >= 3: res["skew"] = float(m[3].mean() / M2 ** 1.5)
    if max_order >= 4: res["exkurt"] = float(m[4].mean() / M2 ** 2 - 3.0)
    if max_order >= 5: res["std5"] = float(m[5].mean() / M2 ** 2.5)
    if max_order >= 6: res["std6"] = float(m[6].mean() / M2 ** 3)
    return res


def calibrate(home=0.444, draw=0.264, pfav=0.499, n=200000):
    """Solves (h, c, σ_ref) to match the observed mean marginal rates."""
    def eqs(x):
        h, c, s = x
        m = marginals(abs(s), h, abs(c), n=n, seed=7)
        return [m["home"] - home, m["draw"] - draw, m["p_fav"] - pfav]
    h, c, s = fsolve(eqs, [0.2, 0.5, 0.4])
    return {"h": float(h), "c": float(abs(c)), "sigma_ref": float(abs(s))}


def calibrate_by_league(df, n=120000, min_n=3000):
    """Calibrates (h, c, σ_L) PER league from the league's own marginal rates
    (Front E3): home advantage, draw cutoff and force dispersion all endogenous.
    Requires add_exante (p_fav_dv). Returns a per-league DataFrame + skew predicted by
    the league's own model vs observed."""
    import pandas as pd
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_n:
            continue
        home = float((g.FTResult == "H").mean())
        draw = float((g.FTResult == "D").mean())
        pfav = float(g.p_fav_dv.mean())
        try:
            par = calibrate(home=home, draw=draw, pfav=pfav, n=n)
        except Exception:
            continue
        sk_model = league_skew(par["sigma_ref"], par["h"], par["c"], n=n, seed=5)
        rows.append({"Division": lg, "n": len(g), "home": home, "draw": draw,
                     "p_fav": pfav, "h": par["h"], "c": par["c"],
                     "sigma_L": par["sigma_ref"], "skew_model": sk_model})
    return pd.DataFrame(rows)


def curve(h, c, sigmas, n=200000, seed=3):
    """Traces (mean p_fav, skewness) over a grid of σ_L."""
    pf, sk = [], []
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        sk.append(league_skew(s, h, c, n=n, seed=seed))
    return np.array(pf), np.array(sk)


def curve_exact(h, c, sigmas):
    """EXACT (mean p_fav, skewness) by quadrature over the σ_L grid —
    the theoretical curve without MC noise (Front E1). Replaces `curve` for the figure."""
    pf = np.array([mean_pfav_exact(s, h, c) for s in sigmas])
    sk = np.array([league_skew_exact(s, h, c) for s in sigmas])
    return pf, sk


def curve_family(h, c, sigmas, family="normal", n=200000, seed=3, **fkw):
    """(mean p_fav, skewness) per force family (Front E2) — MC, since t/
    skew-normal/uniform lack the closed integral of the Gaussian case. Allows
    reparametrising the law by the OBSERVABLE competitiveness (p_fav) and checking
    whether the skew×p_fav curve survives swapping the force distribution."""
    pf, sk = [], []
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed, family=family, **fkw)["p_fav"])
        sk.append(league_skew(s, h, c, n=n, seed=seed, family=family, **fkw))
    return np.array(pf), np.array(sk)


def curve_moments(h, c, sigmas, n=200000, seed=3, max_order=6):
    """Traces (mean p_fav, {var, skew, exkurt, ...}) over the σ_L grid —
    the theoretical curve of EACH moment, to predict each league's shape from p_fav."""
    keys = ["var", "skew", "exkurt", "std5", "std6"][: max_order - 1]
    pf = []; mom = {k: [] for k in keys}
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        lm = league_moments(s, h, c, n=n, seed=seed, max_order=max_order)
        for k in keys:
            mom[k].append(lm[k])
    return np.array(pf), {k: np.array(v) for k, v in mom.items()}
