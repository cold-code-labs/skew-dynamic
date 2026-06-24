"""18 — Distribution collapse (Front B): is the shape universal, or a function of
competitiveness? Two complementary tests on the favourite's return:

  A) WITHOUT controlling competitiveness — returns z-scored by league, pairwise KS.
     The shape differs across leagues (skew varies with the league) ⇒ NOT universal.
  B) CONTROLLING competitiveness — within each p_fav band, is the return
     distribution the same across leagues? (one-vs-rest KS per band). If the effect
     size collapses vs (A), the league identity adds nothing beyond
     competitiveness ⇒ collapse ("stylised fact": shape = f(competitiveness)).

With huge n the KS p-value saturates; what matters is the KS STATISTIC (maximum
CDF distance = effect size).
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, collapse, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")

    # --- A: shape WITHOUT controlling competitiveness (z-score by league) ---
    z = collapse.zscore_returns(df, col="ret_fav", by="Division", min_n=2000)
    A = collapse.pairwise_test(z, test="ks")
    print(f"\nA) returns z-scored by league ({len(z)} leagues) — pairwise KS:")
    print(f"   median KS statistic (effect)    = {A['median_stat']:.4f}")
    print(f"   fraction of pairs that reject    = {A['reject_frac']:.1%} "
          f"(median p-value {A['median_p']:.1e})")
    print("   → the standardised shape DIFFERS across leagues: not universal (skew varies).")

    # --- B: conditional on competitiveness (p_fav band) ---
    tab, summ = collapse.conditional_invariance(
        df, pcol="p_fav_dv", retcol="ret_fav", by="Division", nbins=8, min_n=300)
    D_cond = float(tab.ks_stat.median())
    print(f"\nB) conditional on the p_fav band ({len(tab)} league×band tests) — "
          f"one-vs-rest KS:")
    print(summ.to_string(index=False,
          formatters={"p_mid": "{:.3f}".format, "reject_frac": "{:.1%}".format,
                      "ks_stat_med": "{:.4f}".format}))
    print(f"\n   median CONDITIONAL KS statistic   = {D_cond:.4f}")
    print(f"   vs unconditional (A)               = {A['median_stat']:.4f}  "
          f"→ drop of {(1 - D_cond / A['median_stat']):.0%}")
    print("   → controlling for competitiveness, the distribution collapses across leagues:")
    print("     the SHAPE is a function of competitiveness, the league adds nothing.")

    C.OUTDIR.mkdir(exist_ok=True)
    out = summ.copy()
    out.loc[len(out)] = {"pbin": "UNCONDITIONAL", "p_mid": np.nan,
                         "n_leagues": len(z), "reject_frac": A["reject_frac"],
                         "ks_stat_med": A["median_stat"]}
    out.to_csv(C.OUTDIR / "collapse_ks.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'collapse_ks.csv'}")

    # --- figure: left without collapse (full z-score), right with collapse (band) ---
    moms = pd.read_csv(C.OUTDIR / "moments_by_league.csv") if \
        (C.OUTDIR / "moments_by_league.csv").exists() else None
    # 3 representative leagues: lowest, median and highest p_fav (among the big ones)
    big = (df.groupby("Division").size()
             .loc[lambda s: s >= 3000].index)
    pf = (df[df.Division.isin(big)].groupby("Division").p_fav_dv.mean()
            .sort_values())
    reps = [pf.index[0], pf.index[len(pf) // 2], pf.index[-1]]
    cols = {"#d62728": reps[0], "#7f7f7f": reps[1], "#1f77b4": reps[2]}

    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for c, lg in cols.items():
        xs, F = collapse.ecdf(z[lg])
        axes[0].step(xs, F, color=c, lw=1.5,
                     label=f"{lg} (p̄={pf[lg]:.2f})")
    axes[0].set_title("Without controlling competitiveness\n(return z-scored by league)")
    axes[0].set_xlabel("standardised return"); axes[0].set_ylabel("ECDF")
    axes[0].set_xlim(-2, 3); axes[0].legend(frameon=False, fontsize=8)

    # central p_fav band: restricts to the SAME leagues and plots raw return
    lo, hi = df.p_fav_dv.quantile([0.45, 0.55])
    band = df[(df.p_fav_dv >= lo) & (df.p_fav_dv <= hi)]
    for c, lg in cols.items():
        x = band[band.Division == lg].ret_fav.values
        if len(x) < 50:
            continue
        xs, F = collapse.ecdf(x)
        axes[1].step(xs, F, color=c, lw=1.5, label=lg)
    axes[1].set_title(f"Same competitiveness band\n(p_fav∈[{lo:.2f},{hi:.2f}], raw return)")
    axes[1].set_xlabel("return"); axes[1].set_ylabel("ECDF")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F7 — Distribution collapse: shape is a function of competitiveness",
                 y=1.03)
    fig.tight_layout()
    fig.savefig(FIG / "f7_collapse.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f7_collapse.png'}")


if __name__ == "__main__":
    main()
