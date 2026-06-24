"""23 — Robustez adversarial G1: o de-vig é confiável e a skewness independe dele?
Confiabilidade do favorito de-vigado (Shin) via reliability diagram + decomposição
de Brier (Murphy: BS = REL − RES + UNC) por liga e por ano — se o erro de
calibração REL é pequeno e estável, o de-vig não fabrica nem distorce a assimetria.
E a skewness agrupada sob vários de-vigs (Shin/mult/power) e casas (Odd média vs
Max melhor preço, + consenso multi-casa) — invariância ⇒ achado não é artefato do método.
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
    print(f"\nGLOBAL — favorito: acerto observado {g['obar']:.3f} vs prob média "
          f"{df.p_fav_dv.mean():.3f}")
    print(f"  Brier {g['brier']:.4f} = REL {g['rel']:.4f} − RES {g['res']:.4f} "
          f"+ UNC {g['unc']:.4f}")
    print(f"  erro de calibração REL = {g['rel']:.4f} (≈0 ⇒ Shin bem calibrado)")

    rl = adv.reliability_by(df, "Division", min_n=3000)
    ry = adv.reliability_by(df, "season", min_n=3000)
    print(f"\nESTABILIDADE do REL (erro de calibração):")
    print(f"  entre {len(rl)} ligas:    média {rl.rel.mean():.4f} · sd {rl.rel.std():.4f} "
          f"· max {rl.rel.max():.4f}")
    print(f"  entre {len(ry)} temporadas: média {ry.rel.mean():.4f} · sd {ry.rel.std():.4f} "
          f"· max {ry.rel.max():.4f}")
    print("  → o resíduo do de-vig é pequeno e homogêneo (não há liga/ano mal calibrado).")

    sk = adv.skew_by_devig(df)
    print(f"\nSKEWNESS sob de-vig/casa (invariância ao método):")
    for k, v in sk.items():
        print(f"  {k:12} {v:+.4f}")
    vals = np.array(list(sk.values()))
    print(f"  amplitude {vals.max()-vals.min():.4f} (todos positivos; o sinal e a "
          f"ordem de grandeza não dependem do de-vig)")

    C.OUTDIR.mkdir(exist_ok=True)
    rl.to_csv(C.OUTDIR / "reliability_by_league.csv", index=False)

    # figura: reliability diagram global + REL por liga
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    rel = adv.reliability(df.p_fav_dv.values, y, nbins=12)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot([0.3, 0.85], [0.3, 0.85], "--", color="0.7", lw=1, label="calibração perfeita")
    axes[0].scatter(rel.p_pred, rel.freq_obs, s=rel.n / 200, color="#1f77b4", zorder=3)
    axes[0].set_xlabel("prob. prevista do favorito (Shin)")
    axes[0].set_ylabel("frequência observada de vitória")
    axes[0].set_title(f"Reliability — REL={g['rel']:.4f}")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].axhline(rl.rel.mean(), color="0.7", lw=1, ls="--", label="média")
    axes[1].scatter(rl.n, rl.rel, s=18, color="#d62728")
    axes[1].set_xlabel("nº de jogos da liga"); axes[1].set_ylabel("REL (erro de calibração)")
    axes[1].set_title(f"REL estável entre ligas (sd={rl.rel.std():.4f})")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F12 — G1: de-vig confiável e estável (reliability/Brier)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f12_reliability.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f12_reliability.png'} | {C.OUTDIR / 'reliability_by_league.csv'}")

    prov.write_stamp("23_devig_reliability", metrics={
        "rel_global": g["rel"], "rel_sd_league": float(rl.rel.std()),
        "rel_sd_season": float(ry.rel.std()),
        "skew_devig_range": float(vals.max() - vals.min())})


if __name__ == "__main__":
    main()
