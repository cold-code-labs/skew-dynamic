"""Export site/src/data/worldcup.json — payload for the World Cup spin-off.

Runs the odds-free Elo engine over the internationals, slices the World Cup and
serialises what the site's /worldcup page consumes (validation by p_fav bucket,
series by edition, contrast by phase, out-of-time forecast). It is the artefact
the cron regenerates during the tournament. Runs locally (needs
data/intl_results.csv); the JSON is versioned so the site build does not depend
on the raw dump.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import worldcup as wc, exante

DATA = Path("data/intl_results.csv")
OUT = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data" / "worldcup.json"


def round_rec(o, n=4):
    if isinstance(o, float): return round(o, n)
    if isinstance(o, dict): return {k: round_rec(v, n) for k, v in o.items()}
    if isinstance(o, list): return [round_rec(v, n) for v in o]
    return o


def main():
    wc.ensure_dataset(DATA)
    fp = wc.dataset_fingerprint(DATA)
    intl = wc.load_internationals(DATA)
    wcup = wc.world_cup(wc.add_favorite_bet(wc.fit(intl)))

    pool_pred = exante.pooled_skew(wcup.p_fav.values, wcup.o_fav.values)["skew"]
    pool_real = float(skew(wcup.ret_fav))

    bk = wc.by_pfav_bucket(wcup)
    by_ed = wc.pooled_by(wcup, "edition")
    by_ph = wc.pooled_by(wcup, "phase")
    r_bucket = float(np.corrcoef(bk.skew_pred, bk.skew_real)[0, 1])
    r_comp = float(np.corrcoef(by_ed.p_fav_mean, by_ed.skew_pred)[0, 1])

    # theoretical curve (1-2p)/√(p(1-p)) to overlay on the points
    pgrid = np.linspace(0.34, 0.92, 60)
    curve = [{"p": float(p), "skew": float(exante.per_match_skew(p))} for p in pgrid]

    fc = _forecast(intl, wcup)

    data = {
        "meta": {"n_intl": fp["n_intl"], "n_wc": fp["n_wc"],
                 "editions": len(fp["editions"]),
                 "edition_min": fp["editions"][0], "edition_max": fp["editions"][-1],
                 "date_max": fp["date_max"], "sha256": fp["sha256"][:12],
                 "source": "martj42/international_results"},
        "headline": {"skew_pred_pool": pool_pred, "skew_real_pool": pool_real,
                     "corr_bucket": r_bucket, "corr_pfav_skew": r_comp,
                     "law": "(1-2p)/sqrt(p(1-p))"},
        "buckets": [{"p_fav": float(r.p_fav), "n": int(r.n),
                     "skew_pred": float(r.skew_pred), "skew_real": float(r.skew_real),
                     "win_rate": float(r.win_rate)} for r in bk.itertuples()],
        "curve": curve,
        "by_edition": [{"edition": int(r.edition), "n": int(r.n),
                        "p_fav": float(r.p_fav_mean), "skew_pred": float(r.skew_pred),
                        "skew_real": float(r.skew_real)} for r in by_ed.itertuples()],
        "by_phase": [{"phase": r.phase, "n": int(r.n), "p_fav": float(r.p_fav_mean),
                      "skew_pred": float(r.skew_pred), "skew_real": float(r.skew_real),
                      "upset_rate": float(r.upset_rate)} for r in by_ph.itertuples()],
        "forecast": fc,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(round_rec(data), ensure_ascii=False, indent=0))
    print(f"-> {OUT}  ({OUT.stat().st_size/1024:.1f} KB) | "
          f"{len(data['buckets'])} buckets, {len(data['by_edition'])} editions | "
          f"corr_bucket {r_bucket:+.3f}")


def _forecast(intl, wcup):
    """Out-of-time forecast for the most recent edition with a complete knockout,
    plus the live state of the cup (predicted skew of the 2026 games in the dump)."""
    ko = wcup[wcup.phase == "knockout"]
    sizes = ko.groupby("edition").size()
    complete = sizes[sizes >= 8]
    out = {"holdout": None, "live2026": None}
    if not complete.empty:
        ed = int(complete.index.max())
        sub = wcup[(wcup.edition == ed) & (wcup.phase == "knockout")]
        fx = sub[["date", "HomeTeam", "AwayTeam", "neutral", "FTResult"]]
        fcst, s = wc.forecast(intl, fx, cutoff=sub.date.min())
        out["holdout"] = {"edition": ed, "n": s["n"], "skew_pred": s["skew_pred"],
                          "skew_real": s.get("skew_real"),
                          "upset_rate": s.get("upset_rate")}
    cur = wcup[wcup.edition == 2026]
    if not cur.empty:
        out["live2026"] = {
            "n_played": int(len(cur)),
            "skew_pred": exante.pooled_skew(cur.p_fav.values, cur.o_fav.values)["skew"],
            "skew_real": float(skew(cur.ret_fav)) if len(cur) > 2 else None,
            "p_fav_mean": float(cur.p_fav.mean()),
            "date_max": str(cur.date.max().date())}
    return out


if __name__ == "__main__":
    main()
