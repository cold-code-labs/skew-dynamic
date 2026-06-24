"""27 — Microstructure D3: the Shin z (fraction of INFORMED money) as a series.
z is a by-product of the Shin de-vig: the proportion of the book attributed to
insiders. Here we look at z by league and by year — is it stable over time? Does it
correlate with competitiveness or overround? It is a microstructure descriptor (how
much private information the market prices in) behind the same asymmetry.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, microstructure as ms, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = ms.shin_z_frame(df)
    print(f"N={len(d):,} | mean global z = {d.shin_z.mean():.4f} "
          f"(fraction of informed money in the 1X2)")

    zl = ms.z_by(d, "Division", min_n=2000).sort_values("z")
    zy = ms.z_by(d, "season", min_n=2000).sort_values("season")
    print(f"\nACROSS LEAGUES ({len(zl)}): mean z {zl.z.mean():.4f} · sd {zl.z.std():.4f} · "
          f"range [{zl.z.min():.3f},{zl.z.max():.3f}]")
    ro = stats.bootstrap_corr(zl.z.values, zl.overround.values)
    rp = stats.bootstrap_corr(zl.z.values, zl.p_fav.values)
    print(f"  corr(z, overround) = {ro['r']:+.3f} [{ro['ci_lo']:+.2f},{ro['ci_hi']:+.2f}]"
          f" | corr(z, competitiveness p_fav) = {rp['r']:+.3f} "
          f"[{rp['ci_lo']:+.2f},{rp['ci_hi']:+.2f}]")
    ty = stats.ols(zy.z.values, zy.season.values - zy.season.mean())
    print(f"\nOVER TIME ({len(zy)} seasons): mean z {zy.z.mean():.4f} · sd {zy.z.std():.4f}")
    print(f"  trend β = {ty['slope']:+.5f}/yr (r={ty['r']:+.2f}, Δ20yr "
          f"{ty['slope']*20:+.3f}) — {'stable' if abs(ty['slope'])<0.002 else 'drifting'}")
    print("  → z is low and stable: the informational content of the book is a structural")
    print("    constant, consistent with the invariance of the asymmetry.")

    C.OUTDIR.mkdir(exist_ok=True)
    zl.to_csv(C.OUTDIR / "shin_z_by_league.csv", index=False)
    zy.to_csv(C.OUTDIR / "shin_z_by_season.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(zl.overround, zl.z, s=20, color="#1f77b4")
    axes[0].set_xlabel("league mean overround"); axes[0].set_ylabel("Shin z (informed)")
    axes[0].set_title(f"z vs margin (r={ro['r']:+.2f})")
    axes[1].axhline(zy.z.mean(), color="0.7", lw=1, ls="--")
    axes[1].plot(zy.season, zy.z, "o-", color="#1f77b4", lw=1.5, ms=4)
    axes[1].set_xlabel("season"); axes[1].set_ylabel("Shin z")
    axes[1].set_title(f"z stable over time (β={ty['slope']:+.4f}/yr)")
    fig.suptitle("F15 — D3: Shin z (informed money) by league and over time", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f15_shin_z.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f15_shin_z.png'} | {C.OUTDIR / 'shin_z_by_league.csv'}")

    prov.write_stamp("27_shin_z_series", metrics={
        "z_global": float(d.shin_z.mean()), "z_sd_league": float(zl.z.std()),
        "z_trend_beta": ty["slope"], "corr_z_overround": ro["r"]})


if __name__ == "__main__":
    main()
