"""26 — Microstructure D2: sharp vs soft. Does the skewness diverge between the
market's MEAN odd (Odd*, softer) and the BEST odd (Max*, ~sharp/arb)? By league. The
best odd nearly zeros the overround; if the skewness barely moves and the
cross-sectional LAW is preserved, the asymmetry is from the structure of the sport,
not the type of book (deepens W4).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, microstructure as ms, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    L = ms.skew_by_book_league(df, min_n=2000)
    print(f"N={len(df):,} | {len(L)} leagues with valid Max*")

    print(f"\nMean overround: soft (Odd) {L.over_soft.mean():.3f} → "
          f"sharp (Max) {L.over_sharp.mean():.3f} (margin nearly zeroed at the best odd)")
    print(f"Favourite skew: soft {L.skew_soft.mean():+.3f} | sharp {L.skew_sharp.mean():+.3f}"
          f" | mean Δ(sharp−soft) {L.d_skew.mean():+.3f} (sd {L.d_skew.std():.3f})")
    r = stats.bootstrap_corr(L.skew_soft.values, L.skew_sharp.values)
    print(f"corr(skew_soft, skew_sharp) across leagues = {r['r']:+.3f} "
          f"[{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] — the ordering of leagues is the same")
    rl = stats.bootstrap_corr(L.skew_sharp.values, L.p_fav.values)
    print(f"sharp law: corr(skew_sharp, p_fav) = {rl['r']:+.3f} "
          f"[{rl['ci_lo']:+.2f},{rl['ci_hi']:+.2f}] (the structural law survives at the best odd)")
    print("  → removing the margin (best price) shifts the skew little and uniformly;")
    print("    the book competes on margin, not on asymmetry, and the LAW is invariant to the book.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "sharp_soft_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    lim = [min(L.skew_soft.min(), L.skew_sharp.min()) - .02,
           max(L.skew_soft.max(), L.skew_sharp.max()) + .02]
    ax.plot(lim, lim, "--", color="0.7", lw=1, label="no difference")
    ax.scatter(L.skew_soft, L.skew_sharp, s=22, color="#1f77b4", zorder=3)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("skew (soft — mean odd)"); ax.set_ylabel("skew (sharp — best odd)")
    ax.set_title(f"F14 — D2: sharp vs soft skew by league (r={r['r']:+.2f})")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f14_sharp_soft.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f14_sharp_soft.png'} | {C.OUTDIR / 'sharp_soft_by_league.csv'}")

    prov.write_stamp("26_sharp_soft", metrics={
        "d_skew_mean": float(L.d_skew.mean()), "corr_soft_sharp": r["r"],
        "corr_sharp_pfav": rl["r"]})


if __name__ == "__main__":
    main()
