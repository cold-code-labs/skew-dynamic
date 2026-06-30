"""Goals annex — the over/under ladder. The same skewness law, dialled by the line.

Sweeps the total-goals line L over a fixed match population: each line is a
two-point Over bet with p = P(total > L), sourced odds-free from a per-league-season
Poisson goals model (skewlib.goals). Predicted vs realised skewness across the
ladder + the O/U 2.5 market anchor (the one line with real odds). The line is the
knob — goals reach p from ~0.92 (line 0.5) to ~0.13 (line 4.5), hitting the law's
tails that the 1X2 favourite never reaches.

Outputs: outputs/goals_ladder.csv + a provenance stamp. Frozen club dataset.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import io, goals_ladder as gl, provenance as prov

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)


def main():
    df = io.load()
    print(f"N={len(df):,} | fitting per-league-season goals Poisson "
          f"(this takes a couple of minutes)...", flush=True)
    ml = gl.match_total_lambda(df)
    print(f"  {len(ml):,} matches with a valid goals-model fit")

    lad = gl.ladder(ml)
    lad.to_csv(OUT / "goals_ladder.csv", index=False)
    print("\nThe over/under ladder (the law, dialled by the line):")
    print(lad.to_string(index=False))
    r_bucket = float(np.corrcoef(lad.skew_pred, lad.skew_real)[0, 1])
    max_cerr = float(lad.calib_err.abs().max())
    print(f"\n  corr(predicted, realised) across lines = {r_bucket:+.3f}")
    print(f"  max |model − realised over-rate| across all lines = {max_cerr:.3f}  "
          f"(odds-free model calibration)")

    anc = gl.anchor_25(df)
    print(f"\nO/U 2.5 anchor (the one line with real odds):")
    print(f"  p_over — model {anc['p_model']:.3f} | market {anc['p_market']:.3f} | "
          f"realised {anc['p_real']:.3f}  (overround {anc['overround']:.3f})")

    prov.write_stamp("53_goals_ladder", metrics={
        "n_fit": int(len(ml)),
        "corr_pred_real": round(r_bucket, 4),
        "skew_line05": round(float(lad.set_index("line").loc[0.5, "skew_pred"]), 4),
        "skew_line25": round(float(lad.set_index("line").loc[2.5, "skew_pred"]), 4),
        "skew_line45": round(float(lad.set_index("line").loc[4.5, "skew_pred"]), 4),
        "anchor_p_model": anc["p_model"], "anchor_p_market": anc["p_market"],
        "anchor_p_real": anc["p_real"],
    })


if __name__ == "__main__":
    main()
