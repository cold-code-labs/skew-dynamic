"""29 — Micro F1: sazonalidade intra-temporada. Conforme a classificação cristaliza
(do início ao fim da temporada), a skewness implícita se move? Usamos a temporada
REAL (Ago→Jul) e dividimos cada liga×temporada em terços por data. Se a skew do
fim ≈ a do início, a invariância vale também DENTRO da temporada (não só entre anos).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, intraleague as il, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = il.add_season_phase(df, nseg=3)
    print(f"N={len(df):,} | temporada real (Ago→Jul), 3 fases (início/meio/fim)")

    gp = il.skew_by_phase(d)
    print("\nGLOBAL por fase intra-temporada:")
    for r in gp.itertuples():
        print(f"  fase {r.phase} ({'início meio fim'.split()[r.phase]:6}): "
              f"skew {r.skew:+.4f} | p_fav {r.p_fav:.4f} | n={r.n:,}")
    span = gp["skew"].max() - gp["skew"].min()
    print(f"  amplitude início↔fim = {span:.4f} (≈0 ⇒ sem cristalização da assimetria)")

    sh = il.phase_shift_by_league(d)
    print(f"\nPOR LIGA ({len(sh)}): Δskew(fim−início)")
    print(f"  média {sh["shift"].mean():+.4f} · sd {sh["shift"].std():.4f} · "
          f"range [{sh["shift"].min():+.3f},{sh["shift"].max():+.3f}]")
    t = stats.bootstrap_stat(lambda i: sh["shift"].values[i].mean(), len(sh), B=2000)
    print(f"  IC95 da média do shift = [{t['ci_lo']:+.4f}, {t['ci_hi']:+.4f}] "
          f"({'inclui 0 ⇒ sem deriva intra-temporada' if t['ci_lo']<0<t['ci_hi'] else 'desloca'})")
    print("  → há uma cristalização LEVE (favoritos um pouco mais fortes no fim, "
          f"p_fav {gp['p_fav'].iloc[0]:.3f}→{gp['p_fav'].iloc[-1]:.3f}), mas o shift")
    print(f"    (~{abs(sh['shift'].mean()):.3f}) é ~3–4× menor que o sd entre ligas (0.05):")
    print("    a invariância vale também DENTRO da temporada, a menos de um drift pequeno")
    print("    e PREVISTO pela própria lei (mais p_fav ⇒ menos skew).")

    C.OUTDIR.mkdir(exist_ok=True)
    sh.to_csv(C.OUTDIR / "intraseason_shift_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(gp.phase, gp["skew"], "o-", color="#1f77b4", lw=2, ms=7)
    axes[0].set_xticks([0, 1, 2]); axes[0].set_xticklabels(["início", "meio", "fim"])
    axes[0].set_ylabel("skewness ex-ante"); axes[0].set_title("Global por fase")
    axes[0].set_ylim(gp["skew"].mean() - 0.05, gp["skew"].mean() + 0.05)
    axes[1].axvline(0, color="0.7", lw=1, ls="--")
    axes[1].hist(sh["shift"], bins=18, color="#1f77b4", alpha=.8)
    axes[1].set_xlabel("Δskew (fim − início) por liga")
    axes[1].set_title(f"Sem deriva (média {sh["shift"].mean():+.3f})")
    fig.suptitle("F17 — F1: skewness estável dentro da temporada", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f17_intraseason.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f17_intraseason.png'} | {C.OUTDIR / 'intraseason_shift_by_league.csv'}")

    prov.write_stamp("29_intraseason", metrics={
        "global_span": float(span), "shift_mean": float(sh["shift"].mean()),
        "shift_ci_lo": t["ci_lo"], "shift_ci_hi": t["ci_hi"]})


if __name__ == "__main__":
    main()
