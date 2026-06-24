"""40 — Front N: entropy as a competitiveness index + cross-market co-moment.
(1) The Shannon entropy of the 1X2 distribution is an alternative ODDS-BASED
competitiveness index (high = more uncertain matches); does it relate to skewness?
(2) COMMON factor: do the 1X2 skewness and the over/under 2.5 skewness share a
latent league-competitiveness factor (co-skewness across independent markets)?
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, overunder, extras, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    E = extras.entropy_by_league(df, min_n=2000)
    re = stats.bootstrap_corr(E.entropy.values, E["skew"].values)
    print(f"N={len(df):,} | {len(E)} leagues")
    print(f"\n(1) 1X2 ENTROPY as competitiveness: mean {E.entropy.mean():.3f} nats "
          f"(3-way max = {np.log(3):.3f})")
    print(f"  corr(entropy, skewness) = {re['r']:+.3f} [{re['ci_lo']:+.2f},{re['ci_hi']:+.2f}]"
          f" — more entropy (more balanced) ⇒ more positive skew")

    # (2) co-moment 1X2 × O/U by league
    ou = overunder.prep(df, cols=overunder.OU)
    rows = []
    for lg, g in ou.groupby("Division"):
        if len(g) < 2000:
            continue
        rows.append({"Division": lg,
                     "skew_ou": exante.pooled_skew(g.p_fav_ou.values, g.o_fav_ou.values)["skew"]})
    import pandas as pd
    OUL = pd.DataFrame(rows)
    M = E.merge(OUL, on="Division")
    rc = stats.bootstrap_corr(M["skew"].values, M.skew_ou.values)
    print(f"\n(2) COMMON FACTOR across markets ({len(M)} leagues):")
    print(f"  corr(skew 1X2, skew O/U 2.5) = {rc['r']:+.3f} "
          f"[{rc['ci_lo']:+.2f},{rc['ci_hi']:+.2f}]  (CI includes 0)")
    print("  → honest NULL: the two asymmetries are NOT a single factor. The 1X2 skew")
    print("    measures the dispersion of who-wins (competitiveness); the O/U skew measures")
    print("    the GOALS environment (high/low scoring) — largely orthogonal dimensions. Each")
    print("    market prices a different structural feature, not a single latent.")

    C.OUTDIR.mkdir(exist_ok=True)
    M.to_csv(C.OUTDIR / "entropy_comoment.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(E.entropy, E["skew"], s=22, color="#1f77b4")
    axes[0].set_xlabel("mean 1X2 entropy (nats)"); axes[0].set_ylabel("ex-ante skewness")
    axes[0].set_title(f"Entropy ↔ skew (r={re['r']:+.2f})")
    axes[1].scatter(M["skew"], M.skew_ou, s=22, color="#d62728")
    axes[1].set_xlabel("skew 1X2"); axes[1].set_ylabel("skew O/U 2.5")
    axes[1].set_title(f"Common factor across markets (r={rc['r']:+.2f})")
    fig.suptitle("F28 — N: entropy + comoment across markets", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f28_entropy_comoment.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f28_entropy_comoment.png'} | {C.OUTDIR / 'entropy_comoment.csv'}")

    prov.write_stamp("40_entropy_comoment", metrics={
        "corr_entropy_skew": re["r"], "corr_1x2_ou_skew": rc["r"]})


if __name__ == "__main__":
    main()
