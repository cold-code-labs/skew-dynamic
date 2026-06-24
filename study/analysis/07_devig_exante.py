"""07 — De-vigging + ex-ante skewness (W1): the study's primary object.

Builds the implied (de-vigged) skewness of the favourite bet, decomposes it into
a mechanical term (within-match asymmetry / FLB) vs between-match dispersion, and
contrasts ex-ante × ex-post (realised). The ex-ante≈ex-post convergence is a
calibration test of the odds; the `within` fraction quantifies how much of the
market skewness is the algebraic image of the distribution of p.
"""
import pandas as pd
from scipy.stats import skew
from skewlib import io, returns, exante, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD} | "
          f"mean overround={df.overround.mean():.4f}", end="")
    if "shin_z" in df:
        print(f" | mean Shin z={df.shin_z.mean():.4f} "
              f"(fraction of informed money)")
    else:
        print()

    print("\nGLOBAL — ex-ante (mixture) vs ex-post (realised):")
    g = exante.pooled_skew(df.p_fav_dv.values, df.o_fav.values)
    print(f"  skew ex-ante  = {g['skew']:+.4f}")
    print(f"  skew ex-post  = {skew(df.ret_fav):+.4f}  (realised, favourite)")
    print(f"  decomposition of M3:")
    print(f"    mechanical (within-match / FLB) = {g['within']:+.4e}  ({g['within_frac']:+.1%})")
    print(f"    covariance var×mean             = {g['cov']:+.4e}  ({g['cov_frac']:+.1%})")
    print(f"    between-match dispersion        = {g['between']:+.4e}  ({g['between_frac']:+.1%})")

    print("\nBy p_fav bucket (de-vigged) — ex-ante×ex-post calibration:")
    df["bucket"] = pd.cut(df.p_fav_dv, [0, .4, .45, .5, .55, .6, .7, 1.0])
    tab = exante.pooled_by(df, "bucket")
    print(tab[["bucket", "n", "p_fav_dv_mean", "skew_exante", "skew_expost",
               "within_frac"]].to_string(index=False))

    print("\nBy league — ex-ante skewness (feeds W2):")
    lg = exante.pooled_by(df, "Division", min_n=2000).sort_values("skew_exante")
    print(lg[["Division", "n", "p_fav_dv_mean", "skew_exante", "skew_expost"]]
          .to_string(index=False))
    print(f"\n  corr(skew_exante, skew_expost) across leagues = "
          f"{lg.skew_exante.corr(lg.skew_expost):+.3f}")
    print(f"  corr(p_fav_dv_mean, skew_exante)              = "
          f"{lg.p_fav_dv_mean.corr(lg.skew_exante):+.3f}  (still circular: p comes from the odds)")

    C.OUTDIR.mkdir(exist_ok=True)
    lg.to_csv(C.OUTDIR / "exante_by_league.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'exante_by_league.csv'}")


if __name__ == "__main__":
    main()
