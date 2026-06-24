"""Distribution collapse (data collapse, statistical-physics style).

The "shape invariance" thesis (B): controlling for competitiveness, the ENTIRE
shape of the implied distribution is the same across leagues — not just the 3rd
moment. Two complementary tests:

  1. `pairwise_test` over per-league z-scored returns — is the shape universal
     WITHOUT controlling for competitiveness? Expected to REJECT (the skew varies
     with the league, which is precisely the finding): the shape is not globally
     universal, it is a function of competitiveness.
  2. `conditional_invariance` — the STRONG test: conditional on the p_fav band
     (competitiveness), is the return distribution league-invariant? If so, the
     league identity adds nothing beyond competitiveness → collapse.

Caveat: the favourite's return is discrete (two points per game), so the KS
operates over a discrete mixture; `ks_2samp` handles ties approximately. The
p-values are indicative; the metric of interest is the FRACTION of pairs that reject.
"""
import numpy as np, pandas as pd, warnings
from scipy.stats import ks_2samp, anderson_ksamp


def zscore_returns(df, col="ret_fav", by="Division", min_n=2000):
    """Standardised returns (z-score: removes location and scale) per group.
    Returns dict group -> array. Standardising isolates the SHAPE (skew/kurtosis)."""
    out = {}
    for k, g in df.groupby(by):
        x = g[col].dropna().values
        if len(x) < min_n or x.std() == 0:
            continue
        out[k] = (x - x.mean()) / x.std()
    return out


def pairwise_test(samples, test="ks", alpha=0.05):
    """KS (or Anderson-Darling) 2-sample pairwise between already-standardised groups.
    With large n the p-value saturates (rejects everything) → we also report the
    median KS STATISTIC (maximum CDF distance = effect size), which is what matters.
    Returns dict {pmatrix, reject_frac, median_p, median_stat}."""
    keys = list(samples)
    P = pd.DataFrame(np.eye(len(keys)), index=keys, columns=keys, dtype=float)
    pv, stat = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = samples[keys[i]], samples[keys[j]]
                if test == "ks":
                    r = ks_2samp(a, b); p, s = float(r.pvalue), float(r.statistic)
                else:  # anderson-darling k-sample (k=2)
                    ad = anderson_ksamp([a, b])
                    p, s = float(np.clip(ad.significance_level, 0, 1)), float(ad.statistic)
                P.iloc[i, j] = P.iloc[j, i] = p
                pv.append(p); stat.append(s)
    pv = np.array(pv)
    return {"pmatrix": P, "reject_frac": float((pv < alpha).mean()),
            "median_p": float(np.median(pv)), "median_stat": float(np.median(stat))}


def conditional_invariance(df, pcol="p_fav_dv", retcol="ret_fav", by="Division",
                           nbins=8, min_n=300, alpha=0.05):
    """STRONG collapse test: conditional on the p_fav band, is the return
    distribution the same across leagues? In each p-quantile bin, compares each
    league (with ≥min_n games in the bin) against the REST of the bin (one-vs-rest
    KS). If the shape is a function of competitiveness only, the fraction that
    rejects within the bin is low.

    Returns (table per (bin,league), summary per bin). The summary gives the
    fraction of leagues that reject the 'same shape as the rest' in each
    competitiveness band.
    """
    d = df[[pcol, retcol, by]].dropna().copy()
    d["pbin"] = pd.qcut(d[pcol], nbins, duplicates="drop")
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for b, gb in d.groupby("pbin", observed=True):
            for lg, gl in gb.groupby(by, observed=True):
                if len(gl) < min_n:
                    continue
                rest = gb[gb[by] != lg][retcol].values
                if len(rest) < min_n:
                    continue
                ks = ks_2samp(gl[retcol].values, rest)
                rows.append({"pbin": str(b), "p_mid": float(gb[pcol].median()),
                             by: lg, "n": len(gl), "ks_stat": float(ks.statistic),
                             "ks_p": float(ks.pvalue), "reject": ks.pvalue < alpha})
    tab = pd.DataFrame(rows)
    if tab.empty:
        return tab, pd.DataFrame()
    summ = (tab.groupby("pbin", observed=True)
               .agg(p_mid=("p_mid", "first"), n_leagues=("reject", "size"),
                    reject_frac=("reject", "mean"), ks_stat_med=("ks_stat", "median"))
               .reset_index().sort_values("p_mid"))
    return tab, summ


def ecdf(x):
    """ECDF (sorted xs, F) to overlay curves on the collapse plot."""
    xs = np.sort(np.asarray(x, float))
    return xs, np.arange(1, len(xs) + 1) / len(xs)
