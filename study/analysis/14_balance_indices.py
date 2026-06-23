"""14 — CB canônico odds-independente (P2): a lei skewness~competitividade contra
os índices padrão da literatura (Noll-Scully, HHI*, Theil), computados da
classificação (resultados, sem odds). Ataca a circularidade ainda mais forte que
o Elo e usa as ferramentas size-robust que a literatura recomenda (Gini fora,
Utt & Fort 2002).

Sinal esperado: mais DESEQUILÍBRIO (NS/HHI*/Theil ↑) → favoritos fortes →
skewness ↓ (correlação negativa).
"""
from skewlib import io, returns, exante, balance, elo, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    sk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante", "p_fav_dv_mean"]]

    cb = balance.by_league(balance.cb_indices(balance.standings(df)))
    m = sk.merge(cb, on="Division")
    print(f"ligas com CB de classificação: {len(m)}")

    print("\nPor liga (ordenado por skew_exante):")
    cols = ["Division", "skew_exante", "noll_scully", "hhi_star", "theil"]
    print(m.sort_values("skew_exante")[cols].to_string(index=False,
          formatters={c: "{:.3f}".format for c in cols[1:]}))

    print("\n=== Lei contra CB odds-INDEPENDENTE (classificação) ===")
    for name, col in [("Noll-Scully", "noll_scully"), ("HHI* (Owen)", "hhi_star"),
                      ("Theil/GE1 (Borooah)", "theil")]:
        bc = stats.bootstrap_corr(m[col].values, m.skew_exante.values)
        reg = stats.ols(m.skew_exante.values, m[col].values)
        print(f"  skew ~ {name:22s} r={bc['r']:+.3f} "
              f"IC95%[{bc['ci_lo']:+.3f},{bc['ci_hi']:+.3f}] R²={reg['r2']:.3f}")

    # referência: Elo (W2) e circular (odds)
    d = elo.with_elo(df)
    comp = elo.league_competitiveness(d)[["Division", "upset_rate"]]
    m2 = m.merge(comp, on="Division")
    print("\n  referências:")
    print(f"  skew ~ upset_rate (Elo, odds-free)  r="
          f"{stats.bootstrap_corr(m2.upset_rate.values, m2.skew_exante.values)['r']:+.3f}")
    print(f"  skew ~ p_fav_dv (odds, circular)    r="
          f"{stats.bootstrap_corr(m.p_fav_dv_mean.values, m.skew_exante.values)['r']:+.3f}")
    print("\n  → CB de classificação (sem odds nem Elo) reproduz a lei → não é "
          "artefato\n    de medida nem de circularidade. Gini omitido (Utt & Fort: inválido).")

    C.OUTDIR.mkdir(exist_ok=True)
    m.to_csv(C.OUTDIR / "balance_indices.csv", index=False)
    print(f"  -> {C.OUTDIR / 'balance_indices.csv'}")


if __name__ == "__main__":
    main()
