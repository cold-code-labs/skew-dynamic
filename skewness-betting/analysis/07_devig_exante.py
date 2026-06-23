"""07 — De-vigging + skewness ex-ante (W1): o objeto primário do estudo.

Constrói a skewness implícita (de-vigada) da aposta no favorito, decompõe-a
em termo mecânico (assimetria intra-jogo / FLB) vs dispersão entre jogos, e
confronta ex-ante × ex-post (realizada). A convergência ex-ante≈ex-post é um
teste de calibração das odds; a fração `within` quantifica quanto da skewness
de mercado é imagem algébrica da distribuição de p.
"""
import pandas as pd
from scipy.stats import skew
from skewlib import io, returns, exante, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD} | "
          f"overround médio={df.overround.mean():.4f}", end="")
    if "shin_z" in df:
        print(f" | Shin z médio={df.shin_z.mean():.4f} "
              f"(fração de dinheiro informado)")
    else:
        print()

    print("\nGLOBAL — ex-ante (mistura) vs ex-post (realizada):")
    g = exante.pooled_skew(df.p_fav_dv.values, df.o_fav.values)
    print(f"  skew ex-ante  = {g['skew']:+.4f}")
    print(f"  skew ex-post  = {skew(df.ret_fav):+.4f}  (realizada, favorito)")
    print(f"  decomposição de M3:")
    print(f"    mecânico (intra-jogo / FLB) = {g['within']:+.4e}  ({g['within_frac']:+.1%})")
    print(f"    covariância var×média       = {g['cov']:+.4e}  ({g['cov_frac']:+.1%})")
    print(f"    dispersão entre jogos       = {g['between']:+.4e}  ({g['between_frac']:+.1%})")

    print("\nPor faixa de p_fav (de-vigada) — calibração ex-ante×ex-post:")
    df["bucket"] = pd.cut(df.p_fav_dv, [0, .4, .45, .5, .55, .6, .7, 1.0])
    tab = exante.pooled_by(df, "bucket")
    print(tab[["bucket", "n", "p_fav_dv_mean", "skew_exante", "skew_expost",
               "within_frac"]].to_string(index=False))

    print("\nPor liga — skewness ex-ante (alimenta W2):")
    lg = exante.pooled_by(df, "Division", min_n=2000).sort_values("skew_exante")
    print(lg[["Division", "n", "p_fav_dv_mean", "skew_exante", "skew_expost"]]
          .to_string(index=False))
    print(f"\n  corr(skew_exante, skew_expost) entre ligas = "
          f"{lg.skew_exante.corr(lg.skew_expost):+.3f}")
    print(f"  corr(p_fav_dv_mean, skew_exante)           = "
          f"{lg.p_fav_dv_mean.corr(lg.skew_exante):+.3f}  (ainda circular: p vem das odds)")

    C.OUTDIR.mkdir(exist_ok=True)
    lg.to_csv(C.OUTDIR / "exante_by_league.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'exante_by_league.csv'}")


if __name__ == "__main__":
    main()
