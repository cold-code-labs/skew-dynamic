"""World Cup spin-off: the structural skewness law applied to national teams.

Outside the paper's population (clubs → national teams, league → knockout
tournament) and with NO odds: we use the odds-free engine in `elo.py`
(results → Elo → MNLogit → p_fav) to predict the return-skewness of a 1X2 bet on
the favourite, match by match, and pooled by edition/phase via
`exante.pooled_skew`. It is an out-of-sample, real-time test (the 2026 World Cup
is under way) of the structural-invariance thesis: skewness is the algebraic
image of p_fav, not a dynamic phenomenon.

The bet: stake 1 unit on the Elo favourite (the highest-probability outcome).
Without a market we use FAIR odds o = 1/p (zero EV) — so the predicted skewness
is purely the two-point shape, and the realised one is the empirical skew of the
return. When real odds are available (2026 overlay), `o` becomes the market price.
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

from . import elo, exante

SOURCE_URL = ("https://raw.githubusercontent.com/martj42/"
              "international_results/master/results.csv")
WC_TOURNAMENT = "FIFA World Cup"


def ensure_dataset(path):
    """Download the internationals dump if it does not exist yet (clean clone).
    The data is live and gitignored — this is the annex's only network dependency."""
    import urllib.request
    p = Path(path)
    if p.exists():
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(p, "wb") as f:
        f.write(r.read())
    return p


# ── load / normalise ──────────────────────────────────────────────────────────
def load_internationals(path):
    """Read the martj42 dump and normalise to the skewlib schema (HomeTeam, …)."""
    raw = pd.read_csv(path)
    d = pd.DataFrame({
        "date": pd.to_datetime(raw["date"], errors="coerce"),
        "HomeTeam": raw["home_team"].astype(str),
        "AwayTeam": raw["away_team"].astype(str),
        "FTHome": pd.to_numeric(raw["home_score"], errors="coerce"),
        "FTAway": pd.to_numeric(raw["away_score"], errors="coerce"),
        "tournament": raw["tournament"].astype(str),
        "neutral": raw["neutral"].astype(str).str.upper().eq("TRUE"),
    }).dropna(subset=["date", "FTHome", "FTAway"])
    d["FTResult"] = np.where(d.FTHome > d.FTAway, "H",
                      np.where(d.FTHome < d.FTAway, "A", "D"))
    d["Division"] = "INTL"  # field required by skewlib
    return d.sort_values("date").reset_index(drop=True)


def upcoming_wc_fixtures(path):
    """World Cup fixtures not yet played: the dump carries a scheduled match as a
    row with empty score (home_score/away_score blank). Returns them normalised,
    with a stable match_id (date|home|away) for later reconciliation."""
    raw = pd.read_csv(path)
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    fx = raw[(raw["tournament"] == WC_TOURNAMENT)
             & (raw["home_score"].isna() | raw["away_score"].isna())].copy()
    out = pd.DataFrame({
        "date": fx["date"],
        "HomeTeam": fx["home_team"].astype(str),
        "AwayTeam": fx["away_team"].astype(str),
        "neutral": fx["neutral"].astype(str).str.upper().eq("TRUE"),
    }).dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    out["match_id"] = (out.date.dt.strftime("%Y-%m-%d") + "|"
                       + out.HomeTeam + "|" + out.AwayTeam)
    return out


def predict_upcoming(intl, fixtures, k=20.0, hfa=65.0):
    """Pre-game prediction (no score): chronological Elo over all played games →
    each team's final rating; applies the calibrated MNLogit map to the fixtures.
    Returns fixtures + p_fav, fav_pick, o_fav (=1/p fair), predicted skewness."""
    d, R = elo.run_elo(intl, k=k, hfa=hfa, neutral_col="neutral")
    _, model = elo.calibrate_outcomes(d)
    fx = fixtures.copy().reset_index(drop=True)
    rh = fx.HomeTeam.map(lambda t: R.get(t, 1500.0)).to_numpy(float)
    ra = fx.AwayTeam.map(lambda t: R.get(t, 1500.0)).to_numpy(float)
    hfa_i = np.where(fx.neutral.to_numpy(bool), 0.0, hfa)
    fx["elo_diff"] = (rh + hfa_i) - ra
    pH, pD, pA = _predict_p(model, fx.elo_diff.values)
    fx["pH_elo"], fx["pD_elo"], fx["pA_elo"] = pH, pD, pA
    fx = _features_no_result(fx)
    fx = add_favorite_bet(fx)
    fx["fav_team"] = np.select(
        [fx.fav_pick == "H", fx.fav_pick == "A"],
        [fx.HomeTeam, fx.AwayTeam], default="Draw")
    return fx


def dataset_fingerprint(path):
    """sha256 + coverage — provenance of the live dump (updates during the cup)."""
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    d = load_internationals(path)
    wc = d[d.tournament == WC_TOURNAMENT]
    return {"sha256": h, "n_intl": int(len(d)),
            "n_wc": int(len(wc)), "date_max": str(d.date.max().date()),
            "editions": sorted(wc.date.dt.year.unique().tolist())}


# ── odds-free Elo model + favourite bet ───────────────────────────────────────
def fit(df, k=20.0, hfa=65.0):
    """Run a chronological Elo over ALL internationals (rating carries across
    tournaments) + calibrate the rating-diff→(H,D,A) map. Returns the df with Elo
    p_H/p_D/p_A and per-game features. HFA applies only at home games (neutral=False)."""
    d, _ = elo.run_elo(df, k=k, hfa=hfa, neutral_col="neutral")
    d, _ = elo.calibrate_outcomes(d)
    return elo.add_elo_features(d)


def add_favorite_bet(d, odd_cols=None):
    """Bet on the Elo favourite. p_fav = prob. of the most likely outcome; the
    favourite may be H/D/A. o_fav = FAIR odds (1/p) or market odds if `odd_cols`
    given. Adds p_fav, o_fav, skew_exante_match (closed form) and ret_fav (realised)."""
    P = d[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float)
    j = P.argmax(axis=1)
    i = np.arange(len(P))
    p_fav = P[i, j]
    pick = np.array(["H", "D", "A"])[j]
    out = d.copy()
    out["p_fav"] = p_fav
    out["fav_pick"] = pick
    if odd_cols:                                   # market overlay
        O = d[list(odd_cols)].to_numpy(float)
        out["o_fav"] = O[i, j]
    else:                                          # fair odds (zero EV)
        out["o_fav"] = 1.0 / p_fav
    out["skew_exante_match"] = exante.per_match_skew(p_fav)
    if "FTResult" in d:                            # realised (match already played)
        win = out["fav_pick"].values == d["FTResult"].values
        out["ret_fav"] = np.where(win, out["o_fav"].values - 1.0, -1.0)
    return out


# ── tournament cuts ───────────────────────────────────────────────────────────
def world_cup(d):
    """Subset of World Cup final stages, with edition and phase (group/knockout)."""
    wc = d[d.tournament == WC_TOURNAMENT].copy()
    wc["edition"] = wc.date.dt.year
    wc = wc.sort_values("date").reset_index(drop=True)
    wc["phase"] = _phase(wc)
    return wc


def _phase(wc):
    """Robust heuristic: within an edition, each team's n-th game; knockout = both
    teams have already played ≥3 (modern group-stage format)."""
    appears = {}
    home_idx = np.empty(len(wc), int); away_idx = np.empty(len(wc), int)
    for r, (ed, h, a) in enumerate(zip(wc.edition, wc.HomeTeam, wc.AwayTeam)):
        home_idx[r] = appears.get((ed, h), 0)
        away_idx[r] = appears.get((ed, a), 0)
        appears[(ed, h)] = home_idx[r] + 1
        appears[(ed, a)] = away_idx[r] + 1
    ko = (np.minimum(home_idx, away_idx) >= 3)
    return np.where(ko, "knockout", "group")


def by_pfav_bucket(wc, edges=(0.33, 0.42, 0.48, 0.54, 0.62, 1.0)):
    """The main validation: PREDICTED skewness (structural) vs REALISED, by p_fav
    bucket, with large N per bucket (the 3rd moment stabilises). Mirrors the FLB
    table B2 of the club study. win_rate≈p_fav attests the odds-free Elo's calibration."""
    d = wc.copy()
    d["bucket"] = pd.cut(d.p_fav, list(edges))
    rows = []
    for b, g in d.groupby("bucket", observed=True):
        if len(g) < 20:
            continue
        pk = exante.pooled_skew(g.p_fav.values, g.o_fav.values)
        rows.append({"bucket": str(b), "n": int(len(g)),
                     "p_fav": float(g.p_fav.mean()),
                     "skew_pred": pk["skew"],
                     "skew_real": float(skew(g.ret_fav)),
                     "win_rate": float((g.ret_fav > 0).mean())})
    return pd.DataFrame(rows)


def pooled_by(wc, by):
    """Predicted skew (structural, via p_fav) vs realised (empirical) per group."""
    rows = []
    for key, g in wc.groupby(by, observed=True):
        if len(g) < 4:
            continue
        d = exante.pooled_skew(g.p_fav.values, g.o_fav.values)
        rows.append({**({by: key} if not isinstance(by, list) else dict(zip(by, key))),
                     "n": int(len(g)),
                     "p_fav_mean": float(g.p_fav.mean()),
                     "elo_entropy": float(g.elo_entropy.mean()),
                     "skew_pred": d["skew"],
                     "skew_real": float(skew(g.ret_fav)),
                     "upset_rate": float(g.elo_upset.mean()),
                     "ret_mean": float(g.ret_fav.mean())})
    return pd.DataFrame(rows)


def _predict_p(model, elo_diff):
    """Apply the calibrated MNLogit map (elo_diff → P_A,P_D,P_H)."""
    import statsmodels.api as sm
    z = np.asarray(elo_diff, float) / 400.0
    X = sm.add_constant(np.column_stack([z, z * z]), has_constant="add")
    P = np.asarray(model.predict(X))           # columns A,D,H
    return P[:, 2], P[:, 1], P[:, 0]           # return pH, pD, pA


def forecast(df, fixtures, cutoff, k=20.0, hfa=65.0):
    """Honest forecast: train Elo only on games BEFORE `cutoff` and predict the
    skew of the favourite bet for `fixtures` (DataFrame with HomeTeam/AwayTeam/
    neutral), without looking at their result. Returns (fixtures_with_prediction,
    pooled_summary). `fixtures` may be a dataset slice (hold-out) or future games
    from a schedule feed. If it carries FTResult, the realised value is revealed."""
    cutoff = pd.Timestamp(cutoff)
    train = df[df.date < cutoff]
    _, R = elo.run_elo(train, k=k, hfa=hfa, neutral_col="neutral")
    fitted, _ = elo.run_elo(train, k=k, hfa=hfa, neutral_col="neutral")
    _, model = elo.calibrate_outcomes(fitted)

    fx = fixtures.copy().reset_index(drop=True)
    rh = fx.HomeTeam.map(lambda t: R.get(t, 1500.0)).to_numpy(float)
    ra = fx.AwayTeam.map(lambda t: R.get(t, 1500.0)).to_numpy(float)
    hfa_i = np.where(fx.neutral.to_numpy(bool), 0.0, hfa)
    fx["elo_diff"] = (rh + hfa_i) - ra
    pH, pD, pA = _predict_p(model, fx.elo_diff.values)
    fx["pH_elo"], fx["pD_elo"], fx["pA_elo"] = pH, pD, pA
    fx = elo.add_elo_features(fx) if "FTResult" in fx else _features_no_result(fx)
    fx = add_favorite_bet(fx)

    summary = exante.pooled_skew(fx.p_fav.values, fx.o_fav.values)
    summary = {"n": int(len(fx)), "p_fav_mean": float(fx.p_fav.mean()),
               "skew_pred": summary["skew"]}
    if "FTResult" in fx:
        summary["skew_real"] = float(skew(fx.ret_fav))
        summary["upset_rate"] = float(fx.elo_upset.mean())
    return fx, summary


def _features_no_result(fx):
    """Elo features when games have not been played yet (no FTResult)."""
    P = fx[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float)
    out = fx.copy()
    out["elo_entropy"] = -(P * np.log(np.clip(P, 1e-12, 1.0))).sum(1)
    out["elo_pfav"] = P.max(1)
    return out
