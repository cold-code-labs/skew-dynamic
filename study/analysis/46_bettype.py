"""46 — tipo de aposta: a assimetria dos TRÊS objetos (favorito/empate/azarão).

O estudo mediu a skewness da aposta no FAVORITO e mostrou que ela é governada pela
competitividade (a lei). E os outros lados do mesmo jogo? Para cada partida há três
objetos de dois pontos: favorito (argmax p), empate (resultado D) e azarão (argmin p).
Este bloco mede a skewness ex-ante AGRUPADA dos três por liga e pergunta:

  • Todos são positivamente assimétricos? (o FLB é um fenômeno de aposta única)
  • A LEI skew=f(competitividade) vale para os três, ou só para o favorito?

Achado: os três são fortemente lotéricos (skew>0) e os TRÊS são governados pela
competitividade — em sentidos opostos. Menos balanço (p_fav alto) baixa a skew do
FAVORITO (corr −0.90) e ELEVA a do empate e do azarão (corr +0.95 / +0.91), que
viram longshots maiores. Não é uma lei do favorito: é a MESMA lei estrutural em
todo lado do book, espelhada pela competitividade.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,}", flush=True)

    # global: skew ex-ante de cada objeto de aposta (pooled, odds de mercado)
    sel = exante.fav_dog_draw(df)
    glob = {k: exante.pooled_skew(p, o)["skew"] for k, (p, o) in sel.items()}
    print("\nSkewness ex-ante GLOBAL por objeto de aposta (pooled, odds de mercado):")
    for k in ("fav", "draw", "dog"):
        print(f"   {k:>4}: {glob[k]:+.3f}")

    # por liga + correlação de cada tipo com a competitividade (média de p_fav)
    bt = exante.bettype_by(df, min_n=2000).sort_values("p_fav_mean")
    comp = bt.p_fav_mean.values
    corr = {k: float(np.corrcoef(bt[f"skew_{k}"].values, comp)[0, 1])
            for k in ("fav", "draw", "dog")}
    print(f"\nPor liga ({len(bt)} ligas) — corr(skew, competitividade=média p_fav):")
    for k in ("fav", "draw", "dog"):
        sd = float(bt[f"skew_{k}"].std())
        print(f"   {k:>4}: corr={corr[k]:+.2f}  | sd entre-ligas={sd:.3f}")
    print("   → a competitividade governa os TRÊS: baixa a skew do favorito e eleva a do")
    print("     empate/azarão (longshots maiores) — a mesma lei, espelhada, em todo o book.")

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    bt.to_csv(C.OUTDIR / "bettype_by_league.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    colors = {"fav": "#1f77b4", "draw": "#7f7f7f", "dog": "#d62728"}
    names = {"fav": "favourite", "draw": "draw", "dog": "underdog"}
    for k in ("dog", "draw", "fav"):
        ax.scatter(comp, bt[f"skew_{k}"].values, s=22, color=colors[k],
                   alpha=.7, label=f"{names[k]} (corr {corr[k]:+.2f})")
    ax.axhline(0, color="0.85", lw=.8)
    ax.set_xlabel("league competitiveness (mean favourite probability)")
    ax.set_ylabel("ex-ante skewness of the bet")
    ax.set_title("F34 — three bet objects: all lottery-like, all governed by\n"
                 "competitiveness (favourite falls, draw & underdog rise)")
    ax.legend(frameon=False, fontsize=9); fig.tight_layout()
    fig.savefig(FIG / "f34_bettype.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f34_bettype.png'} | {C.OUTDIR / 'bettype_by_league.csv'}")

    prov.write_stamp("46_bettype", metrics={
        "skew_fav": glob["fav"], "skew_draw": glob["draw"], "skew_dog": glob["dog"],
        "corr_fav_comp": corr["fav"], "corr_draw_comp": corr["draw"],
        "corr_dog_comp": corr["dog"], "n_leagues": int(len(bt))})


if __name__ == "__main__":
    main()
