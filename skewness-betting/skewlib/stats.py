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


def breakpoints(ser, min_size=20, pen_mult=2.0):
    """Quebras estruturais endógenas na média (PELT, modelo l2)."""
    import ruptures as rpt
    y = np.asarray(ser.dropna())
    algo = rpt.Pelt(model="l2", min_size=min_size).fit(y)
    bkps = algo.predict(pen=np.log(len(y)) * y.var() * pen_mult)
    return [ser.index[b] for b in bkps[:-1]]
