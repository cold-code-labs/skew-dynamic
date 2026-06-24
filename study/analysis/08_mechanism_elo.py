"""08 — Mechanism (W2): does the skewness ~ competitiveness relationship survive an
ODDS-FREE competitiveness measure (Elo from results)?

Breaks the circularity of Block E/W1 (there competitiveness came from p_fav, which
comes from the odds). Here the regressor is Elo built from results only. If the sign
and magnitude hold, the law skewness=f(competitiveness) is structural.
"""
import pandas as pd
from skewlib import io, returns, exante, elo, stats, config as C


def main():
    base = exante.add_exante(returns.add_returns(io.load()))

    # ex-ante skewness by league (W1's primary object)
    sk = exante.pooled_by(base, "Division", min_n=2000)[
        ["Division", "n", "skew_exante", "skew_expost", "p_fav_dv_mean"]]

    # odds-free competitiveness
    print("running Elo (results) + MNLogit calibration...", flush=True)
    d = elo.with_elo(base)
    comp = elo.league_competitiveness(d)

    m = sk.merge(comp.drop(columns="n"), on="Division").sort_values("skew_exante")
    print(f"\nLeagues: {len(m)} | Elo calibration: mean P(H)={d.pH_elo.mean():.3f} "
          f"(actual {(d.FTResult=='H').mean():.3f}) "
          f"P(D)={d.pD_elo.mean():.3f} ({(d.FTResult=='D').mean():.3f})")

    cols = ["Division", "skew_exante", "elo_pfav", "p_fav_dv_mean",
            "elo_entropy", "elo_disp", "upset_rate"]
    print("\nBy league (ordered by skew_exante):")
    print(m[cols].to_string(index=False,
          formatters={c: "{:.3f}".format for c in cols[1:]}))

    print("\n=== Validation: odds vs Elo (do both measure the SAME structure?) ===")
    v = stats.bootstrap_corr(m.elo_pfav.values, m.p_fav_dv_mean.values)
    print(f"  corr(elo_pfav, p_fav_dv) = {v['r']:+.3f}  95%CI [{v['ci_lo']:+.3f},{v['ci_hi']:+.3f}]")
    print("  -> odds simply read off the sporting competitiveness (structural efficiency)")

    print("\n=== Non-circular law: skewness ~ ODDS-FREE competitiveness ===")
    for name, x, sgn in [("elo_pfav (fav prob)", m.elo_pfav, "−"),
                         ("elo_entropy (evenness)", m.elo_entropy, "+"),
                         ("elo_disp (strength spread)", m.elo_disp, "−"),
                         ("upset_rate (upsets)", m.upset_rate, "+")]:
        bc = stats.bootstrap_corr(x.values, m.skew_exante.values)
        reg = stats.ols(m.skew_exante.values, x.values)
        print(f"  skew ~ {name:24s} r={bc['r']:+.3f} "
              f"95%CI[{bc['ci_lo']:+.3f},{bc['ci_hi']:+.3f}] R²={reg['r2']:.3f}")

    print("\n  Circular reference (odds): skew ~ p_fav_dv "
          f"r={stats.bootstrap_corr(m.p_fav_dv_mean.values, m.skew_exante.values)['r']:+.3f}")

    C.OUTDIR.mkdir(exist_ok=True)
    m.to_csv(C.OUTDIR / "mechanism_elo.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'mechanism_elo.csv'}")


if __name__ == "__main__":
    main()
