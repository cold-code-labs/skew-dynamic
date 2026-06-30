"""WC front (World Cup spin-off) — the structural skewness law on national teams.

Runs the odds-free Elo engine over ALL international history (1872→today),
slices the World Cup final stages (1930→2026, live) and confronts the PREDICTED
favourite-bet skewness (structural, via the Elo p_fav) with the REALISED one.
Three cuts: by p_fav bucket, by edition, by phase (group×knockout), plus an honest
out-of-time forecast (train through the group stage, predict the knockout, reveal).

Outputs: outputs/wc_by_pfav.csv, wc_by_edition.csv, wc_by_phase.csv,
wc_forecast.csv + a provenance stamp. No odds, no API key.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import worldcup as wc, exante, provenance as prov

DATA = Path("data/intl_results.csv")
OUT = Path("outputs"); OUT.mkdir(exist_ok=True)


def main():
    wc.ensure_dataset(DATA)
    fp = wc.dataset_fingerprint(DATA)
    print(f"dump: {fp['n_intl']:,} internationals | {fp['n_wc']:,} World Cup games "
          f"| {len(fp['editions'])} editions {fp['editions'][0]}–{fp['editions'][-1]} "
          f"| through {fp['date_max']}")

    intl = wc.load_internationals(DATA)
    fitted = wc.fit(intl)
    bet = wc.add_favorite_bet(fitted)
    wcup = wc.world_cup(bet)
    pool_pred = exante.pooled_skew(wcup.p_fav.values, wcup.o_fav.values)["skew"]
    pool_real = float(skew(wcup.ret_fav))
    ci = _boot_ci(wcup.ret_fav.values)
    print(f"World Cup: {len(wcup):,} games | predicted skew (pool) {pool_pred:+.3f} | "
          f"realised {pool_real:+.3f}  bootCI[{ci[0]:+.3f},{ci[1]:+.3f}]")

    # — MAIN CUT: predicted vs realised by p_fav bucket (large N, the 3rd moment
    #   stabilises). This is the out-of-sample validation of the structural law. —
    bk = wc.by_pfav_bucket(wcup)
    bk.to_csv(OUT / "wc_by_pfav.csv", index=False)
    print("\nValidation by p_fav bucket (the law, out of sample):")
    print(bk.to_string(index=False))
    r_bucket = float(np.corrcoef(bk.skew_pred, bk.skew_real)[0, 1])
    print(f"  corr(skew_pred, skew_real) by bucket = {r_bucket:+.3f}")

    # — by edition (1930→2026): noisy by construction (small N per edition) —
    by_ed = wc.pooled_by(wcup, "edition")
    by_ed.to_csv(OUT / "wc_by_edition.csv", index=False)

    # — by phase (group × knockout) —
    by_ph = wc.pooled_by(wcup, "phase")
    by_ph.to_csv(OUT / "wc_by_phase.csv", index=False)
    print("\nBy phase (all editions):")
    print(by_ph.to_string(index=False))

    e = by_ed.dropna(subset=["skew_pred", "skew_real"])
    r_ed = float(np.corrcoef(e.skew_pred, e.skew_real)[0, 1])
    r_comp = float(np.corrcoef(by_ed.p_fav_mean, by_ed.skew_pred)[0, 1])
    print(f"\ncorr(p_fav_mean, skew_pred) across editions = {r_comp:+.3f}  "
          f"(stronger favourite ⇒ more negative skew)")

    # — honest out-of-time forecast (train through groups, predict the knockout) —
    fc = _forecast_holdout(intl, wcup)

    prov.write_stamp("41_worldcup", metrics={
        "n_intl": fp["n_intl"], "n_wc": fp["n_wc"],
        "editions": len(fp["editions"]),
        "skew_pred_pool": round(pool_pred, 4),
        "skew_real_pool": round(pool_real, 4),
        "real_ci_lo": round(ci[0], 4), "real_ci_hi": round(ci[1], 4),
        "corr_bucket": round(r_bucket, 4),
        "corr_pred_real_edition": round(r_ed, 4),
        "corr_pfav_skew": round(r_comp, 4),
        "skew_group": round(float(by_ph.set_index("phase").loc["group", "skew_pred"]), 4),
        "skew_knockout": round(float(by_ph.set_index("phase").loc["knockout", "skew_pred"]), 4),
        "fc_edition": fc["edition"], "fc_pred": fc["pred"], "fc_real": fc["real"],
        "data_sha256": fp["sha256"][:16], "date_max": fp["date_max"],
    })


def _boot_ci(r, B=2000, seed=42):
    rng = np.random.default_rng(seed); n = len(r)
    bs = [skew(r[rng.integers(0, n, n)]) for _ in range(B)]
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _forecast_holdout(intl, wcup):
    """Out-of-time forecast: take the most recent edition that already has a
    knockout in the dump, train the Elo only through its group stage, and predict
    the knockout skew without looking at the score — then reveal the realised one.
    Proves the forecast mechanism the cron applies live to the 2026 knockout."""
    ko_all = wcup[wcup.phase == "knockout"]
    sizes = ko_all.groupby("edition").size()
    complete = sizes[sizes >= 8]                   # full knockout (≥8 games)
    if complete.empty:
        print("\n[forecast] no complete knockout in the dump — skipping.")
        return {"edition": None, "pred": None, "real": None}
    ed = int(complete.index.max())
    ko = wcup[(wcup.edition == ed) & (wcup.phase == "knockout")].copy()
    cutoff = ko.date.min()
    fx = ko[["date", "HomeTeam", "AwayTeam", "neutral", "FTResult"]]
    fcst, summary = wc.forecast(intl, fx, cutoff=cutoff)
    fcst.to_csv(OUT / "wc_forecast.csv", index=False)
    print(f"\n[forecast {ed}] train through {cutoff.date()} → knockout "
          f"({summary['n']} games): predicted skew {summary['skew_pred']:+.3f} | "
          f"realised {summary.get('skew_real', float('nan')):+.3f} | "
          f"upsets {summary.get('upset_rate', float('nan')):.0%}")
    return {"edition": ed, "pred": round(summary["skew_pred"], 4),
            "real": round(summary["skew_real"], 4) if summary.get("skew_real") is not None else None}


if __name__ == "__main__":
    main()
