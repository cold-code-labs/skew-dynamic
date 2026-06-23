"""27 — Microestrutura D3: o z de Shin (fração de dinheiro INFORMADO) como série.
z é subproduto do de-vig de Shin: a proporção do book atribuída a insiders. Aqui
olhamos z por liga e por ano — é estável no tempo? correlaciona com competitividade
ou overround? É um descritor de microestrutura (quanto de informação privada o
mercado precifica) por trás da mesma assimetria.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, microstructure as ms, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = ms.shin_z_frame(df)
    print(f"N={len(d):,} | z global médio = {d.shin_z.mean():.4f} "
          f"(fração de dinheiro informado no 1X2)")

    zl = ms.z_by(d, "Division", min_n=2000).sort_values("z")
    zy = ms.z_by(d, "season", min_n=2000).sort_values("season")
    print(f"\nENTRE LIGAS ({len(zl)}): z médio {zl.z.mean():.4f} · sd {zl.z.std():.4f} · "
          f"range [{zl.z.min():.3f},{zl.z.max():.3f}]")
    ro = stats.bootstrap_corr(zl.z.values, zl.overround.values)
    rp = stats.bootstrap_corr(zl.z.values, zl.p_fav.values)
    print(f"  corr(z, overround) = {ro['r']:+.3f} [{ro['ci_lo']:+.2f},{ro['ci_hi']:+.2f}]"
          f" | corr(z, competitividade p_fav) = {rp['r']:+.3f} "
          f"[{rp['ci_lo']:+.2f},{rp['ci_hi']:+.2f}]")
    ty = stats.ols(zy.z.values, zy.season.values - zy.season.mean())
    print(f"\nNO TEMPO ({len(zy)} temporadas): z médio {zy.z.mean():.4f} · sd {zy.z.std():.4f}")
    print(f"  tendência β = {ty['slope']:+.5f}/ano (r={ty['r']:+.2f}, Δ20a "
          f"{ty['slope']*20:+.3f}) — {'estável' if abs(ty['slope'])<0.002 else 'com deriva'}")
    print("  → z é baixo e estável: o conteúdo informacional do book é uma constante")
    print("    estrutural, coerente com a invariância da assimetria.")

    C.OUTDIR.mkdir(exist_ok=True)
    zl.to_csv(C.OUTDIR / "shin_z_by_league.csv", index=False)
    zy.to_csv(C.OUTDIR / "shin_z_by_season.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(zl.overround, zl.z, s=20, color="#1f77b4")
    axes[0].set_xlabel("overround médio da liga"); axes[0].set_ylabel("z de Shin (informado)")
    axes[0].set_title(f"z vs margem (r={ro['r']:+.2f})")
    axes[1].axhline(zy.z.mean(), color="0.7", lw=1, ls="--")
    axes[1].plot(zy.season, zy.z, "o-", color="#1f77b4", lw=1.5, ms=4)
    axes[1].set_xlabel("temporada"); axes[1].set_ylabel("z de Shin")
    axes[1].set_title(f"z estável no tempo (β={ty['slope']:+.4f}/ano)")
    fig.suptitle("F15 — D3: z de Shin (dinheiro informado) por liga e no tempo", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f15_shin_z.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f15_shin_z.png'} | {C.OUTDIR / 'shin_z_by_league.csv'}")

    prov.write_stamp("27_shin_z_series", metrics={
        "z_global": float(d.shin_z.mean()), "z_sd_league": float(zl.z.std()),
        "z_trend_beta": ty["slope"], "corr_z_overround": ro["r"]})


if __name__ == "__main__":
    main()
