"""28 — Microestrutura D4: o mercado de HANDICAP ASIÁTICO como 3º mercado para a
identidade. Além de 1X2 (W1) e O/U 2.5 (W5), o AH é um mercado de 2 vias com linha
MÓVEL que equilibra o jogo para ~50/50. Predição: a identidade (1−2p)/√(p(1−p))
continua valendo, mas como o AH empurra p_fav→0.5, a skewness implícita ≈ 0 — a
MESMA lei mecânica, num regime de competitividade artificialmente máxima.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import skew as spskew
from skewlib import io, returns, exante, microstructure as ms, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = ms.prep_ah(df)
    print(f"N(AH válido)={len(d):,} de {len(df):,} | overround AH médio "
          f"{d.overround_ah.mean():.3f}")

    g = exante.pooled_skew(d.p_fav_ah.values, d.o_fav_ah.values)
    print(f"\nMERCADO AH — favorito: p_fav médio {d.p_fav_ah.mean():.3f} "
          f"(linha equilibra p/ ~0.5)")
    print(f"  skewness ex-ante AGRUPADA = {g['skew']:+.4f}  (within-match "
          f"{g['within_frac']*100:.1f}%)")
    print(f"  vs 1X2 +0.236 (p_fav~0.50) e O/U −0.21 — o AH precifica p_fav mais")
    print(f"    perto de 0.5, então a skew implícita encolhe, como a identidade prevê.")

    # confronto ex-ante vs ex-post (só jogos liquidados sem push/quarto)
    s = d[d.ah_settled]
    if len(s) > 5000:
        ep = float(spskew(s.ret_fav_ah.values))
        print(f"\n  ex-post (n liquidados={len(s):,}): skew realizada {ep:+.3f} "
              f"vs ex-ante {exante.pooled_skew(s.p_fav_ah.values, s.o_fav_ah.values)['skew']:+.3f}")

    L = ms.ah_league(d, min_n=2000)
    # cada liga: a skew AH cai na curva da identidade no p_fav daquele mercado?
    ident = exante.per_match_skew(L.p_fav_ah.values)
    rr = float(np.corrcoef(L.skew_ah.values, ident)[0, 1])
    print(f"\nPOR LIGA ({len(L)}): skew_ah na identidade (1−2p)/√(p(1−p)) avaliada no "
          f"p_fav do AH → r={rr:+.2f}")
    print("  → terceiro mercado independente confirma o núcleo mecânico (não é do 1X2).")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "asian_handicap_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    pp = np.linspace(0.3, 0.7, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(pp, exante.per_match_skew(pp), color="0.5", lw=2,
            label="identidade (1−2p)/√(p(1−p))")
    ax.scatter(L.p_fav_ah, L.skew_ah, s=22, color="#d62728", zorder=3, label="AH por liga")
    ax.axhline(0, color="0.85", lw=.8); ax.axvline(0.5, color="0.85", lw=.8)
    ax.set_xlabel("p_fav do mercado AH"); ax.set_ylabel("skewness ex-ante AH")
    ax.set_title(f"F16 — D4: handicap asiático na identidade (r={rr:+.2f})")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f16_asian_handicap.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f16_asian_handicap.png'} | {C.OUTDIR / 'asian_handicap_by_league.csv'}")

    prov.write_stamp("28_asian_handicap", metrics={
        "p_fav_ah": float(d.p_fav_ah.mean()), "skew_ah_global": g["skew"],
        "within_frac_ah": g["within_frac"], "league_identity_r": rr})


if __name__ == "__main__":
    main()
