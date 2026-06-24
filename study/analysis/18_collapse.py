"""18 — Colapso de distribuição (Frente B): a forma é universal, ou função da
competitividade? Dois testes complementares sobre o retorno do favorito:

  A) SEM controlar competitividade — retornos z-scored por liga, KS par-a-par.
     A forma difere entre ligas (a skew varia com a liga) ⇒ NÃO é universal.
  B) CONTROLANDO competitividade — dentro de cada faixa de p_fav, a distribuição
     do retorno é a mesma entre ligas? (one-vs-rest KS por faixa). Se o tamanho
     de efeito desaba vs (A), a identidade da liga não acrescenta nada além da
     competitividade ⇒ colapso ("fato estilizado": forma = f(competitividade)).

Com n enorme o p-valor do KS satura; o que vale é a ESTATÍSTICA KS (distância
máxima de CDF = tamanho de efeito).
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, collapse, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")

    # --- A: forma SEM controlar competitividade (z-score por liga) ---
    z = collapse.zscore_returns(df, col="ret_fav", by="Division", min_n=2000)
    A = collapse.pairwise_test(z, test="ks")
    print(f"\nA) retornos z-scored por liga ({len(z)} ligas) — KS par-a-par:")
    print(f"   estatística KS mediana (efeito) = {A['median_stat']:.4f}")
    print(f"   fração de pares que rejeita      = {A['reject_frac']:.1%} "
          f"(p-valor mediano {A['median_p']:.1e})")
    print("   → a forma padronizada DIFERE entre ligas: não é universal (a skew varia).")

    # --- B: condicional à competitividade (faixa de p_fav) ---
    tab, summ = collapse.conditional_invariance(
        df, pcol="p_fav_dv", retcol="ret_fav", by="Division", nbins=8, min_n=300)
    D_cond = float(tab.ks_stat.median())
    print(f"\nB) condicional à faixa de p_fav ({len(tab)} testes liga×faixa) — "
          f"one-vs-rest KS:")
    print(summ.to_string(index=False,
          formatters={"p_mid": "{:.3f}".format, "reject_frac": "{:.1%}".format,
                      "ks_stat_med": "{:.4f}".format}))
    print(f"\n   estatística KS mediana CONDICIONAL = {D_cond:.4f}")
    print(f"   vs incondicional (A)               = {A['median_stat']:.4f}  "
          f"→ queda de {(1 - D_cond / A['median_stat']):.0%}")
    print("   → controlada a competitividade, a distribuição colapsa entre ligas:")
    print("     a FORMA é função da competitividade, a liga não acrescenta nada.")

    C.OUTDIR.mkdir(exist_ok=True)
    out = summ.copy()
    out.loc[len(out)] = {"pbin": "UNCONDITIONAL", "p_mid": np.nan,
                         "n_leagues": len(z), "reject_frac": A["reject_frac"],
                         "ks_stat_med": A["median_stat"]}
    out.to_csv(C.OUTDIR / "collapse_ks.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'collapse_ks.csv'}")

    # --- figura: esquerda sem colapso (z-score full), direita com colapso (faixa) ---
    moms = pd.read_csv(C.OUTDIR / "moments_by_league.csv") if \
        (C.OUTDIR / "moments_by_league.csv").exists() else None
    # 3 ligas representativas: menor, mediana e maior p_fav (entre as grandes)
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
    axes[0].set_title("Sem controlar competitividade\n(retorno z-scored por liga)")
    axes[0].set_xlabel("retorno padronizado"); axes[0].set_ylabel("ECDF")
    axes[0].set_xlim(-2, 3); axes[0].legend(frameon=False, fontsize=8)

    # faixa central de p_fav: restringe as MESMAS ligas e plota retorno cru
    lo, hi = df.p_fav_dv.quantile([0.45, 0.55])
    band = df[(df.p_fav_dv >= lo) & (df.p_fav_dv <= hi)]
    for c, lg in cols.items():
        x = band[band.Division == lg].ret_fav.values
        if len(x) < 50:
            continue
        xs, F = collapse.ecdf(x)
        axes[1].step(xs, F, color=c, lw=1.5, label=lg)
    axes[1].set_title(f"Mesma faixa de competitividade\n(p_fav∈[{lo:.2f},{hi:.2f}], retorno cru)")
    axes[1].set_xlabel("retorno"); axes[1].set_ylabel("ECDF")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F7 — Colapso de distribuição: a forma é função da competitividade",
                 y=1.03)
    fig.tight_layout()
    fig.savefig(FIG / "f7_collapse.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f7_collapse.png'}")


if __name__ == "__main__":
    main()
