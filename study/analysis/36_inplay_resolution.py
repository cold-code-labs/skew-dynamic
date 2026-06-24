"""36 — Frente J: chegada de informação (HT→FT). O placar do intervalo atualiza a
prob de vitória do favorito pré-jogo; a skewness do "resto do jogo" é de novo a
identidade (1−2q)/√(q(1−q)) na prob condicional q. Mostra que (i) o núcleo mecânico
é DINÂMICO (vale a cada estado de info) e (ii) a assimetria se RESOLVE com o placar:
favorito à frente ⇒ q alto ⇒ skew negativa; atrás ⇒ q baixo ⇒ skew positiva.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, inplay, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = inplay.fav_state(df)
    print(f"N(HT válido)={len(d):,} de {len(df):,} | favorito pré-jogo, estado no intervalo")

    sk0 = exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)["skew"]
    print(f"\nPRÉ-JOGO: p_fav {d.p0.mean():.3f} | skew agrupada {sk0:+.3f}")

    tab = inplay.conditional_table(d)
    print("\nESTADO DO FAVORITO NO INTERVALO → prob condicional e skewness do resto do jogo:")
    print(f"  {'estado':12} {'share':>7} {'q (vit.)':>9} {'skew resto':>11} {'n':>8}")
    for r in tab.itertuples():
        print(f"  {r.state:12} {r.share:>7.1%} {r.q_cond:>9.3f} {r.skew_cond:>+11.3f} {r.n:>8,}")
    print("  → a assimetria RESOLVE: à frente a aposta vira skew NEGATIVA (favorito")
    print("    quase ganhou), atrás vira POSITIVA (vira lotérica) — a identidade")
    print("    mecânica vale DINAMICAMENTE, não só no apito inicial.")

    mc = inplay.martingale_check(d)
    print("\nCALIBRAÇÃO DINÂMICA (E[q do HT | faixa de p0] ≈ p0 — refinamento martingale):")
    for r in mc.itertuples():
        print(f"  {r.p_bin:14} p0 {r.p0_mean:.3f} → q médio FT {r.q_mean:.3f} (n={r.n:,})")
    err = float(np.mean(np.abs(mc.p0_mean - mc.q_mean)))
    print(f"  erro médio |p0 − q| = {err:.4f} (≈0 ⇒ a prob pré-jogo é bem calibrada e")
    print("    o HT a refina sem viés: skewness implícita coerente em todo estado de info.)")

    C.OUTDIR.mkdir(exist_ok=True)
    tab.to_csv(C.OUTDIR / "inplay_conditional.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    pp = np.linspace(0.05, 0.95, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(pp, exante.per_match_skew(pp), color="0.5", lw=2,
                 label="identidade (1−2q)/√(q(1−q))")
    axes[0].axhline(0, color="0.85", lw=.8); axes[0].axvline(0.5, color="0.85", lw=.8)
    cols = {"atrás": "#2ca02c", "empatado": "#1f77b4", "+1": "#ff7f0e", "+2 ou mais": "#d62728"}
    for r in tab.itertuples():
        axes[0].scatter([r.q_cond], [r.skew_cond], s=90, color=cols.get(r.state, "#333"),
                        zorder=4, label=f"HT {r.state}")
    axes[0].set_xlabel("q = P(favorito vence | estado HT)")
    axes[0].set_ylabel("skewness do resto do jogo")
    axes[0].set_title("A assimetria resolve com a info"); axes[0].legend(frameon=False, fontsize=7)
    axes[1].plot([0.4, 0.75], [0.4, 0.75], "--", color="0.7", lw=1, label="calibração")
    axes[1].scatter(mc.p0_mean, mc.q_mean, s=40, color="#1f77b4", zorder=3)
    axes[1].set_xlabel("p0 pré-jogo (média da faixa)"); axes[1].set_ylabel("q médio no FT")
    axes[1].set_title(f"Refinamento martingale (|Δ|={err:.3f})"); axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F24 — J: o núcleo mecânico é dinâmico (HT→FT)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f24_inplay.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f24_inplay.png'} | {C.OUTDIR / 'inplay_conditional.csv'}")

    prov.write_stamp("36_inplay_resolution", metrics={
        "skew_pregame": sk0, "skew_behind": float(tab[tab.state == "atrás"].skew_cond.iloc[0]),
        "skew_ahead2": float(tab[tab.state == "+2 ou mais"].skew_cond.iloc[0]),
        "martingale_err": err})


if __name__ == "__main__":
    main()
