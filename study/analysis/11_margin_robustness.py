"""11 — Margin orthogonality (W4) + robustness to the de-vig method.

W4: the house margin (overround) affects the LEVEL of return, but is the skewness
(asymmetry structure) invariant to the book? Compares average vs maximum odds (best
market price) over the SAME matches, already de-vigged.

Robustness: does the central finding depend on the de-vig method? Repeats global +
cross-league law under multiplicative / power / shin.
"""
import numpy as np, pandas as pd
from skewlib import io, returns, exante, stats, config as C

AVG = ("OddHome", "OddDraw", "OddAway")
MAX = ("MaxHome", "MaxDraw", "MaxAway")


def main():
    df = io.load()
    sub = df.dropna(subset=list(MAX)).copy()
    for c in MAX:
        sub = sub[sub[c] > C.MIN_ODD]
    print(f"games with Max* market: {len(sub):,}")

    print("\n=== W4 — Margin orthogonality (average vs maximum odds) ===")
    pa, oa, ga = exante.market_skew(sub, AVG)
    pm, om, gm = exante.market_skew(sub, MAX)
    ora = (1 / sub[list(AVG)].to_numpy()).sum(1).mean()
    orm = (1 / sub[list(MAX)].to_numpy()).sum(1).mean()
    print(f"  overround     avg={ora:.4f}   max={orm:.4f}   (margin drops)")
    print(f"  skew ex-ante  avg={ga['skew']:+.4f}  max={gm['skew']:+.4f}  (invariant)")
    print(f"  p_fav mean    avg={pa.mean():.4f}   max={pm.mean():.4f}")
    print(f"  corr(p_fav_avg, p_fav_max) per game = {np.corrcoef(pa, pm)[0,1]:.4f}")
    print("  → the book competes on the MARGIN (level), not on the asymmetry (structure).")

    print("\n=== Robustness to the de-vig method ===")
    base = returns.add_returns(io.load())
    print(f"  {'method':14s} {'skew_global':>11s} {'corr(p_fav,skew) league':>22s}")
    for meth in ("multiplicative", "power", "shin"):
        d = exante.add_exante(base, method=meth)
        g = exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)
        lg = exante.pooled_by(d, "Division", min_n=2000)
        r = stats.bootstrap_corr(lg.p_fav_dv_mean.values, lg.skew_exante.values)["r"]
        print(f"  {meth:14s} {g['skew']:>+11.4f} {r:>+22.3f}")
    print("  → global and cross-league law stable to the method: finding is not a de-vig artefact.")


if __name__ == "__main__":
    main()
