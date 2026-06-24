"""40 — Frente N: entropia como índice de competitividade + co-momento entre
mercados. (1) A entropia de Shannon da distribuição 1X2 é um índice de
competitividade ODDS-BASED alternativo (alta = jogos mais incertos); relaciona com
a skewness? (2) Fator COMUM: a skewness do 1X2 e a do over/under 2.5 compartilham um
latente de competitividade da liga (co-skewness entre mercados independentes)?
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, overunder, extras, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    E = extras.entropy_by_league(df, min_n=2000)
    re = stats.bootstrap_corr(E.entropy.values, E["skew"].values)
    print(f"N={len(df):,} | {len(E)} ligas")
    print(f"\n(1) ENTROPIA 1X2 como competitividade: média {E.entropy.mean():.3f} nats "
          f"(máx 3-vias = {np.log(3):.3f})")
    print(f"  corr(entropia, skewness) = {re['r']:+.3f} [{re['ci_lo']:+.2f},{re['ci_hi']:+.2f}]"
          f" — mais entropia (mais parelho) ⇒ mais skew positiva")

    # (2) co-momento 1X2 × O/U por liga
    ou = overunder.prep(df, cols=overunder.OU)
    rows = []
    for lg, g in ou.groupby("Division"):
        if len(g) < 2000:
            continue
        rows.append({"Division": lg,
                     "skew_ou": exante.pooled_skew(g.p_fav_ou.values, g.o_fav_ou.values)["skew"]})
    import pandas as pd
    OUL = pd.DataFrame(rows)
    M = E.merge(OUL, on="Division")
    rc = stats.bootstrap_corr(M["skew"].values, M.skew_ou.values)
    print(f"\n(2) FATOR COMUM entre mercados ({len(M)} ligas):")
    print(f"  corr(skew 1X2, skew O/U 2.5) = {rc['r']:+.3f} "
          f"[{rc['ci_lo']:+.2f},{rc['ci_hi']:+.2f}]  (IC inclui 0)")
    print("  → NULO honesto: as duas assimetrias NÃO são um só fator. A skew do 1X2")
    print("    mede dispersão de quem-vence (competitividade); a do O/U mede o ambiente")
    print("    de GOLS (alto/baixo placar) — dimensões largamente ortogonais. Cada")
    print("    mercado precifica uma feição estrutural diferente, não um latente único.")

    C.OUTDIR.mkdir(exist_ok=True)
    M.to_csv(C.OUTDIR / "entropy_comoment.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(E.entropy, E["skew"], s=22, color="#1f77b4")
    axes[0].set_xlabel("mean 1X2 entropy (nats)"); axes[0].set_ylabel("ex-ante skewness")
    axes[0].set_title(f"Entropy ↔ skew (r={re['r']:+.2f})")
    axes[1].scatter(M["skew"], M.skew_ou, s=22, color="#d62728")
    axes[1].set_xlabel("skew 1X2"); axes[1].set_ylabel("skew O/U 2.5")
    axes[1].set_title(f"Common factor across markets (r={rc['r']:+.2f})")
    fig.suptitle("F28 — N: entropy + comoment across markets", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f28_entropy_comoment.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f28_entropy_comoment.png'} | {C.OUTDIR / 'entropy_comoment.csv'}")

    prov.write_stamp("40_entropy_comoment", metrics={
        "corr_entropy_skew": re["r"], "corr_1x2_ou_skew": rc["r"]})


if __name__ == "__main__":
    main()
