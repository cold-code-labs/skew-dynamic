"""08 — Mecanismo (W2): a relação skewness ~ competitividade sobrevive a uma
medida de competitividade ODDS-FREE (Elo de resultados)?

Quebra a circularidade do Bloco E/W1 (lá a competitividade vinha de p_fav, que
vem das odds). Aqui o regressor é Elo construído só de resultados. Se o sinal
e a magnitude se mantiverem, a lei skewness=f(competitividade) é estrutural.
"""
import pandas as pd
from skewlib import io, returns, exante, elo, stats, config as C


def main():
    base = exante.add_exante(returns.add_returns(io.load()))

    # skewness ex-ante por liga (objeto primário do W1)
    sk = exante.pooled_by(base, "Division", min_n=2000)[
        ["Division", "n", "skew_exante", "skew_expost", "p_fav_dv_mean"]]

    # competitividade odds-free
    print("rodando Elo (resultados) + calibração MNLogit...", flush=True)
    d = elo.with_elo(base)
    comp = elo.league_competitiveness(d)

    m = sk.merge(comp.drop(columns="n"), on="Division").sort_values("skew_exante")
    print(f"\nLigas: {len(m)} | calibração Elo: P(H) médio={d.pH_elo.mean():.3f} "
          f"(real {(d.FTResult=='H').mean():.3f}) "
          f"P(D)={d.pD_elo.mean():.3f} ({(d.FTResult=='D').mean():.3f})")

    cols = ["Division", "skew_exante", "elo_pfav", "p_fav_dv_mean",
            "elo_entropy", "elo_disp", "upset_rate"]
    print("\nPor liga (ordenado por skew_exante):")
    print(m[cols].to_string(index=False,
          formatters={c: "{:.3f}".format for c in cols[1:]}))

    print("\n=== Validação: odds vs Elo (ambos medem a MESMA estrutura?) ===")
    v = stats.bootstrap_corr(m.elo_pfav.values, m.p_fav_dv_mean.values)
    print(f"  corr(elo_pfav, p_fav_dv) = {v['r']:+.3f}  IC95% [{v['ci_lo']:+.3f},{v['ci_hi']:+.3f}]")
    print("  -> odds só leem a competitividade esportiva (eficiência estrutural)")

    print("\n=== Lei não-circular: skewness ~ competitividade ODDS-FREE ===")
    for name, x, sgn in [("elo_pfav (prob fav)", m.elo_pfav, "−"),
                         ("elo_entropy (parelha)", m.elo_entropy, "+"),
                         ("elo_disp (spread força)", m.elo_disp, "−"),
                         ("upset_rate (zebras)", m.upset_rate, "+")]:
        bc = stats.bootstrap_corr(x.values, m.skew_exante.values)
        reg = stats.ols(m.skew_exante.values, x.values)
        print(f"  skew ~ {name:24s} r={bc['r']:+.3f} "
              f"IC95%[{bc['ci_lo']:+.3f},{bc['ci_hi']:+.3f}] R²={reg['r2']:.3f}")

    print("\n  Referência circular (odds): skew ~ p_fav_dv "
          f"r={stats.bootstrap_corr(m.p_fav_dv_mean.values, m.skew_exante.values)['r']:+.3f}")

    C.OUTDIR.mkdir(exist_ok=True)
    m.to_csv(C.OUTDIR / "mechanism_elo.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'mechanism_elo.csv'}")


if __name__ == "__main__":
    main()
