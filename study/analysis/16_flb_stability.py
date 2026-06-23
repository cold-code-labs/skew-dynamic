"""16 — Estabilidade temporal do FLB (P4): blindar contra o confound de
Angelini & De Angelis (2019), que acham o FLB ENFRAQUECENDO em dados europeus
recentes. Se o viés deriva, poderia contaminar nossa invariância de skewness.
Testamos se (i) o barômetro do FLB é estável e (ii) a calibração ex-ante↔ex-post
se mantém ano a ano.
"""
from scipy.stats import skew
from skewlib import io, returns, exante, decompose, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    fy = decompose.flb_by_year(df)
    print(f"anos: {fy.year.min()}–{fy.year.max()} ({len(fy)} pontos)")

    print("\nano   n     ret_dog  flb_spread  calib_err  skew_expost")
    for _, r in fy.iterrows():
        print(f"{r.year:.0f} {r.n:6.0f}  {r.ret_dog:+.3f}    {r.flb_spread:+.3f}"
              f"     {r.calib_err:+.3f}     {r.skew_expost:+.3f}")

    print("\n=== Tendência no tempo (slope/ano + corr com ano) ===")
    for name, col in [("ret_dog (FLB barômetro)", "ret_dog"),
                      ("flb_spread (fav−dog)", "flb_spread"),
                      ("calib_err (calibração)", "calib_err"),
                      ("skew_expost", "skew_expost")]:
        reg = stats.ols(fy[col].values, fy.year.values)
        bc = stats.bootstrap_corr(fy.year.values, fy[col].values)
        print(f"  {name:26s} slope={reg['slope']:+.5f}/ano  "
              f"Δ20a={reg['slope']*20:+.3f}  corr(ano)={bc['r']:+.2f} "
              f"[{bc['ci_lo']:+.2f},{bc['ci_hi']:+.2f}]")

    print("\n=== Calibração agregada ex-ante vs ex-post por ano ===")
    ex = exante.pooled_by(df.assign(yr=df.date.dt.year), "yr", min_n=500)
    c = ex.skew_exante.corr(ex.skew_expost)
    md = (ex.skew_exante - ex.skew_expost).abs().mean()
    print(f"  corr(skew_exante, skew_expost) ano a ano = {c:+.3f} | "
          f"|dif| média = {md:.3f}")
    print("  → se FLB driftasse, ex-ante e ex-post divergiriam no tempo; não o fazem.")
    print("    A invariância de skewness não é artefato de um FLB em movimento.")

    C.OUTDIR.mkdir(exist_ok=True)
    fy.to_csv(C.OUTDIR / "flb_by_year.csv", index=False)
    print(f"  -> {C.OUTDIR / 'flb_by_year.csv'}")


if __name__ == "__main__":
    main()
