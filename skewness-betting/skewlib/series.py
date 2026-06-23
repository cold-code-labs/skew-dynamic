"""Série temporal deslizante de skewness + bootstrap do erro-padrão."""
import numpy as np, pandas as pd
from scipy.stats import skew
from . import config as C


def rolling_skew(df, col="ret_fav", window=None, step=None, overlap=True):
    """Skewness numa janela deslizante de `window` jogos.

    overlap=False usa janelas disjuntas (step=window) — recomendado para
    inferência, pois a sobreposição induz autocorrelação artificial.
    """
    window = window or C.WINDOW
    step = (step or C.STEP) if overlap else window
    s = df[col].dropna().reset_index(drop=True)
    dts = df.loc[df[col].notna(), "date"].reset_index(drop=True)
    vals, idx = [], []
    for i in range(0, len(s) - window, step):
        vals.append(skew(s.iloc[i:i + window]))
        idx.append(dts.iloc[i + window // 2])
    return pd.Series(vals, index=pd.DatetimeIndex(idx), name=col)


def bootstrap_se(x, B=None, seed=None):
    """Erro-padrão da skewness por bootstrap (skewness é momento de 3ª ordem)."""
    B = B or C.BOOT_B
    rng = np.random.default_rng(seed or C.SEED)
    x = np.asarray(x); n = len(x)
    return float(np.std([skew(x[rng.integers(0, n, n)]) for _ in range(B)]))
