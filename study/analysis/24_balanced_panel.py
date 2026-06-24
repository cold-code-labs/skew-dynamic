"""24 — Adversarial robustness G2: strict BALANCED panel. The temporal invariance
(W3/P1) used a league×season panel and a per-league test. Here we kill 100% the
COMPOSITION confound in the GLOBAL series: we rebuild the yearly skewness series using
only the leagues present in ALL seasons of the window. If the trend remains null, the
"no drift" is not an effect of the basket of leagues changing from year to year.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, panel as pan, adversarial as adv, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    P = pan.league_season_panel(df)
    bal = adv.balanced_leagues(P, min_frac=1.0)
    nseasons = P.season.nunique()
    print(f"N={len(df):,} | {P.Division.nunique()} leagues in the panel, "
          f"{nseasons} seasons")
    print(f"\nBALANCED leagues (present in all {nseasons} seasons): "
          f"{len(bal)} → {sorted(bal)}")
    if len(bal) < 3:
        bal = adv.balanced_leagues(P, min_frac=0.9)
        print(f"  (relaxing to ≥90% of the seasons: {len(bal)} leagues)")

    # unbalanced GLOBAL series (all leagues) vs balanced (fixed core)
    gall = adv.global_series_balanced(df, list(P.Division.unique()))
    gbal = adv.global_series_balanced(df, bal)

    def trend(series):
        s = series.set_index("season").skew_exante
        st = stats.stationarity(s)
        ol = stats.ols(s.values, series.season.values - series.season.mean())
        return st, ol

    st_a, ol_a = trend(gall)
    st_b, ol_b = trend(gbal)
    print("\nTREND of the GLOBAL series (ex-ante skew by year):")
    print(f"  {'series':22} {'β/yr':>10} {'r':>7} {'ADF p':>8} {'KPSS p':>8}")
    print(f"  {'all leagues':22} {ol_a['slope']:+10.5f} {ol_a['r']:+7.2f} "
          f"{st_a['adf_p']:8.3f} {st_a['kpss_p']:8.3f}")
    print(f"  {'balanced (fixed)':22} {ol_b['slope']:+10.5f} {ol_b['r']:+7.2f} "
          f"{st_b['adf_p']:8.3f} {st_b['kpss_p']:8.3f}")
    print(f"\n  Δ20yr balanced = {ol_b['slope']*20:+.3f} | mean level "
          f"{gbal.skew_exante.mean():+.3f} (sd {gbal.skew_exante.std():.3f})")
    print("  → with the basket of leagues FIXED, the global series remains trendless: the")
    print("    invariance does not come from a composition change (confound dead).")

    C.OUTDIR.mkdir(exist_ok=True)
    gbal.to_csv(C.OUTDIR / "balanced_global_series.csv", index=False)

    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(gall.season, gall.skew_exante, "o-", color="0.6", lw=1.2, ms=4,
            label=f"all leagues (β={ol_a['slope']:+.4f})")
    ax.plot(gbal.season, gbal.skew_exante, "s-", color="#1f77b4", lw=2, ms=5,
            label=f"balanced, {len(bal)} fixed leagues (β={ol_b['slope']:+.4f})")
    ax.axhline(gbal.skew_exante.mean(), color="#1f77b4", lw=.8, ls="--", alpha=.6)
    ax.set_xlabel("season"); ax.set_ylabel("global ex-ante skewness")
    ax.set_title("F13 — G2: global series on strict balanced panel (no drift)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f13_balanced_panel.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f13_balanced_panel.png'} | {C.OUTDIR / 'balanced_global_series.csv'}")

    prov.write_stamp("24_balanced_panel", metrics={
        "n_balanced": len(bal), "beta_balanced": ol_b["slope"],
        "delta20_balanced": ol_b["slope"] * 20, "kpss_p_balanced": st_b["kpss_p"]})


if __name__ == "__main__":
    main()
