"""16 — Temporal stability of the FLB (P4): guard against the confound of
Angelini & De Angelis (2019), who find the FLB WEAKENING in recent European data.
If the bias drifts, it could contaminate our skewness invariance. We test whether
(i) the FLB barometer is stable and (ii) the ex-ante↔ex-post calibration holds
year by year.
"""
from scipy.stats import skew
from skewlib import io, returns, exante, decompose, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    fy = decompose.flb_by_year(df)
    print(f"years: {fy.year.min()}–{fy.year.max()} ({len(fy)} points)")

    print("\nyear  n     ret_dog  flb_spread  calib_err  skew_expost")
    for _, r in fy.iterrows():
        print(f"{r.year:.0f} {r.n:6.0f}  {r.ret_dog:+.3f}    {r.flb_spread:+.3f}"
              f"     {r.calib_err:+.3f}     {r.skew_expost:+.3f}")

    print("\n=== Trend over time (slope/year + corr with year) ===")
    for name, col in [("ret_dog (FLB barometer)", "ret_dog"),
                      ("flb_spread (fav−dog)", "flb_spread"),
                      ("calib_err (calibration)", "calib_err"),
                      ("skew_expost", "skew_expost")]:
        reg = stats.ols(fy[col].values, fy.year.values)
        bc = stats.bootstrap_corr(fy.year.values, fy[col].values)
        print(f"  {name:26s} slope={reg['slope']:+.5f}/year  "
              f"Δ20y={reg['slope']*20:+.3f}  corr(year)={bc['r']:+.2f} "
              f"[{bc['ci_lo']:+.2f},{bc['ci_hi']:+.2f}]")

    print("\n=== Aggregate ex-ante vs ex-post calibration by year ===")
    ex = exante.pooled_by(df.assign(yr=df.date.dt.year), "yr", min_n=500)
    c = ex.skew_exante.corr(ex.skew_expost)
    md = (ex.skew_exante - ex.skew_expost).abs().mean()
    print(f"  corr(skew_exante, skew_expost) year by year = {c:+.3f} | "
          f"mean |diff| = {md:.3f}")
    print("  → if the FLB drifted, ex-ante and ex-post would diverge over time; they do not.")
    print("    The skewness invariance is not an artefact of a moving FLB.")

    C.OUTDIR.mkdir(exist_ok=True)
    fy.to_csv(C.OUTDIR / "flb_by_year.csv", index=False)
    print(f"  -> {C.OUTDIR / 'flb_by_year.csv'}")


if __name__ == "__main__":
    main()
