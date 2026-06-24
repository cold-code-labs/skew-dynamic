"""Front G — adversarial robustness (pre-submission). Three attacks on the finding:

  G1  is the de-vig reliable and stable? Reliability diagram + Brier decomposition
      (Murphy) of the favourite per league/year; and skewness is invariant to the
      de-vig METHOD and to the bookmaker (average Odd vs Max best price, +
      multi-book consensus).
  G2  strict BALANCED panel: rebuilds the GLOBAL series using only leagues present
      in ALL years — kills 100% of the composition confound (P1 did it per-league).
  G3  block-bootstrap over SEASONS (resamples whole years, respecting the
      intra-year dependence) → honest CI for all the headline numbers.
"""
import numpy as np, pandas as pd
from . import exante, devig

OUTCOMES = np.array(["H", "D", "A"])


# ── G1 — de-vig reliability ──────────────────────────────────────────────────
def fav_won(df):
    """1.0 if the favourite (argmax de-vigged p) won the game, 0.0 otherwise."""
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    j = P.argmax(1)
    return (OUTCOMES[j] == df["FTResult"].to_numpy()).astype(float)


def reliability(p, y, nbins=12, min_bin=40):
    """Reliability diagram: mean predicted prob vs observed frequency."""
    p = np.asarray(p, float); y = np.asarray(y, float)
    edges = np.linspace(p.min(), p.max(), nbins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, nbins - 1)
    rows = []
    for b in range(nbins):
        m = idx == b
        if m.sum() < min_bin:
            continue
        rows.append({"p_pred": float(p[m].mean()), "freq_obs": float(y[m].mean()),
                     "n": int(m.sum())})
    return pd.DataFrame(rows)


def brier_decomp(p, y, nbins=12):
    """Murphy decomposition of the Brier score: BS = REL − RES + UNC.
    REL = calibration error (↓ better); RES = resolution; UNC = base uncertainty."""
    p = np.asarray(p, float); y = np.asarray(y, float)
    N = len(y); obar = y.mean()
    edges = np.linspace(p.min(), p.max(), nbins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, nbins - 1)
    rel = res = 0.0
    for b in range(nbins):
        m = idx == b; nk = int(m.sum())
        if nk == 0:
            continue
        fk = p[m].mean(); ok = y[m].mean()
        rel += nk * (fk - ok) ** 2
        res += nk * (ok - obar) ** 2
    rel /= N; res /= N; unc = obar * (1 - obar)
    return {"brier": float(np.mean((p - y) ** 2)), "rel": float(rel),
            "res": float(res), "unc": float(unc), "obar": float(obar)}


def reliability_by(df, col, min_n=3000, nbins=10):
    """REL (calibration error) of the favourite per group (league or year). Stable
    and small ⇒ the Shin de-vig is reliable in a homogeneous way."""
    rows = []
    for key, g in df.groupby(col):
        if len(g) < min_n:
            continue
        d = brier_decomp(g.p_fav_dv.values, fav_won(g), nbins=nbins)
        rows.append({col: key, "n": len(g), "rel": d["rel"], "res": d["res"],
                     "brier": d["brier"]})
    return pd.DataFrame(rows)


def skew_by_devig(df):
    """Pooled skewness of the favourite under various de-vigs and bookmakers
    (multi-book consensus = average of the de-vigged probs of Odd and Max).
    Invariance ⇒ the finding depends on neither the method nor the bookmaker."""
    odd = ("OddHome", "OddDraw", "OddAway")
    mx = ("MaxHome", "MaxDraw", "MaxAway")
    out = {}
    # Max* (best price) has missing/invalid values — restrict to the clean and
    # COMMON sample to compare like with like (same rows in all methods).
    has_max = all(c in df for c in mx)
    base = df
    if has_max:
        ok = df[list(mx)].notna().all(1) & (df[list(mx)] > 1.01).all(1)
        base = df[ok]
    for name, cols, meth in [("shin·odd", odd, "shin"), ("shin·max", mx, "shin"),
                             ("mult·odd", odd, "multiplicative"),
                             ("power·odd", odd, "power")]:
        if not all(c in base for c in cols):
            continue
        _, _, d = exante.market_skew(base, cols, method=meth)
        out[name] = d["skew"]
    # multi-book consensus: average of the de-vigged probabilities (Shin) of the 2 books
    if has_max and len(base):
        po = devig.devig_frame(base, method="shin", cols=odd)[["p_H", "p_D", "p_A"]].to_numpy()
        pm = devig.devig_frame(base, method="shin", cols=mx)[["p_H", "p_D", "p_A"]].to_numpy()
        pc = 0.5 * (po + pm); pc = pc / pc.sum(1, keepdims=True)
        j = pc.argmax(1); i = np.arange(len(pc))
        oc = 1.0 / pc[i, j]                       # fair odd of the consensus
        out["consenso"] = exante.pooled_skew(pc[i, j], oc)["skew"]
    return out


# ── G2 — strict balanced panel ───────────────────────────────────────────────
def balanced_leagues(panel, min_frac=1.0):
    """Leagues present in ≥ min_frac of the panel's seasons (1.0 = all)."""
    nseasons = panel.season.nunique()
    cnt = panel.groupby("Division").season.nunique()
    return list(cnt[cnt >= np.ceil(min_frac * nseasons)].index)


def global_series_balanced(df, leagues):
    """GLOBAL ex-ante skewness series per year, restricted to the balanced leagues."""
    d = df[df.Division.isin(leagues)].copy()
    d["season"] = d.date.dt.year
    rows = []
    for yr, g in d.groupby("season"):
        rows.append({"season": int(yr), "n": len(g),
                     "skew_exante": exante.pooled_skew(g.p_fav_dv.values,
                                                       g.o_fav.values)["skew"]})
    return pd.DataFrame(rows).sort_values("season").reset_index(drop=True)


# ── G3 — block-bootstrap over seasons ─────────────────────────────────────────
def season_block_bootstrap(df, stat_fn, B=400, seed=42):
    """CI of `stat_fn(boot_df)` resampling whole SEASONS with replacement
    (preserves the intra-year dependence that resampling games would break)."""
    d = df.copy()
    d["season"] = d.date.dt.year
    seasons = sorted(d.season.unique())
    groups = {s: d[d.season == s] for s in seasons}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        pick = rng.choice(seasons, len(seasons), replace=True)
        vals.append(stat_fn(pd.concat([groups[s] for s in pick], ignore_index=True)))
    vals = np.array([v for v in vals if v == v])      # discard NaN
    return {"mean": float(vals.mean()), "ci_lo": float(np.percentile(vals, 2.5)),
            "ci_hi": float(np.percentile(vals, 97.5)), "se": float(vals.std())}


def stat_global_skew(d):
    return exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)["skew"]


def stat_league_corr(d, min_n=1500):
    """corr(skew_league, p_fav_league) across leagues — the cross-sectional structural law."""
    rows = []
    for lg, g in d.groupby("Division"):
        if len(g) < min_n:
            continue
        rows.append((exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                     float(g.p_fav_dv.mean())))
    if len(rows) < 5:
        return float("nan")
    a = np.array(rows)
    return float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])
