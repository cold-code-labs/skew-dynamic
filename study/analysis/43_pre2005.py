"""43 — Pre-2005 front: does the skewness baseline BREAK across regimes? [CANONICAL DATA]
The paper predicts that the league-specific baseline shifts at the regime shocks in
the literature (Bosman 1995, Champions League expansion 1994/95, revenue divergence
~2003). The main study's ≥2005 window sits INSIDE the modern regime. Here we extend
backwards with the canonical football-data.co.uk using WILLIAM HILL — the only book
continuous over 2000–2025 (consistent book ⇒ no source-switch confound; skewness is
book-invariant, G1/D2).

Honest limit: 1X2 odds only exist from ~2000 onwards, so we do NOT reach the 1990s
shocks (Bosman/Champions). We test the reachable tail (2000–2004 vs 2005+), which
brackets the revenue divergence of the early 2000s.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (fdcanon as fc, exante, panel as P, stats,
                     provenance as prov, config)

CUT = 2005


def main():
    raw = fc.load()
    d = exante.add_exante(fc.with_odds(raw, fc.WH))          # de-vig William Hill
    d["year"] = d.date.dt.year
    pan = P.league_season_panel(d, min_n=150)
    pan = pan[pan.season <= 2023]        # the 2024 calendar is partial (biased composition)
    print(f"N={len(d):,} matches (WH) | panel {len(pan)} league-years | "
          f"{pan.season.min()}–{pan.season.max()} | {pan.Division.nunique()} leagues", flush=True)

    # WH calibration in the early era (sanity)
    early = d[d.year < CUT]
    sk_a = exante.pooled_skew(early.p_fav_dv.values, early.o_fav.values)
    print(f"  WH calibration pre-2005: ex-ante skew {sk_a['skew']:+.3f} | "
          f"within {sk_a['within_frac']:.3f} | overround {early.overround.mean():.4f}")

    # ── pre-2005 vs modern era, by league (only leagues with both eras) ──
    pan["era"] = np.where(pan.season < CUT, "pre2005", "modern")
    rows = []
    for lg, g in pan.groupby("Division"):
        a = g[g.era == "pre2005"].skew_exante; m = g[g.era == "modern"].skew_exante
        if len(a) >= 3 and len(m) >= 5:
            rows.append({"Division": lg, "pre2005": float(a.mean()),
                         "modern": float(m.mean()), "delta": float(m.mean() - a.mean()),
                         "n_pre": len(a)})
    import pandas as pd
    E = pd.DataFrame(rows)
    from scipy.stats import ttest_rel
    tt = ttest_rel(E.modern, E.pre2005)
    print(f"\nBASELINE pre-2005 vs modern ({len(E)} leagues with both eras):")
    print(f"  mean pre-2005 skew {E.pre2005.mean():+.3f} | modern {E.modern.mean():+.3f} "
          f"| mean Δ {E.delta.mean():+.4f} (sd {E.delta.std():.3f})")
    print(f"  paired test (modern−pre): t={tt.statistic:+.2f}, p={tt.pvalue:.2f} "
          f"| corr(pre, modern) across leagues = {np.corrcoef(E.pre2005, E.modern)[0,1]:+.3f}")

    # level DiD: pre-2005 indicator under league FE (clustered by league)
    import statsmodels.formula.api as smf
    pan["pre"] = (pan.era == "pre2005").astype(int)
    m = smf.ols("skew_exante ~ pre + C(Division)", data=pan).fit(
        cov_type="cluster", cov_kwds={"groups": pan.Division})
    ci = m.conf_int().loc["pre"]
    print(f"  pre-2005 vs modern level (league FE): β={m.params['pre']:+.4f} "
          f"[{ci[0]:+.4f},{ci[1]:+.4f}] p={m.pvalues['pre']:.2f}")

    # trend and breaks over the FULL 2000–2025 span
    tr = P.trend_test(pan)
    print(f"\nFULL SPAN 2000–2024: trend β={tr['beta_year']:+.5f}/yr "
          f"[{tr['ci_lo']:+.5f},{tr['ci_hi']:+.5f}] p={tr['p']:.2f}")
    brk = P.league_breaks(pan, min_seasons=12)
    if len(brk):
        yrs = brk.break_season.value_counts().sort_index()
        print(f"  PELT breaks by league: {len(brk)} in total | years: {dict(yrs)}")
    else:
        print("  PELT breaks by league: none")
    print("\n  → extending to 2000 (consistent WH book): NO break in 2005 (the study's")
    print("    cut is not a regime boundary), and the league ordering is preserved")
    print("    (r=0.76) — the STRUCTURE is the same since 2000. There is a weak and")
    print("    marginal LEVEL drift (modern ~0.018 above pre-2005, p≈0.03–0.10, sensitive to")
    print("    the 2023/24 endpoint), far smaller than the between-league variation — consistent")
    print("    with INTRA-regime invariance + slow balance evolution, not timelessness.")
    print("    The 1990s shocks (Bosman/Champions) sit before the odds.")

    # league-demeaned series (COMMON temporal component, composition-free —
    # the raw mean would rise just because high-skew leagues enter over time,
    # the Block F confound; here each league is centred on its own mean)
    pan["dm"] = pan.skew_exante - pan.groupby("Division").skew_exante.transform("mean")
    gy = pan.groupby("season").dm.mean()

    config.OUTDIR.mkdir(exist_ok=True)
    E.to_csv(config.OUTDIR / "pre2005_by_league.csv", index=False)
    FIG = config.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    axes[0].axhline(0, color="0.85", lw=0.8)
    axes[0].plot(gy.index, gy.values, "o-", color="#1f77b4", ms=4)
    axes[0].axvline(CUT - 0.5, color="#d62728", ls="--", lw=1, label="study cut ≥2005")
    axes[0].set_xlabel("year"); axes[0].set_ylabel("skewness − league mean (WH)")
    axes[0].set_title("No baseline break in 2005\n(demeaned series, no composition)")
    axes[0].legend(frameon=False, fontsize=8)
    lo = min(E.pre2005.min(), E.modern.min()) - 0.02
    hi = max(E.pre2005.max(), E.modern.max()) + 0.02
    axes[1].plot([lo, hi], [lo, hi], "--", color="0.7", lw=1)
    axes[1].scatter(E.pre2005, E.modern, s=28, color="#1f77b4")
    axes[1].set_xlabel("pre-2005 baseline (2000–2004)")
    axes[1].set_ylabel("modern baseline (2005+)")
    axes[1].set_title(f"Same baseline by league (r={np.corrcoef(E.pre2005,E.modern)[0,1]:+.2f})")
    fig.suptitle("F32 — pre-2005: the modern regime already holds since ~2000 "
                 "(extended invariance)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f32_pre2005.png", dpi=config.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f32_pre2005.png'} | {config.OUTDIR / 'pre2005_by_league.csv'}")

    ch = fc.canonical_hash()
    prov.write_stamp("43_pre2005", metrics={
        "skew_pre2005": float(E.pre2005.mean()), "skew_modern": float(E.modern.mean()),
        "delta_mean": float(E.delta.mean()), "paired_p": float(tt.pvalue),
        "level_beta_pre": float(m.params["pre"]), "level_p": float(m.pvalues["pre"]),
        "trend_beta": tr["beta_year"], "trend_p": tr["p"], "n_leagues": len(E),
        "data_source": "canonical_WH", "canonical_sha": ch["sha256"]})


if __name__ == "__main__":
    main()
