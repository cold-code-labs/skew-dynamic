"""Front O — battery of generative models: is the law skewness=f(competitiveness)
model-independent? Front I showed that a goals Poisson falls on the same curve as
the margin ordered-probit. Here we widen it to a BATTERY of genuinely distinct
generators, each producing (pH,pD,pA) per game, and test whether ALL reproduce the
law and fall on the S(σ_L) curve of the strength model:

  • Poisson (Maher)         — independent goals; anchor on the grid (= Front I).
  • Dixon-Coles (1997)      — Poisson + low-score dependence correction (ρ): fine
                              adjustment of 0-0/0-1/1-0/1-1 vs independence.
  • Bradley-Terry-Davidson  — multiplicative strengths + draw (Davidson 1970), by
    (1970)                    logistic PAIRWISE COMPARISON, WITHOUT goals. A family
                              completely distinct (neither Poisson nor probit).
  • Results Elo             — strengths by results rating (no goals, no odds) →
                              ordinal map (MNLogit). 4th family, links to W2/P2.

The goals generators (Poisson/DC) share the λ rates from `goals.fit_rates`
(same attack/defence+home advantage), isolating the effect of the dependence (ρ) on
the outcome probabilities and the skewness. BTD and Elo fit their own strengths.
All use `goals.degenerate_fit` to discard degenerate fits (GLM separation,
e.g.: JAP 2017).

Note (models that do NOT enter): football goals are almost pure independent
Poisson — home×away covariance ≈ −0.07 (median) and over-dispersion ≈ 0. So a
BIVARIATE Poisson (λ₃≥0) and a Negative-Binomial (NB2, α) collapse to the Poisson
and add nothing to the figure; we report this collapse as robustness, not as a series.
"""
import warnings
import numpy as np, pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize_scalar, minimize
from . import goals, exante
warnings.filterwarnings("ignore")

MAXG = 12                       # goals ceiling on the grid (tail beyond this negligible)
_GG = np.arange(MAXG + 1)
MODELS = ["poisson", "dixoncoles", "btd", "elo"]


def _result_probs(joint):
    """(pH,pD,pA) from the joint joint[...,x,y]=P(home=x, away=y): home
    wins x>y (lower triangular), draw x=y (diagonal), away x<y."""
    H = np.tril(joint, -1).sum(axis=(-2, -1))
    A = np.triu(joint, 1).sum(axis=(-2, -1))
    D = np.trace(joint, axis1=-2, axis2=-1)
    s = H + D + A
    return H / s, D / s, A / s


def _poisson_grid(lh, la):
    """Independent joint P(x,y)=Pois(x;lh)·Pois(y;la) per game → (M,G+1,G+1)."""
    px = poisson.pmf(_GG[None, :], lh[:, None])
    py = poisson.pmf(_GG[None, :], la[:, None])
    return px[:, :, None] * py[:, None, :]


# ── Dixon-Coles (1997): low-score dependence correction ──────────────────────
def dc_rho(lh, la, x, y):
    """Dixon-Coles ρ by PROFILE likelihood (λ fixed from the GLM): only the 4
    low scores {(0,0),(0,1),(1,0),(1,1)} depend on ρ via τ; the rest
    contribute log 1. Bounded to a safe range to keep τ>0."""
    x = np.asarray(x); y = np.asarray(y)
    m00 = (x == 0) & (y == 0); m01 = (x == 0) & (y == 1)
    m10 = (x == 1) & (y == 0); m11 = (x == 1) & (y == 1)

    def negll(rho):
        t = np.ones(len(x))
        t[m00] = 1.0 - lh[m00] * la[m00] * rho
        t[m01] = 1.0 + lh[m01] * rho
        t[m10] = 1.0 + la[m10] * rho
        t[m11] = 1.0 - rho
        return -np.log(np.clip(t, 1e-9, None)).sum()
    return float(minimize_scalar(negll, bounds=(-0.3, 0.3), method="bounded").x)


def dc_probs(lh, la, rho):
    """(pH,pD,pA) per game under Dixon-Coles: Poisson + τ(ρ) on the 4 low scores.
    ρ=0 recovers exactly the independent Poisson (battery anchor on the grid)."""
    joint = _poisson_grid(lh, la)
    joint[:, 0, 0] *= np.clip(1.0 - lh * la * rho, 1e-9, None)
    joint[:, 0, 1] *= np.clip(1.0 + lh * rho, 1e-9, None)
    joint[:, 1, 0] *= np.clip(1.0 + la * rho, 1e-9, None)
    joint[:, 1, 1] *= np.clip(1.0 - rho, 1e-9, None)
    return _result_probs(joint)


# ── Bradley-Terry-Davidson (1970): strengths + draw, pairwise comparison ─────
def btd_probs(g, ridge=1e-3):
    """Fits the Davidson model (Bradley-Terry with draws + home advantage) by MLE and
    returns (pH,pD,pA) per game. Strengths θ per team (zero-sum via reference team),
    home advantage log α and draw parameter log ν:
        pH ∝ exp(α+θ_i), pA ∝ exp(θ_j), pD ∝ exp(ν+(α+θ_i+θ_j)/2).
    A family completely distinct from the goals/probit models. None if it fails."""
    teams = sorted(set(g.HomeTeam) | set(g.AwayTeam))
    idx = {t: k for k, t in enumerate(teams)}
    n = len(teams)
    hi = g.HomeTeam.map(idx).to_numpy(); aj = g.AwayTeam.map(idx).to_numpy()
    res = g.FTResult.map({"H": 0, "D": 1, "A": 2}).to_numpy()

    def probs(w):
        th = np.concatenate([[0.0], w[:n - 1]])      # team 0 = reference (zero-sum)
        la, lv = w[n - 1], w[n]                       # logα (home advantage), logν (draw)
        ti = th[hi]; tj = th[aj]
        eh = np.exp(la + ti); ea = np.exp(tj)
        ed = np.exp(lv + 0.5 * (la + ti + tj))
        Z = eh + ea + ed
        return np.vstack([eh / Z, ed / Z, ea / Z]).T, th

    def negll(w):
        p, th = probs(w)
        ll = np.log(np.clip(p[np.arange(len(res)), res], 1e-12, None)).sum()
        return -ll + ridge * float(th @ th)           # ridge for identifiability
    w0 = np.zeros(n + 1); w0[n - 1] = 0.3             # reasonable initial logα
    try:
        sol = minimize(negll, w0, method="L-BFGS-B")
    except Exception:
        return None
    p, _ = probs(sol.x)
    return p[:, 0], p[:, 1], p[:, 2]


# ── battery ───────────────────────────────────────────────────────────────────
def _pfav(pH, pD, pA):
    return np.clip(np.vstack([pH, pD, pA]).T.max(1), 1e-6, 1 - 1e-6)


def battery_table(df, min_games=150, min_teams=8):
    """Favourite skewness per league-season under EACH model of the battery vs
    empirical. Requires add_exante (p_fav_dv, o_fav) and a `season` column. Discards
    degenerate fits (separation) via goals.degenerate_fit: in the goals generators
    the degeneracy comes from the shared λ ⇒ the entire league-season drops out."""
    rows = []
    for (lg, yr), g in df.groupby(["Division", "season"]):
        if len(g) < min_games or g.HomeTeam.nunique() < min_teams:
            continue
        rates = goals.fit_rates(g)
        if rates is None:
            continue
        lh, la = rates
        x = g.FTHome.astype(int).to_numpy(); y = g.FTAway.astype(int).to_numpy()
        pfe = g.p_fav_dv.values
        if goals.degenerate_fit(_pfav(*dc_probs(lh, la, 0.0)), pfe):
            continue                                  # degenerate λ (e.g.: JAP 2017)
        gens = {
            "poisson": dc_probs(lh, la, 0.0),
            "dixoncoles": dc_probs(lh, la, dc_rho(lh, la, x, y)),
        }
        btd = btd_probs(g)
        if btd is not None and not goals.degenerate_fit(_pfav(*btd), pfe):
            gens["btd"] = btd
        row = {"Division": lg, "season": int(yr), "n": len(g),
               "skew_emp": exante.pooled_skew(pfe, g.o_fav.values)["skew"],
               "pfav_emp": float(pfe.mean())}
        for name, (pH, pD, pA) in gens.items():
            pf = _pfav(pH, pD, pA)
            row[f"skew_{name}"] = exante.pooled_skew(pf, 1.0 / pf)["skew"]
            row[f"pfav_{name}"] = float(pf.mean())
        rows.append(row)
    return pd.DataFrame(rows)


def by_league(tab, models=MODELS):
    """Aggregates league-season → league (means) for skew and pfav of each model + emp."""
    agg = {"n": ("n", "sum"), "seasons": ("season", "nunique"),
           "skew_emp": ("skew_emp", "mean"), "pfav_emp": ("pfav_emp", "mean")}
    for m in models:
        if f"skew_{m}" in tab:
            agg[f"skew_{m}"] = (f"skew_{m}", "mean")
            agg[f"pfav_{m}"] = (f"pfav_{m}", "mean")
    return tab.groupby("Division").agg(**agg).reset_index()


def elo_by_league(df):
    """4th family — ODDS-FREE generator: strengths by RESULTS Elo (no goals, no
    odds, chronological multi-league pass) → ordinal map rating-diff→(pH,pD,pA) by
    MNLogit calibrated on the results (W2/P2) → favourite skewness per league. Since
    the Elo is a single global model, we aggregate the per-game probabilities within
    each league (there is no refit per league-season)."""
    from . import elo
    d = elo.with_elo(df)
    rows = []
    for lg, g in d.groupby("Division"):
        pf = np.clip(g[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float).max(1),
                     1e-6, 1 - 1e-6)
        rows.append({"Division": lg, "n": len(g),
                     "skew_elo": exante.pooled_skew(pf, 1.0 / pf)["skew"],
                     "pfav_elo": float(pf.mean())})
    return pd.DataFrame(rows)
