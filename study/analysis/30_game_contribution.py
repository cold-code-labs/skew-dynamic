"""30 — Micro F2: que JOGOS carregam a skewness da liga? Decompõe o 3º momento
agrupado por faixa de competitividade do jogo (p_fav). Torna explícito o
"cancelamento de caudas": jogos de favorito FRACO (p≈0.5) contribuem skew positiva,
de favorito FORTE (p alto) skew negativa — a competitividade no nível do JOGO
determina a contribuição de skew do jogo.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, intraleague as il, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    tab, tot = il.m3_contribution_by_bin(df)
    print(f"N={len(df):,} | M₃ agrupado total = {tot:.1f}")
    print("\nContribuição ao 3º momento por faixa de competitividade do jogo (p_fav):")
    print(f"  {'faixa':16} {'n':>8} {'p_mid':>7} {'skew_jogo':>10} {'share M₃':>9}")
    for r in tab.itertuples():
        print(f"  {r.bin:16} {r.n:>8,} {r.p_mid:>7.3f} {r.skew_match:>+10.3f} "
              f"{r.m3_share:>+9.1%}")
    pos = tab[tab.skew_match > 0].m3_share.sum()
    neg = tab[tab.skew_match < 0].m3_share.sum()
    print(f"\n  jogos de favorito FRACO (p<0.5) somam {pos:+.0%} do M₃; "
          f"favorito FORTE (p>0.5) {neg:+.0%}")
    print("  → a skew da liga é a soma líquida: a competitividade do JOGO fixa o")
    print("    sinal e a magnitude da contribuição de cada jogo (lei no nível micro).")

    C.OUTDIR.mkdir(exist_ok=True)
    tab.to_csv(C.OUTDIR / "m3_contribution_by_bin.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ["#2ca02c" if s > 0 else "#d62728" for s in tab.skew_match]
    ax.bar(range(len(tab)), tab.m3_share * 100, color=colors, alpha=.85)
    ax.axhline(0, color="0.5", lw=.8)
    ax.set_xticks(range(len(tab)))
    ax.set_xticklabels([f"{r.p_mid:.2f}" for r in tab.itertuples()])
    ax.set_xlabel("p_fav médio da faixa (competitividade do jogo)")
    ax.set_ylabel("contribuição ao M₃ (%)")
    ax.set_title("F18 — F2: jogos parelhos (verde) puxam +skew, desequilibrados (vermelho) −")
    fig.tight_layout()
    fig.savefig(FIG / "f18_game_contribution.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f18_game_contribution.png'} | {C.OUTDIR / 'm3_contribution_by_bin.csv'}")

    prov.write_stamp("30_game_contribution", metrics={
        "share_weak_fav": float(pos), "share_strong_fav": float(neg)})


if __name__ == "__main__":
    main()
