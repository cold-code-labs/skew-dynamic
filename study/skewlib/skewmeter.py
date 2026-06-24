"""skew-meter — instrument for ASYMMETRY SIMILARITY.

Root objective of the study: measure how alike the asymmetries (skewness/shape)
of two entities are — leagues, eras, markets (1X2/O/U/AH), models, time windows.
Gathers the study's machinery into a single FEW-parameter apparatus:

  measure(p, o)            asymmetry signature (skew/var/exkurt + competitiveness).
  gauge_cheap / _1param /  decreasing-cost variants: without Shin (inverse-odds),
  _oddsfree                1 parameter (mean p_fav → closed form), and outcomes
                           only (upset rate).
  predict_skew(comp)       the law skew=f(competitiveness) evaluated (closed form).
  residual(sig)            IDIOSYNCRATIC asymmetry: skew − what competitiveness
                           explains. ≈0 ⇒ competitiveness is a sufficient statistic.
  skew_se(p, o)            sampling floor (bootstrap SE) — calibrates "alike".
  similar(A, B)            verdict: does the residual asymmetry fit within noise? (z-score).
  matrix(sigs)             pairwise distances: RAW vs RESIDUAL.

Anchor finding (Front B2, now operationalised): the RAW distance between leagues is
large, but the RESIDUAL one (conditioning on competitiveness) collapses to the sampling
floor — the asymmetries are the SAME once competitiveness is equalised. The apparatus
measures this pairwise, with a calibrated distance and null.
"""
import numpy as np
from . import exante, model


# ── measurement: asymmetry signature (with few-parameter variants) ───────────
def measure(p, o, label=None, n=None):
    """Asymmetry signature of an entity from (p_fav, o_fav)."""
    m = exante.pooled_moments(np.asarray(p, float), np.asarray(o, float), max_order=4)
    return {"label": label, "n": int(n if n is not None else len(p)),
            "skew": m["skew"], "var": m["var"], "exkurt": m["exkurt"],
            "within": m["within_frac_m3"], "comp": float(np.mean(p))}


def gauge_cheap(odds_HDA):
    """Signature WITHOUT Shin: favourite probability by normalised inverse-odds (1 op,
    ~0 cost). odds_HDA: (n,3) array of 1X2 odds. corr≈1.0 with the truth (Shin)."""
    r = 1.0 / np.asarray(odds_HDA, float)
    P = r / r.sum(1, keepdims=True)
    pf = P.max(1)
    return measure(pf, 1.0 / pf)


def gauge_oddsfree(upset_rate):
    """Odds-free proxy (W/D/L only): the competitiveness from the upset rate of the
    results Elo. Returns the competitiveness number; becomes skew via predict_skew∘map
    (corr≈0.83 — the limit of using no odds at all)."""
    return float(upset_rate)


# ── the law skew=f(competitiveness) as a basis of computation (1 parameter) ───
def fit_law(df):
    """Calibrates the closed curve S(competitiveness) once (ordered-probit) and returns
    a comp→skew evaluator. `df` needs FTResult and p_fav_dv."""
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.05, 1.30, 80)
    cpf, csk = model.curve_exact(par["h"], par["c"], sig)
    o = np.argsort(cpf)
    cpf, csk = cpf[o], csk[o]
    return {"par": par, "cpf": cpf, "csk": csk}


def predict_skew(comp, law):
    """Skew predicted by competitiveness (1 parameter), via closed form."""
    return float(np.interp(comp, law["cpf"], law["csk"]))


def residual(sig, law):
    """Idiosyncratic asymmetry: observed − explained by competitiveness."""
    return sig["skew"] - predict_skew(sig["comp"], law)


# ── sampling null: noise floor (calibrates 'alike') ──────────────────────────
def skew_se(p, o, B=300, seed=42):
    """Bootstrap SE of the pooled skew — the floor below which two asymmetries are
    indistinguishable. Resamples matches with replacement."""
    p = np.asarray(p, float); o = np.asarray(o, float); n = len(p)
    rng = np.random.default_rng(seed)
    vals = [exante.pooled_skew(p[i], o[i])["skew"]
            for i in (rng.integers(0, n, n) for _ in range(B))]
    return float(np.std(vals))


# ── asymmetry similarity ──────────────────────────────────────────────────────
def distance(A, B, kind="skew"):
    """RAW distance between signatures. kind='skew' (scalar) or 'shape'
    (standardised shape: skew + exkurt, scale-free)."""
    if kind == "skew":
        return abs(A["skew"] - B["skew"])
    da = np.array([A["skew"], A["exkurt"]]); db = np.array([B["skew"], B["exkurt"]])
    return float(np.linalg.norm(da - db))


def residual_distance(A, B, law):
    """Distance between asymmetries AFTER discounting competitiveness — how
    different A and B are beyond what competitiveness already explains."""
    return abs(residual(A, law) - residual(B, law))


def similar(A, B, law, seA=None, seB=None, z_thr=2.0):
    """Asymmetry similarity verdict. Compares the RESIDUAL distance to the combined
    sampling floor: z<z_thr ⇒ 'same asymmetry' (the difference is noise)."""
    rd = residual_distance(A, B, law)
    se = np.hypot(seA or 0.0, seB or 0.0)
    z = rd / se if se > 0 else np.inf
    return {"raw": distance(A, B), "residual": rd, "noise": float(se),
            "z": float(z), "same_asymmetry": bool(z < z_thr)}


def sufficiency_ladder(df, law, min_n=2000):
    """Sufficiency ladder: how much of the between-league asymmetry each set of
    competitiveness parameters explains. 1 moment (mean p_fav, closed form) →
    2 moments (mean+variance, OLS) → the WHOLE distribution (skew under fair odds,
    = mechanical image of the p distribution). Returns the R² of each rung."""
    import numpy as np
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_n:
            continue
        p = g.p_fav_dv.values; o = g.o_fav.values
        rows.append({"truth": exante.pooled_skew(p, o)["skew"],
                     "mean_pf": float(p.mean()), "var_pf": float(p.var()),
                     "pred1": predict_skew(float(p.mean()), law),
                     "full": exante.pooled_skew(p, 1.0 / p)["skew"]})
    t = np.array([r["truth"] for r in rows])
    def r2(pred): return float(np.corrcoef(t, pred)[0, 1] ** 2)
    p1 = np.array([r["pred1"] for r in rows])
    full = np.array([r["full"] for r in rows])
    X = np.column_stack([np.ones(len(rows)), [r["mean_pf"] for r in rows],
                         [r["var_pf"] for r in rows]])
    beta = np.linalg.lstsq(X, t, rcond=None)[0]
    p2 = X @ beta
    return {"r2_1param": r2(p1), "r2_2moment": r2(p2), "r2_full": r2(full),
            "n_leagues": len(rows), "resid_sd_1param": float((t - p1).std()),
            "resid_sd_full": float((t - full * (np.std(t) / np.std(full))).std())}


def split_half_residual(df, law, min_n=4000):
    """Stability of the idiosyncratic residual: corr between the residual measured in
    EVEN vs ODD seasons. High ⇒ the residual is a real league trait, not noise."""
    import numpy as np, pandas as pd
    d = df.copy(); d["yr"] = d.date.dt.year
    rows = []
    for lg, g in d.groupby("Division"):
        ev = g[g.yr % 2 == 0]; od = g[g.yr % 2 == 1]
        if len(ev) < min_n or len(od) < min_n:
            continue
        se = measure(ev.p_fav_dv.values, ev.o_fav.values)
        so = measure(od.p_fav_dv.values, od.o_fav.values)
        rows.append((residual(se, law), residual(so, law)))
    a = np.array([r[0] for r in rows]); b = np.array([r[1] for r in rows])
    return {"r": float(np.corrcoef(a, b)[0, 1]), "n_leagues": len(rows)}


def skew_se_block(g, B=150, seed=42):
    """Skew SE by BLOCK-bootstrap of SEASONS (resamples whole years) —
    respects the intra-season dependence that `skew_se` (i.i.d. matches) ignores.
    A more honest sampling floor. `g`: league frame with date/p_fav_dv/o_fav."""
    import numpy as np, pandas as pd
    g = g.copy(); g["yr"] = g.date.dt.year
    seasons = [sg for _, sg in g.groupby("yr")]
    if len(seasons) < 2:
        return skew_se(g.p_fav_dv.values, g.o_fav.values, B=B, seed=seed)
    rng = np.random.default_rng(seed); m = len(seasons)
    vals = []
    for _ in range(B):
        sub = pd.concat([seasons[i] for i in rng.integers(0, m, m)])
        vals.append(exante.pooled_skew(sub.p_fav_dv.values, sub.o_fav.values)["skew"])
    return float(np.std(vals))


def sampling_shape_cov(g, B=200, seed=1):
    """Sampling covariance of (skew, exkurt) of a league by bootstrap of matches —
    the metric for the Mahalanobis shape distance (scale- and correlation-aware)."""
    import numpy as np
    p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
    rng = np.random.default_rng(seed)
    S = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        m = exante.pooled_moments(p[i], o[i], max_order=4)
        S.append([m["skew"], m["exkurt"]])
    return np.cov(np.array(S).T)


def shape_distance(A, B, cov_inv):
    """MAHALANOBIS shape distance in (skew, exkurt) — scale/correlation-aware
    metric, superior to the scalar |Δskew| and the raw Euclidean of `distance(kind='shape')`."""
    import numpy as np
    d = np.array([A["skew"] - B["skew"], A["exkurt"] - B["exkurt"]])
    return float(np.sqrt(d @ cov_inv @ d))


def law_oos_r2(df, min_n=2000):
    """OUT-OF-SAMPLE calibration: fits the law on the rates of EVEN seasons and predicts
    the leagues' skew in ODD seasons (the law never sees the test target). High R²
    ⇒ the law is not overfit; the residual ruler is honest."""
    import numpy as np
    d = df.copy(); d["yr"] = d.date.dt.year
    ev, od = d[d.yr % 2 == 0], d[d.yr % 2 == 1]
    law_ev = fit_law(ev)
    t, pred = [], []
    for lg, g in od.groupby("Division"):
        if len(g) < min_n:
            continue
        t.append(exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"])
        pred.append(predict_skew(float(g.p_fav_dv.mean()), law_ev))
    return float(np.corrcoef(t, pred)[0, 1] ** 2)


def tost(A, B, law, seA, seB, margin):
    """Equivalence test (TOST) — the right verdict with huge n (significance
    always rejects). 'Same asymmetry' if the 90% CI of the residual difference fits
    within [−margin, +margin]. margin = half a between-league deviation, pre-registered."""
    import numpy as np
    d = residual(A, law) - residual(B, law)
    se = float(np.hypot(seA, seB))
    return {"d": float(d), "se": se, "margin": float(margin),
            "equivalent": bool(abs(d) + 1.645 * se < margin)}


def matrix(sigs, law, ses=None):
    """Pairwise distance matrices (RAW and RESIDUAL) between N entities.
    Returns a dict with the matrices and summaries. The RAW→RESIDUAL collapse is the
    study's asymmetry similarity, operationalised."""
    n = len(sigs)
    raw = np.zeros((n, n)); res = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            raw[i, j] = distance(sigs[i], sigs[j])
            res[i, j] = residual_distance(sigs[i], sigs[j], law)
    iu = np.triu_indices(n, 1)
    noise = float(np.median(ses)) if ses is not None else None
    return {"raw": raw, "residual": res,
            "labels": [s["label"] for s in sigs],
            "median_raw": float(np.median(raw[iu])),
            "median_residual": float(np.median(res[iu])),
            "noise_floor": noise,
            "collapse": float(np.median(res[iu]) / np.median(raw[iu]))}
