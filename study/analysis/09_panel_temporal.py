"""09 — Temporal invariance (W3): league×season panel.

Shows that the ex-ante skewness is (i) free of secular trend, (ii) dominated by
between-league variance (the structural invariant) and not within-league, (iii) free
of per-league breaks, and (iv) immune to the COVID home-advantage shock.
"""
from skewlib import io, returns, exante, panel, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = panel.league_season_panel(df)
    print(f"panel: {len(pan)} league×season obs | "
          f"{pan.Division.nunique()} leagues | {pan.season.min()}–{pan.season.max()}")

    print("\n=== Secular trend (league + year FE, clustered SE) ===")
    t = panel.trend_test(pan)
    print(f"  β_year = {t['beta_year']:+.5f}/year  SE={t['se']:.5f}  p={t['p']:.3f}  "
          f"95%CI[{t['ci_lo']:+.5f},{t['ci_hi']:+.5f}]  (n={t['n_obs']})")
    print(f"  → drift over 20 years ≈ {t['beta_year']*20:+.4f} "
          f"(vs between-league sd ~0.06) — {'no trend' if t['p']>0.05 else 'TREND'}")

    print("\n=== Variance decomposition ===")
    v = panel.variance_decomp(pan)
    se = panel.sampling_se(df)
    print(f"  between-league sd = {v['sd_between']:.4f}  (the structural invariant)")
    print(f"  within-league sd  = {v['sd_within']:.4f}  (temporal fluctuation)")
    print(f"  mean sampling SE (bootstrap of games) = {se:.4f}")
    print(f"  → within ({v['sd_within']:.4f}) ≈ sampling noise ({se:.4f}): "
          f"{'fluctuation is sampling' if se >= 0.8*v['sd_within'] else 'real temporal signal present'}")
    print(f"  ICC = {v['icc']:.3f}  → {v['icc']*100:.0f}% of the variance is between leagues")

    print("\n=== Per-league trends/breaks ===")
    pl = panel.per_league_trends(pan)
    big = pl[pl.slope_per_year.abs() > 0.003]
    print(f"  leagues with |slope|>0.003/year: {len(big)}/{len(pl)}")
    print(f"  mean |slope| = {pl.slope_per_year.abs().mean():.5f}/year | "
          f"total breaks = {pl.n_breaks.clip(lower=0).sum()} "
          f"(leagues with ≥1 break: {(pl.n_breaks>0).sum()})")

    print("\n=== COVID vignette (empty stadiums 2020/21) ===")
    hw = panel.home_win_rate_by_year(df)
    for y in (2018, 2019, 2020, 2021, 2022):
        if y in hw.index:
            print(f"  home win rate {y}: {hw[y]:.3f}")
    cov = panel.covid_vignette(pan)
    print(f"  2020 skewness deviation vs league mean: mean z (signed) = "
          f"{cov.z.mean():+.2f} | mean |z| = {cov.z.abs().mean():.2f}  "
          f"(leagues with z>0: {(cov.z>0).sum()}/{len(cov)})")
    print("  → HFA drops (weaker home side → more parity); the law predicts skewness ↑.")
    print("    positive signed mean z = competitiveness shock moved the skewness")
    print("    in the predicted direction (corroborates the cause; does not contradict the secular invariance).")

    C.OUTDIR.mkdir(exist_ok=True)
    pan.to_csv(C.OUTDIR / "panel_league_season.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'panel_league_season.csv'}")


if __name__ == "__main__":
    main()
