"""Front O — three observers, one curve (strong observer-invariance test).

Three p-generators with disjoint information sets price the SAME favourite bet
at fair odds o = 1/p:
  elo     — match results only (pre-computed archive Elo + MNLogit link),
  book    — the market (Shin de-vig of the closing 1X2 line),
  players — player attributes only (log matchday-lineup market value + the
            same MNLogit link; state never sees a result or a price).
Per observer, matches are bucketed by its own p_fav; each bucket's REALISED
return skewness is compared to the law (1−2p)/√(p(1−p)). The observer's error
decomposes into calibration (p level, Brier — free to differ) and SHAPE
(realised skew at realised frequency — predicted ≡ 0 for every observer).

    python analysis/55_third_observer.py     # ~2 min with the TM dump cached
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import players as pl, devig, io as sio, provenance as prov

SITE = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data"
OUT = Path("outputs")
TRAIN_END = "2018-07-01"          # link fit era (disjoint from evaluation)
ERA_START = "2013-07-01"          # lineups ≥95% from 2013 (docs/SPIKE-O0.md)
EDGES = np.arange(0.35, 0.925, 0.05)
RNG = np.random.default_rng(7)


def law(p):
    p = np.asarray(p, float)
    return (1 - 2 * p) / np.sqrt(p * (1 - p))


def fav_returns(pH, pA, res):
    """Favourite 1X2 bet at fair odds 1/p: (p_fav, ret, won)."""
    fav_h = pH >= pA
    p = np.where(fav_h, pH, pA)
    won = np.where(fav_h, res == "H", res == "A")
    ret = np.where(won, 1.0 / p - 1.0, -1.0)
    return p, ret, won


def buckets(p, ret, won, n_boot=1000, min_n=200):
    rows = []
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        m = (p >= lo) & (p < hi)
        if m.sum() < min_n:
            continue
        r, w = ret[m], won[m]
        s = skew(r)
        bs = np.array([skew(RNG.choice(r, size=len(r), replace=True))
                       for _ in range(n_boot)])
        rows.append({"p_lo": lo, "p_hi": hi, "n": int(m.sum()),
                     "p_mean": float(p[m].mean()), "freq": float(w.mean()),
                     "skew_real": float(s),
                     "ci_lo": float(np.percentile(bs, 2.5)),
                     "ci_hi": float(np.percentile(bs, 97.5)),
                     "skew_law_p": float(law(p[m].mean())),
                     "skew_law_freq": float(law(w.mean()))})
    return pd.DataFrame(rows)


def metrics(b, p, won):
    shape = b.skew_real - b.skew_law_freq          # ≡ 0 under the law
    calib = b.p_mean - b.freq                      # free to differ
    return {"n_buckets": len(b), "n_matches": int(len(p)),
            "corr_law": float(np.corrcoef(b.skew_law_p, b.skew_real)[0, 1]),
            "rmse_law": float(np.sqrt(((b.skew_real - b.skew_law_p) ** 2).mean())),
            "shape_rmse": float(np.sqrt((shape ** 2).mean())),
            "shape_max_abs": float(shape.abs().max()),
            "calib_mean_abs": float(calib.abs().mean()),
            "brier": float(((p - won) ** 2).mean())}


def main():
    OUT.mkdir(exist_ok=True)
    d = sio.load()
    d = d[(d.date >= ERA_START) & d.Division.isin(pl.DIV2COMP)].copy()

    # ── players observer: club map + matchday lineup values ─────────────────
    pl.ensure_tm()
    vals = pl.lineup_values()
    names = pl.tm_names_by_comp()
    teams_by_div = {dv: set(g.HomeTeam) | set(g.AwayTeam)
                    for dv, g in d.groupby("Division")}
    overrides = (json.loads(pl.CLUB_MAP.read_text()).get("overrides", {})
                 if pl.CLUB_MAP.exists() else {})
    cmap, misses = pl.build_club_map(teams_by_div, names, overrides=overrides)
    pl.CLUB_MAP.parent.mkdir(parents=True, exist_ok=True)
    pl.CLUB_MAP.write_text(json.dumps(
        {"map": {dv: {t: int(c) for t, c in m.items()} for dv, m in cmap.items()},
         "overrides": overrides,
         "unmatched": [f"{dv}|{t}" for dv, t in misses]}, indent=1, ensure_ascii=False))
    j = pl.attach_values(d, vals, cmap)
    j = j[np.isfinite(j.lv_gap) & j.HomeElo.notna() & j.AwayElo.notna()]
    print(f"joined {len(j):,}/{len(d):,} frozen matches "
          f"({len(misses)} team names unmatched)")

    train = j[j.date < TRAIN_END]
    ev = j[j.date >= TRAIN_END].copy()
    link = pl.calibrate_value_link(train)
    pl.save_value_link(link, meta={"train_n": len(train), "train_end": TRAIN_END,
                                   "era_start": ERA_START})
    pA, pD, pH = pl.apply_value_link(link, ev.lv_gap.values)
    obs = {"players": (pH, pA)}

    # ── elo observer: same link form on the archive's pre-computed ratings ──
    def elo_fit(frame):
        y = frame.FTResult.map({"A": 0, "D": 1, "H": 2}).values
        z = (frame.HomeElo - frame.AwayElo).values / 400.0
        X = sm.add_constant(np.column_stack([z, z * z]))
        return sm.MNLogit(y, X).fit(disp=0)

    me = elo_fit(train)
    ze = (ev.HomeElo - ev.AwayElo).values / 400.0
    Pe = np.asarray(me.predict(sm.add_constant(
        np.column_stack([ze, ze * ze]), has_constant="add")))
    obs["elo"] = (Pe[:, 2], Pe[:, 0])

    # ── book observer: Shin de-vig of the closing line ───────────────────────
    pb = devig.devig_frame(ev, method="shin")
    obs["book"] = (pb.p_H.values, pb.p_A.values)

    # ── the test ─────────────────────────────────────────────────────────────
    res = ev.FTResult.values
    site, table, stamp = {}, [], {}
    for name, (ph, pa) in obs.items():
        ok = ~(np.isnan(ph) | np.isnan(pa))
        p, ret, won = fav_returns(ph[ok], pa[ok], res[ok])
        b = buckets(p, ret, won)
        mt = metrics(b, p, won)
        print(f"{name:8s} n={mt['n_matches']:>6,} corr_law={mt['corr_law']:+.3f} "
              f"shape_rmse={mt['shape_rmse']:.3f} calib={mt['calib_mean_abs']:.3f} "
              f"brier={mt['brier']:.3f}")
        b.insert(0, "observer", name)
        table.append(b)
        site[name] = {"buckets": b.drop(columns="observer").to_dict("records"),
                      "metrics": mt}
        stamp.update({f"{name}_corr_law": round(mt["corr_law"], 4),
                      f"{name}_shape_rmse": round(mt["shape_rmse"], 4),
                      f"{name}_brier": round(mt["brier"], 4)})

    pd.concat(table).to_csv(OUT / "third_observer_buckets.csv", index=False)
    SITE.joinpath("observers.json").write_text(json.dumps(
        {"schema": "observers@1", "era": [TRAIN_END, str(ev.date.max().date())],
         "train": [ERA_START, TRAIN_END], "n_eval": int(len(ev)),
         "law": "(1-2p)/sqrt(p(1-p))", "observers": site}, indent=1))
    stamp["n_eval"] = len(ev)
    prov.write_stamp("55_third_observer", metrics=stamp)
    print(f"-> {OUT/'third_observer_buckets.csv'} | site observers.json")


if __name__ == "__main__":
    main()
