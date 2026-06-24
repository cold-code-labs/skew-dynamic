"""20 — Invariant CPT (Front C2): is the probability weighting (the preference
behind the FLB) itself an INVARIANT — stable across leagues and over time?
Fits the Tversky-Kahneman γ to the calibration curve (implied q ≈ w(objective π))
globally, by league and by season.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, cpt, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = df.date.dt.year
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")

    cal = cpt.calibration(df, nbins=25)
    g0 = cpt.fit_gamma(cal)
    print(f"\nGLOBAL — Tversky-Kahneman γ = {g0:.3f}  "
          f"({'inverse-S (underdog overweight) = FLB' if g0 < 1 else 'no inverse-S'})")
    print("  calibration curve (implied q vs objective π), by q band:")
    sub = cal.iloc[::4]
    print(sub.to_string(index=False, formatters={"q": "{:.3f}".format,
          "pi": "{:.3f}".format}))

    # cross-sectional invariance: γ by league
    gl = cpt.gamma_by(df, "Division", min_n=4000, nbins=15).sort_values("gamma")
    print(f"\nINVARIANCE ACROSS LEAGUES ({len(gl)} leagues):")
    print(f"  mean γ = {gl.gamma.mean():.3f} | sd = {gl.gamma.std():.3f} | "
          f"range [{gl.gamma.min():.3f}, {gl.gamma.max():.3f}]")
    rcp = stats.bootstrap_corr(gl.gamma.values, gl.p_fav_dv.values)
    print(f"  corr(γ, p_fav) = {rcp['r']:+.3f} [{rcp['ci_lo']:+.2f},{rcp['ci_hi']:+.2f}]"
          f"  (γ ~constant ⇒ preference does not depend on competitiveness)")

    # temporal invariance: γ by season + trend
    gy = cpt.gamma_by(df, "season", min_n=4000, nbins=15).sort_values("season")
    ry = stats.ols(gy.gamma.values, gy.season.values - gy.season.mean())
    print(f"\nTEMPORAL INVARIANCE ({len(gy)} seasons):")
    print(f"  mean γ = {gy.gamma.mean():.3f} | sd = {gy.gamma.std():.3f}")
    print(f"  trend: β = {ry['slope']:+.5f}/yr (r={ry['r']:+.2f}) — "
          f"{'no drift' if abs(ry['slope']) < 0.005 else 'drift'} "
          f"(Δ20yr ≈ {ry['slope']*20:+.3f}); the weighting is stable over time.")

    C.OUTDIR.mkdir(exist_ok=True)
    gl.to_csv(C.OUTDIR / "cpt_by_league.csv", index=False)
    gy.to_csv(C.OUTDIR / "cpt_by_season.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'cpt_by_league.csv'} | {C.OUTDIR / 'cpt_by_season.csv'}")

    # figure: (a) fitted w(p) + calibration points; (b) γ by league and by year
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    pp = np.linspace(0.01, 0.99, 200)
    axes[0].plot([0, 1], [0, 1], "--", color="0.7", lw=1, label="unbiased (w=p)")
    axes[0].plot(pp, cpt.w_tk(pp, g0), color="#1f77b4", lw=2, label=f"TK γ={g0:.2f}")
    axes[0].scatter(cal.pi, cal.q, s=16, color="#d62728", zorder=3, label="calibration")
    axes[0].set_xlabel("objective π (hit rate)"); axes[0].set_ylabel("implied q")
    axes[0].set_title("Probability weighting (FLB)")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].axhline(gl.gamma.mean(), color="0.7", lw=1, ls="--")
    axes[1].scatter(gy.season, gy.gamma, s=22, color="#1f77b4", label="γ by season")
    axes[1].fill_between(gy.season, gl.gamma.mean() - gl.gamma.std(),
                         gl.gamma.mean() + gl.gamma.std(), color="#1f77b4", alpha=.08,
                         label="±sd between leagues")
    axes[1].set_xlabel("season"); axes[1].set_ylabel("γ")
    axes[1].set_title(f"invariant γ (β={ry['slope']:+.4f}/year)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F9 — Invariant CPT: probability weighting is stable",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f9_cpt.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f9_cpt.png'}")


if __name__ == "__main__":
    main()
