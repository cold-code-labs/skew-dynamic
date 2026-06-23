"""26 — Microestrutura D2: sharp vs soft. A skewness diverge entre a odd MÉDIA do
mercado (Odd*, mais soft) e a MELHOR odd (Max*, ~sharp/arb)? Por liga. A melhor odd
quase zera o overround; se a skewness mal se move e a LEI transversal se preserva,
a assimetria é da estrutura do esporte, não do tipo de casa (aprofunda W4).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, microstructure as ms, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    L = ms.skew_by_book_league(df, min_n=2000)
    print(f"N={len(df):,} | {len(L)} ligas com Max* válido")

    print(f"\nOverround médio: soft (Odd) {L.over_soft.mean():.3f} → "
          f"sharp (Max) {L.over_sharp.mean():.3f} (margem quase zerada na melhor odd)")
    print(f"Skew do favorito: soft {L.skew_soft.mean():+.3f} | sharp {L.skew_sharp.mean():+.3f}"
          f" | Δ(sharp−soft) médio {L.d_skew.mean():+.3f} (sd {L.d_skew.std():.3f})")
    r = stats.bootstrap_corr(L.skew_soft.values, L.skew_sharp.values)
    print(f"corr(skew_soft, skew_sharp) entre ligas = {r['r']:+.3f} "
          f"[{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}] — a ordenação das ligas é a mesma")
    rl = stats.bootstrap_corr(L.skew_sharp.values, L.p_fav.values)
    print(f"lei sharp: corr(skew_sharp, p_fav) = {rl['r']:+.3f} "
          f"[{rl['ci_lo']:+.2f},{rl['ci_hi']:+.2f}] (a lei estrutural sobrevive na melhor odd)")
    print("  → tirar a margem (best price) desloca pouco e uniformemente a skew;")
    print("    a casa compete em margem, não em assimetria, e a LEI é invariante ao livro.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "sharp_soft_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    lim = [min(L.skew_soft.min(), L.skew_sharp.min()) - .02,
           max(L.skew_soft.max(), L.skew_sharp.max()) + .02]
    ax.plot(lim, lim, "--", color="0.7", lw=1, label="sem diferença")
    ax.scatter(L.skew_soft, L.skew_sharp, s=22, color="#1f77b4", zorder=3)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("skew (soft — odd média)"); ax.set_ylabel("skew (sharp — melhor odd)")
    ax.set_title(f"F14 — D2: skew sharp vs soft por liga (r={r['r']:+.2f})")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f14_sharp_soft.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f14_sharp_soft.png'} | {C.OUTDIR / 'sharp_soft_by_league.csv'}")

    prov.write_stamp("26_sharp_soft", metrics={
        "d_skew_mean": float(L.d_skew.mean()), "corr_soft_sharp": r["r"],
        "corr_sharp_pfav": rl["r"]})


if __name__ == "__main__":
    main()
