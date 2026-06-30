"""Export site/src/data/goals.json — payload for the goals over/under ladder page.

Runs the per-league-season Poisson (slow), caches per-match λ to
outputs/goals_lambda.csv so re-runs are fast, and serialises what /goals consumes:
the line ladder (predicted vs realised), the O/U 2.5 market anchor, the law curve,
the empirical total-goals histogram (for the smooth interactive slider) and the
goal-count skewness fact. Frozen club dataset.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import io, goals_ladder as gl, config as C

OUT = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data" / "goals.json"
CACHE = Path("outputs/goals_lambda.csv")


def round_rec(o, n=4):
    if isinstance(o, float): return round(o, n)
    if isinstance(o, dict): return {k: round_rec(v, n) for k, v in o.items()}
    if isinstance(o, list): return [round_rec(v, n) for v in o]
    return o


def main():
    df = io.load()
    if CACHE.exists():
        ml = pd.read_csv(CACHE)
        print(f"using cached λ ({len(ml):,} matches)")
    else:
        print(f"N={len(df):,} | fitting per-league-season goals Poisson...", flush=True)
        ml = gl.match_total_lambda(df)
        CACHE.parent.mkdir(exist_ok=True)
        ml.to_csv(CACHE, index=False)

    lad = gl.ladder(ml)
    anc = gl.anchor_25(df)

    # empirical total-goals histogram (for a smooth client-side line slider)
    tot = ml.tot.astype(int).values
    kmax = 10
    hist = [float((tot == k).mean()) for k in range(kmax)]
    hist.append(float((tot >= kmax).mean()))            # 10+ bucket
    prov = json.loads((C.DATA_PATH.parent / "PROVENANCE.json").read_text())

    data = {
        "meta": {"n": int(len(ml)), "sha256": prov["sha256"][:12],
                 "leagues": prov["leagues"], "date_min": prov["date_min"],
                 "date_max": prov["date_max"], "source": "football-data.co.uk"},
        "headline": {
            "max_calib_err": float(lad.calib_err.abs().max()),
            "corr_pred_real": float(np.corrcoef(lad.skew_pred, lad.skew_real)[0, 1]),
            "skew_min": float(lad.skew_pred.min()), "skew_max": float(lad.skew_pred.max()),
            "goal_mean": float(tot.mean()), "goal_skew": float(skew(tot)),
            "goal_skew_poisson": float(1 / np.sqrt(tot.mean())),
        },
        "ladder": [{"line": float(r.line), "p_model": float(r.p_model),
                    "p_real": float(r.p_real), "calib_err": float(r.calib_err),
                    "skew_pred": float(r.skew_pred), "skew_real": float(r.skew_real)}
                   for r in lad.itertuples()],
        "anchor": anc,
        "hist": hist,                                   # P(total = 0..9), then 10+
        "curve": gl.law_curve(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(round_rec(data), ensure_ascii=False, indent=0))
    print(f"-> {OUT}  ({OUT.stat().st_size/1024:.1f} KB) | {len(data['ladder'])} lines | "
          f"calib≤{data['headline']['max_calib_err']:.3f} | "
          f"anchor model {anc['p_model']:.3f}≈market {anc['p_market']:.3f}≈real {anc['p_real']:.3f}")


if __name__ == "__main__":
    main()
