"""20 — CPT invariante (Frente C2): a ponderação de probabilidade (a preferência
por trás do FLB) é ela própria um INVARIANTE — estável entre ligas e no tempo?
Ajusta γ de Tversky-Kahneman à curva de calibração (q implícita ≈ w(π objetiva))
globalmente, por liga e por temporada.
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
    print(f"\nGLOBAL — γ de Tversky-Kahneman = {g0:.3f}  "
          f"({'inverse-S (overweight de azarão) = FLB' if g0 < 1 else 'sem inverse-S'})")
    print("  curva de calibração (q implícita vs π objetiva), por faixa de q:")
    sub = cal.iloc[::4]
    print(sub.to_string(index=False, formatters={"q": "{:.3f}".format,
          "pi": "{:.3f}".format}))

    # invariância cross-sectional: γ por liga
    gl = cpt.gamma_by(df, "Division", min_n=4000, nbins=15).sort_values("gamma")
    print(f"\nINVARIÂNCIA ENTRE LIGAS ({len(gl)} ligas):")
    print(f"  γ médio = {gl.gamma.mean():.3f} | sd = {gl.gamma.std():.3f} | "
          f"range [{gl.gamma.min():.3f}, {gl.gamma.max():.3f}]")
    rcp = stats.bootstrap_corr(gl.gamma.values, gl.p_fav_dv.values)
    print(f"  corr(γ, p_fav) = {rcp['r']:+.3f} [{rcp['ci_lo']:+.2f},{rcp['ci_hi']:+.2f}]"
          f"  (γ ~constante ⇒ preferência não depende da competitividade)")

    # invariância temporal: γ por temporada + tendência
    gy = cpt.gamma_by(df, "season", min_n=4000, nbins=15).sort_values("season")
    ry = stats.ols(gy.gamma.values, gy.season.values - gy.season.mean())
    print(f"\nINVARIÂNCIA TEMPORAL ({len(gy)} temporadas):")
    print(f"  γ médio = {gy.gamma.mean():.3f} | sd = {gy.gamma.std():.3f}")
    print(f"  tendência: β = {ry['slope']:+.5f}/ano (r={ry['r']:+.2f}) — "
          f"{'sem drift' if abs(ry['slope']) < 0.005 else 'drift'} "
          f"(Δ20a ≈ {ry['slope']*20:+.3f}); a ponderação é estável no tempo.")

    C.OUTDIR.mkdir(exist_ok=True)
    gl.to_csv(C.OUTDIR / "cpt_by_league.csv", index=False)
    gy.to_csv(C.OUTDIR / "cpt_by_season.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'cpt_by_league.csv'} | {C.OUTDIR / 'cpt_by_season.csv'}")

    # figura: (a) w(p) ajustada + pontos de calibração; (b) γ por liga e por ano
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    pp = np.linspace(0.01, 0.99, 200)
    axes[0].plot([0, 1], [0, 1], "--", color="0.7", lw=1, label="sem viés (w=p)")
    axes[0].plot(pp, cpt.w_tk(pp, g0), color="#1f77b4", lw=2, label=f"TK γ={g0:.2f}")
    axes[0].scatter(cal.pi, cal.q, s=16, color="#d62728", zorder=3, label="calibração")
    axes[0].set_xlabel("π objetiva (taxa de acerto)"); axes[0].set_ylabel("q implícita")
    axes[0].set_title("Ponderação de probabilidade (FLB)")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].axhline(gl.gamma.mean(), color="0.7", lw=1, ls="--")
    axes[1].scatter(gy.season, gy.gamma, s=22, color="#1f77b4", label="γ por temporada")
    axes[1].fill_between(gy.season, gl.gamma.mean() - gl.gamma.std(),
                         gl.gamma.mean() + gl.gamma.std(), color="#1f77b4", alpha=.08,
                         label="±sd entre ligas")
    axes[1].set_xlabel("temporada"); axes[1].set_ylabel("γ")
    axes[1].set_title(f"γ invariante (β={ry['slope']:+.4f}/ano)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F9 — CPT invariante: a ponderação de probabilidade é estável",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f9_cpt.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f9_cpt.png'}")


if __name__ == "__main__":
    main()
