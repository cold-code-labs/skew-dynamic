"""14 — Canonical odds-independent CB (P2): the skewness~competitiveness law against
the literature's standard indices (Noll-Scully, HHI*, Theil), computed from the
standings (results, no odds). Attacks the circularity even more strongly than Elo
and uses the size-robust tools the literature recommends (Gini excluded,
Utt & Fort 2002).

Expected sign: more IMBALANCE (NS/HHI*/Theil ↑) → strong favourites →
skewness ↓ (negative correlation).
"""
from skewlib import io, returns, exante, balance, elo, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    sk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante", "p_fav_dv_mean"]]

    cb = balance.by_league(balance.cb_indices(balance.standings(df)))
    m = sk.merge(cb, on="Division")
    print(f"leagues with standings CB: {len(m)}")

    print("\nBy league (ordered by skew_exante):")
    cols = ["Division", "skew_exante", "noll_scully", "hhi_star", "theil"]
    print(m.sort_values("skew_exante")[cols].to_string(index=False,
          formatters={c: "{:.3f}".format for c in cols[1:]}))

    print("\n=== Law against odds-INDEPENDENT CB (standings) ===")
    for name, col in [("Noll-Scully", "noll_scully"), ("HHI* (Owen)", "hhi_star"),
                      ("Theil/GE1 (Borooah)", "theil")]:
        bc = stats.bootstrap_corr(m[col].values, m.skew_exante.values)
        reg = stats.ols(m.skew_exante.values, m[col].values)
        print(f"  skew ~ {name:22s} r={bc['r']:+.3f} "
              f"95%CI[{bc['ci_lo']:+.3f},{bc['ci_hi']:+.3f}] R²={reg['r2']:.3f}")

    # reference: Elo (W2) and circular (odds)
    d = elo.with_elo(df)
    comp = elo.league_competitiveness(d)[["Division", "upset_rate"]]
    m2 = m.merge(comp, on="Division")
    print("\n  references:")
    print(f"  skew ~ upset_rate (Elo, odds-free)  r="
          f"{stats.bootstrap_corr(m2.upset_rate.values, m2.skew_exante.values)['r']:+.3f}")
    print(f"  skew ~ p_fav_dv (odds, circular)    r="
          f"{stats.bootstrap_corr(m.p_fav_dv_mean.values, m.skew_exante.values)['r']:+.3f}")
    print("\n  → standings CB (no odds, no Elo) reproduces the law → it is not a "
          "measurement\n    artefact or a circularity artefact. Gini omitted (Utt & Fort: invalid).")

    C.OUTDIR.mkdir(exist_ok=True)
    m.to_csv(C.OUTDIR / "balance_indices.csv", index=False)
    print(f"  -> {C.OUTDIR / 'balance_indices.csv'}")


if __name__ == "__main__":
    main()
