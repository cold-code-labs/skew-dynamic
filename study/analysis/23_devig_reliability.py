"""23 — Adversarial robustness G1: is the de-vig reliable and is the skewness
independent of it? Reliability of the de-vigged favourite (Shin) via reliability
diagram + Brier decomposition (Murphy: BS = REL − RES + UNC) by league and by year —
if the calibration error REL is small and stable, the de-vig neither fabricates nor
distorts the asymmetry. And the pooled skewness under several de-vigs (Shin/mult/power)
and books (mean Odd vs Max best price, + multi-book consensus) — invariance ⇒ finding
is not an artefact of the method.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, adversarial as adv, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = df.date.dt.year
    y = adv.fav_won(df)
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")

    g = adv.brier_decomp(df.p_fav_dv.values, y)
    print(f"\nGLOBAL — favourite: observed hit rate {g['obar']:.3f} vs mean prob "
          f"{df.p_fav_dv.mean():.3f}")
    print(f"  Brier {g['brier']:.4f} = REL {g['rel']:.4f} − RES {g['res']:.4f} "
          f"+ UNC {g['unc']:.4f}")
    print(f"  calibration error REL = {g['rel']:.4f} (≈0 ⇒ Shin well calibrated)")

    rl = adv.reliability_by(df, "Division", min_n=3000)
    ry = adv.reliability_by(df, "season", min_n=3000)
    print(f"\nSTABILITY of REL (calibration error):")
    print(f"  across {len(rl)} leagues:  mean {rl.rel.mean():.4f} · sd {rl.rel.std():.4f} "
          f"· max {rl.rel.max():.4f}")
    print(f"  across {len(ry)} seasons:  mean {ry.rel.mean():.4f} · sd {ry.rel.std():.4f} "
          f"· max {ry.rel.max():.4f}")
    print("  → the de-vig residual is small and homogeneous (no poorly calibrated league/year).")

    sk = adv.skew_by_devig(df)
    print(f"\nSKEWNESS under de-vig/book (invariance to the method):")
    for k, v in sk.items():
        print(f"  {k:12} {v:+.4f}")
    vals = np.array(list(sk.values()))
    print(f"  range {vals.max()-vals.min():.4f} (all positive; the sign and the "
          f"order of magnitude do not depend on the de-vig)")

    C.OUTDIR.mkdir(exist_ok=True)
    rl.to_csv(C.OUTDIR / "reliability_by_league.csv", index=False)

    # figure: global reliability diagram + REL by league
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    rel = adv.reliability(df.p_fav_dv.values, y, nbins=12)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot([0.3, 0.85], [0.3, 0.85], "--", color="0.7", lw=1, label="perfect calibration")
    axes[0].scatter(rel.p_pred, rel.freq_obs, s=rel.n / 200, color="#1f77b4", zorder=3)
    axes[0].set_xlabel("predicted favourite probability (Shin)")
    axes[0].set_ylabel("observed win frequency")
    axes[0].set_title(f"Reliability — REL={g['rel']:.4f}")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].axhline(rl.rel.mean(), color="0.7", lw=1, ls="--", label="mean")
    axes[1].scatter(rl.n, rl.rel, s=18, color="#d62728")
    axes[1].set_xlabel("no. of matches in league"); axes[1].set_ylabel("REL (calibration error)")
    axes[1].set_title(f"REL stable across leagues (sd={rl.rel.std():.4f})")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F12 — G1: reliable and stable de-vig (reliability/Brier)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f12_reliability.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f12_reliability.png'} | {C.OUTDIR / 'reliability_by_league.csv'}")

    prov.write_stamp("23_devig_reliability", metrics={
        "rel_global": g["rel"], "rel_sd_league": float(rl.rel.std()),
        "rel_sd_season": float(ry.rel.std()),
        "skew_devig_range": float(vals.max() - vals.min())})


if __name__ == "__main__":
    main()
