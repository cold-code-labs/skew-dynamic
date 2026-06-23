"""Bateria de testes: estacionariedade, persistência, i.i.d., quebras."""
import numpy as np, warnings
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
warnings.filterwarnings("ignore")


def stationarity(ser):
    """ADF (H0: raiz unitária) + KPSS (H0: estacionária). Confirmação dupla."""
    s = ser.dropna()
    return {"adf_p": adfuller(s)[1],
            "kpss_p": kpss(s, regression="c", nlags="auto")[1]}


def persistence(ser, lags=20):
    """Ljung-Box (H0: ruído branco) + ACF de lag 1."""
    s = ser.dropna()
    lb = float(acorr_ljungbox(s, lags=[lags], return_df=True)["lb_pvalue"].iloc[0])
    return {"ljungbox_p": lb, "acf1": float(acf(s, nlags=1)[1])}


def variance_ratio(ser, ks=(2, 4, 8)):
    """VR(k)≈1 indica i.i.d.; <1 reversão à média; >1 momentum."""
    x = np.asarray(ser.dropna()); v1 = x.var(); n = len(x)
    out = {}
    for k in ks:
        xk = np.array([x[i:i + k].sum() for i in range(n - k + 1)])
        out[k] = (xk.var() / k) / v1
    return out


def ar1(ser):
    """Ajusta AR(1); retorna phi, p-valor e half-life da reversão."""
    m = ARIMA(np.asarray(ser.dropna()), order=(1, 0, 0)).fit()
    phi = float(m.arparams[0])
    hl = float(np.log(0.5) / np.log(abs(phi))) if 0 < abs(phi) < 1 else float("inf")
    return {"phi": phi, "phi_p": float(m.pvalues[1]), "half_life": hl}


def bootstrap_corr(x, y, B=5000, seed=42):
    """Pearson r + IC bootstrap (reamostra pares). Para n pequeno (ligas)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    rng = np.random.default_rng(seed); n = len(x)
    r = float(np.corrcoef(x, y)[0, 1])
    cs = [np.corrcoef(x[i], y[i])[0, 1]
          for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = np.percentile(cs, [2.5, 97.5])
    return {"r": r, "ci_lo": float(lo), "ci_hi": float(hi)}


def bootstrap_stat(fn, n, B=2000, seed=42):
    """SE bootstrap de uma estatística `fn(idx)` que recebe índices reamostrados
    (com reposição) de 0..n-1. Para momentos de ordem alta (skew/kurtose), em que
    a normalidade do estimador não vale."""
    rng = np.random.default_rng(seed)
    vals = [fn(rng.integers(0, n, n)) for _ in range(B)]
    return {"se": float(np.std(vals)),
            "ci_lo": float(np.percentile(vals, 2.5)),
            "ci_hi": float(np.percentile(vals, 97.5))}


def ols(y, x):
    """Regressão simples y~x: slope, intercepto, R², r. (1 regressor)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    b, a = np.polyfit(x, y, 1)
    yhat = a + b * x
    ss = ((y - yhat) ** 2).sum(); st = ((y - y.mean()) ** 2).sum()
    return {"slope": float(b), "intercept": float(a),
            "r2": float(1 - ss / st), "r": float(np.corrcoef(x, y)[0, 1])}


def breakpoints(ser, min_size=20, pen_mult=2.0):
    """Quebras estruturais endógenas na média (PELT, modelo l2)."""
    import ruptures as rpt
    y = np.asarray(ser.dropna())
    algo = rpt.Pelt(model="l2", min_size=min_size).fit(y)
    bkps = algo.predict(pen=np.log(len(y)) * y.var() * pen_mult)
    return [ser.index[b] for b in bkps[:-1]]
