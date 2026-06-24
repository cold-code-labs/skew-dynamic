"""37 — Front K: diversification / portfolio. Skewness is a SINGLE-bet phenomenon.
The standardised skewness of the mean return of N (nearly) independent bets scales as
skew(X)/√N: a diversified bankroll of favourites (or of underdogs) tends to Gaussian,
even though the isolated bet is strongly asymmetric. Hence the preference for skewness
(the FLB) matters to the RECREATIONAL bettor (few bets), not to the syndicate — the
microeconomic channel that sustains the bias being EV-negative.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, portfolio as pf, provenance as prov, config as C

SIZES = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,}")

    base_f, rows_f = pf.skew_decay(df.ret_fav.values, SIZES)
    base_d, rows_d = pf.skew_decay(df.ret_dog.values, SIZES)
    print(f"\nSkewness of the SINGLE bet (realised): favourite {base_f:+.3f} · "
          f"underdog {base_d:+.3f} (underdog = lottery-like)")
    print(f"\nSkewness of the MEAN RETURN of N bets (iid scaling skew/√N):")
    print(f"  {'N':>5} {'fav skew':>9} {'(pred)':>8} {'dog skew':>9} {'(pred)':>8}")
    for rf, rd in zip(rows_f, rows_d):
        print(f"  {rf['N']:>5} {rf['skew']:>+9.3f} {rf['skew_pred']:>+8.3f} "
              f"{rd['skew']:>+9.3f} {rd['skew_pred']:>+8.3f}")
    ngf = pf.n_to_gaussian(base_f); ngd = pf.n_to_gaussian(base_d)
    print(f"\n  bets until skew<0.1 (~Gaussian): favourite ~{ngf} · underdog ~{ngd}")
    print("  → the asymmetry the bettor 'loves' belongs to the ISOLATED bet; diversifying")
    print("    kills it (1/√N). The FLB survives because the recreational bettor concentrates")
    print("    a few lottery-like bets — the diversified syndicate only sees the negative EV.")

    C.OUTDIR.mkdir(exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows_f).assign(bet="fav").to_csv(C.OUTDIR / "diversification.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    Ns = np.array(SIZES)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(Ns, [r["skew"] for r in rows_d], "o-", color="#d62728", lw=1.8, label="underdog (empirical)")
    ax.plot(Ns, [r["skew"] for r in rows_f], "o-", color="#1f77b4", lw=1.8, label="favourite (empirical)")
    ax.plot(Ns, base_d / np.sqrt(Ns), "--", color="#d62728", lw=1, alpha=.7, label="underdog skew/√N")
    ax.plot(Ns, base_f / np.sqrt(Ns), "--", color="#1f77b4", lw=1, alpha=.7, label="favourite skew/√N")
    ax.axhline(0, color="0.85", lw=.8); ax.axhline(0.1, color="0.7", lw=.6, ls=":")
    ax.set_xscale("log"); ax.set_xlabel("bets in the portfolio N (log)")
    ax.set_ylabel("skewness of the mean return")
    ax.set_title("F25 — K: diversification kills the skewness (≈1/√N)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f25_diversification.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f25_diversification.png'} | {C.OUTDIR / 'diversification.csv'}")

    prov.write_stamp("37_diversification", metrics={
        "skew_single_fav": base_f, "skew_single_dog": base_d,
        "skew_n100_fav": rows_f[6]["skew"], "n_to_gaussian_dog": ngd})


if __name__ == "__main__":
    main()
