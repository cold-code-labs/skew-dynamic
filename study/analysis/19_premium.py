"""19 — Prêmio de skewness (Frente C1): decompor o retorno esperado do favorito em
margem (vig) + nível FLB mecânico + resíduo, e perguntar se sobra um "prêmio" por
liga correlacionado com a SKEWNESS implícita, além do nível mecânico do FLB.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, premium, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")

    g = premium.decompose_global(df)
    print("\nGLOBAL — retorno do favorito = margem (vig) + FLB (calibração):")
    print(f"  ret médio   = {g['ret_mean']:+.4f}")
    print(f"  vig (margem)= {g['vig']:+.4f}   (perda à margem sob p de-vigada verdadeira)")
    print(f"  FLB         = {g['flb']:+.4f}   (favorito ganha mais que o implícito)")
    print(f"  check (≈0)  = {g['residual_check']:+.2e}")

    print("\nCurva mecânica do FLB (contribuição (1{win}−p_dv)·o por faixa de p_dv):")
    cur = premium.flb_curve(df, nbins=10)
    print(cur.to_string(index=False,
          formatters={"p": "{:.3f}".format, "flb": "{:+.4f}".format}))

    # por liga: vig + flb(sistemático+resíduo) + skewness implícita
    dec = premium.decompose_by_league(df, min_n=2000)
    sk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante"]]
    L = dec.merge(sk, on="Division").sort_values("residual")

    rr = stats.bootstrap_corr(L.residual.values, L.skew_exante.values)
    rf = stats.bootstrap_corr(L.flb.values, L.skew_exante.values)
    rv = stats.bootstrap_corr(L.vig.values, L.skew_exante.values)
    print(f"\nPor liga ({len(L)}) — corr com a skewness implícita (boot IC95):")
    print(f"  vig       ~ skew : r={rv['r']:+.3f} [{rv['ci_lo']:+.2f},{rv['ci_hi']:+.2f}]  "
          f"(margem ~ortogonal à assimetria)")
    print(f"  FLB total ~ skew : r={rf['r']:+.3f} [{rf['ci_lo']:+.2f},{rf['ci_hi']:+.2f}]  "
          f"(o FLB acompanha a skewness — o prêmio bruto)")
    print(f"  RESÍDUO   ~ skew : r={rr['r']:+.3f} [{rr['ci_lo']:+.2f},{rr['ci_hi']:+.2f}]  "
          f"(prêmio ALÉM do nível mecânico)")
    print("\n  extremos por resíduo:")
    print(L[["Division", "p_fav_dv", "vig", "flb", "flb_syst", "residual",
             "skew_exante"]].head(4).to_string(index=False))
    print(L[["Division", "p_fav_dv", "vig", "flb", "flb_syst", "residual",
             "skew_exante"]].tail(4).to_string(index=False))

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "return_decomp.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'return_decomp.csv'}")

    # figura: (a) curva FLB por p; (b) FLB total vs skew com resíduo destacado
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    cur2 = premium.flb_curve(df, nbins=20)
    axes[0].axhline(0, color="0.8", lw=1)
    axes[0].plot(cur2.p, cur2.flb, "o-", color="#1f77b4", ms=4)
    axes[0].set_xlabel("de-vigged $p_{fav}$"); axes[0].set_ylabel("FLB contribution ·o")
    axes[0].set_title("Mechanical FLB curve")
    axes[1].scatter(L.skew_exante, L.flb, s=22, color="#1f77b4", label="total FLB")
    axes[1].scatter(L.skew_exante, L.residual, s=22, color="#d62728", label="residual")
    axes[1].axhline(0, color="0.8", lw=1)
    axes[1].set_xlabel("league implied skewness"); axes[1].set_ylabel("return")
    axes[1].set_title(f"total FLB (r={rf['r']:+.2f}) vs residual (r={rr['r']:+.2f})")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F8 — Skewness premium: FLB tracks skewness; the residual is small",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f8_premium.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f8_premium.png'}")


if __name__ == "__main__":
    main()
