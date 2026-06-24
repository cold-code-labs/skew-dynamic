"""Test battery: stationarity, persistence, i.i.d., breaks."""
import numpy as np, warnings
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
warnings.filterwarnings("ignore")


def stationarity(ser):
    """ADF (H0: unit root) + KPSS (H0: stationary). Double confirmation."""
    s = ser.dropna()
    return {"adf_p": adfuller(s)[1],
            "kpss_p": kpss(s, regression="c", nlags="auto")[1]}


def persistence(ser, lags=20):
    """Ljung-Box (H0: white noise) + lag-1 ACF."""
    s = ser.dropna()
    lb = float(acorr_ljungbox(s, lags=[lags], return_df=True)["lb_pvalue"].iloc[0])
    return {"ljungbox_p": lb, "acf1": float(acf(s, nlags=1)[1])}


def variance_ratio(ser, ks=(2, 4, 8)):
    """VR(k)≈1 indicates i.i.d.; <1 mean reversion; >1 momentum."""
    x = np.asarray(ser.dropna()); v1 = x.var(); n = len(x)
    out = {}
    for k in ks:
        xk = np.array([x[i:i + k].sum() for i in range(n - k + 1)])
        out[k] = (xk.var() / k) / v1
    return out


def ar1(ser):
    """Fits AR(1); returns phi, p-value and the reversion half-life."""
    m = ARIMA(np.asarray(ser.dropna()), order=(1, 0, 0)).fit()
    phi = float(m.arparams[0])
    hl = float(np.log(0.5) / np.log(abs(phi))) if 0 < abs(phi) < 1 else float("inf")
    return {"phi": phi, "phi_p": float(m.pvalues[1]), "half_life": hl}


def bootstrap_corr(x, y, B=5000, seed=42):
    """Pearson r + bootstrap CI (resamples pairs). For small n (leagues)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    rng = np.random.default_rng(seed); n = len(x)
    r = float(np.corrcoef(x, y)[0, 1])
    cs = [np.corrcoef(x[i], y[i])[0, 1]
          for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = np.percentile(cs, [2.5, 97.5])
    return {"r": r, "ci_lo": float(lo), "ci_hi": float(hi)}


def bootstrap_stat(fn, n, B=2000, seed=42):
    """Bootstrap SE of a statistic `fn(idx)` that takes resampled indices
    (with replacement) from 0..n-1. For high-order moments (skew/kurtosis), where
    the estimator's normality does not hold."""
    rng = np.random.default_rng(seed)
    vals = [fn(rng.integers(0, n, n)) for _ in range(B)]
    return {"se": float(np.std(vals)),
            "ci_lo": float(np.percentile(vals, 2.5)),
            "ci_hi": float(np.percentile(vals, 97.5))}


def ols(y, x):
    """Simple regression y~x: slope, intercept, R², r. (1 regressor)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    b, a = np.polyfit(x, y, 1)
    yhat = a + b * x
    ss = ((y - yhat) ** 2).sum(); st = ((y - y.mean()) ** 2).sum()
    return {"slope": float(b), "intercept": float(a),
            "r2": float(1 - ss / st), "r": float(np.corrcoef(x, y)[0, 1])}


def tost(beta, se, delta, dof=None):
    """EQUIVALENCE test (TOST: two one-sided tests). H0 (non-equivalence):
    |β| ≥ delta. Two one-sided tests — H0a: β ≤ −delta and H0b: β ≥ +delta — and
    equivalence is declared only if BOTH are rejected (p_tost = max of the two <
    α). This is POSITIVE evidence that β lies within (−delta,+delta), unlike the
    mere non-rejection of β=0 (absence of evidence). The 90% CI
    (= 1−2α for α=.05) lying within [−delta,+delta] is the equivalent criterion.

    `dof` uses the Student-t (small samples); default normal. Reuses the same SE
    of the estimator (analytic cluster-robust or bootstrap)."""
    from scipy import stats as _st
    se = float(se)
    t_lo = (beta + delta) / se                 # H0a: β ≤ −delta (upper tail)
    t_hi = (beta - delta) / se                 # H0b: β ≥ +delta (lower tail)
    if dof:
        p_lo, p_hi, q = _st.t.sf(t_lo, dof), _st.t.cdf(t_hi, dof), _st.t.ppf(0.95, dof)
    else:
        p_lo, p_hi, q = _st.norm.sf(t_lo), _st.norm.cdf(t_hi), _st.norm.ppf(0.95)
    p = max(float(p_lo), float(p_hi))
    return {"beta": float(beta), "se": se, "delta": float(delta),
            "p_lower": float(p_lo), "p_upper": float(p_hi), "p_tost": p,
            "ci90_lo": float(beta - q * se), "ci90_hi": float(beta + q * se),
            "equivalent": bool(p < 0.05)}


def breakpoints(ser, min_size=20, pen_mult=2.0):
    """Endogenous structural breaks in the mean (PELT, l2 model)."""
    import ruptures as rpt
    y = np.asarray(ser.dropna())
    algo = rpt.Pelt(model="l2", min_size=min_size).fit(y)
    bkps = algo.predict(pen=np.log(len(y)) * y.var() * pen_mult)
    return [ser.index[b] for b in bkps[:-1]]
