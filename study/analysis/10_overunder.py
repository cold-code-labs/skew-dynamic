"""10 — Binary over/under 2.5 market (W5): the cleanest test of the mechanical
identity. No draw → skewness is a function of a single p. Confirms that the W1
finding does not depend on the 3-way structure of 1X2.
"""
import numpy as np, pandas as pd
from scipy.stats import skew
from skewlib import io, overunder, exante, config as C


def main():
    df = io.load()
    d = overunder.prep(df)
    print(f"N={len(d):,} games with O/U 2.5 | mean overround={d.overround.mean():.4f} | "
          f"mean Shin z={d.shin_z.mean():.4f}")
    print(f"over rate (goals≥3) = {d.over.mean():.3f} | "
          f"mean de-vigged p_over = {d.p_over.mean():.3f} (calibration)")

    print("\nGLOBAL — favourite O/U bet: ex-ante vs ex-post:")
    g = exante.pooled_skew(d.p_fav_ou.values, d.o_fav_ou.values)
    print(f"  skew ex-ante = {g['skew']:+.4f}  | within(within-match) = {g['within_frac']:+.1%}")
    print(f"  skew ex-post = {skew(d.ret_fav_ou):+.4f}  (realised)")
    print(f"  mean favourite ret = {d.ret_fav_ou.mean():+.4f}")

    print("\nPure identity: skew ex-ante = (1-2p)/√(p(1-p)) per match")
    p = d.p_fav_ou.values
    ident = (1 - 2 * p) / np.sqrt(p * (1 - p))
    print(f"  per-match skew (formula) vs exante.per_match_skew: "
          f"max|diff| = {np.abs(ident - exante.per_match_skew(p)).max():.2e}")

    print("\nBy p bucket (favourite side) — ex-ante×ex-post:")
    d["bucket"] = pd.cut(d.p_fav_ou, [0.5, .55, .6, .65, .7, .8, 1.0])
    rows = []
    for b, gb in d.groupby("bucket", observed=True):
        if len(gb) < 200:
            continue
        ex = exante.pooled_skew(gb.p_fav_ou.values, gb.o_fav_ou.values)
        rows.append({"bucket": str(b), "n": len(gb), "p_mean": gb.p_fav_ou.mean(),
                     "skew_exante": ex["skew"], "skew_expost": skew(gb.ret_fav_ou),
                     "win_rate": (gb.ret_fav_ou > 0).mean()})
    print(pd.DataFrame(rows).to_string(index=False,
          formatters={c: "{:.3f}".format for c in ["p_mean", "skew_exante", "skew_expost", "win_rate"]}))

    print("\n→ O/U is binary, p~0.5 (few extreme goal counts), small skewness but "
          "governed by the SAME identity. within≈100% confirms the W1 core\n"
          "  outside the 1X2 structure.")

    C.OUTDIR.mkdir(exist_ok=True)
    d[["Division", "p_fav_ou", "o_fav_ou", "ret_fav_ou", "over"]].to_csv(
        C.OUTDIR / "overunder.csv", index=False)
    print(f"  -> {C.OUTDIR / 'overunder.csv'}")


if __name__ == "__main__":
    main()
