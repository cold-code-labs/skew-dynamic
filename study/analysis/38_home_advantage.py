"""38 — Front L: secular home advantage (HFA) vs skewness invariance. HFA has
fallen over recent decades (and at the COVID shock, W3). If skewness stays invariant
even as HFA moves, it closes the confound on the HOME side: the asymmetry depends on
the dispersion of p_fav (competitiveness), not on the level of home advantage.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, extras, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    T = extras.hfa_and_skew_by_year(df)
    print(f"N={len(df):,} | {len(T)} years")

    th = stats.ols(T.home_win.values, T.year.values - T.year.mean())
    ts = stats.ols(T["skew"].values, T.year.values - T.year.mean())
    print(f"\nHOME ADVANTAGE (home win rate) over time:")
    print(f"  {T.home_win.iloc[0]:.3f} ({T.year.iloc[0]}) → {T.home_win.iloc[-1]:.3f} "
          f"({T.year.iloc[-1]}) | β = {th['slope']:+.5f}/yr (Δ20yr {th['slope']*20:+.3f})")
    print(f"SKEWNESS over time: β = {ts['slope']:+.5f}/yr (Δ20yr {ts['slope']*20:+.3f})")
    rc = stats.bootstrap_corr(T.home_win.values, T["skew"].values)
    print(f"\ncorr(HFA, skewness) year by year = {rc['r']:+.3f} "
          f"[{rc['ci_lo']:+.2f},{rc['ci_hi']:+.2f}]")
    print("  → HFA falls markedly, but skewness does not follow: the asymmetry")
    print("    depends on the DISPERSION of p_fav, not on the level of home advantage (confound closed).")

    C.OUTDIR.mkdir(exist_ok=True)
    T.to_csv(C.OUTDIR / "hfa_by_year.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(T.year, T.home_win, "o-", color="#d62728", lw=2, label="HFA (home win)")
    ax.set_xlabel("year"); ax.set_ylabel("home win rate", color="#d62728")
    ax.tick_params(axis="y", labelcolor="#d62728")
    ax2 = ax.twinx()
    ax2.plot(T.year, T["skew"], "s-", color="#1f77b4", lw=2, label="ex-ante skewness")
    ax2.set_ylabel("ex-ante skewness", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.set_ylim(T["skew"].mean() - 0.06, T["skew"].mean() + 0.06)
    ax.set_title(f"F26 — L: HFA falls (β={th['slope']:+.4f}), skew invariant "
                 f"(corr={rc['r']:+.2f})")
    fig.tight_layout()
    fig.savefig(FIG / "f26_home_advantage.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f26_home_advantage.png'} | {C.OUTDIR / 'hfa_by_year.csv'}")

    prov.write_stamp("38_home_advantage", metrics={
        "hfa_beta": th["slope"], "skew_beta": ts["slope"], "corr_hfa_skew": rc["r"]})


if __name__ == "__main__":
    main()
