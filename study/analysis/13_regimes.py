"""13 — Regime vs invariance (P1): the thesis is WITHIN-REGIME invariance.

The literature (Lee & Fort 2012; Basini et al. 2023) finds real structural breaks
in EPL competitiveness, tied to institutional shocks — Champions League (1994/95),
Bosman (1995), revenue inequality (~2003). ALL prior to our ≥2005 sample. Prediction
under the regime view: WITHIN 2005–2025 (a single modern regime) there should be few
breaks and NO common year across leagues. We test exactly that.
"""
from skewlib import io, returns, exante, panel, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = panel.league_season_panel(df)

    print("=== Per-league breaks within 2005–2025 (conservative PELT) ===")
    bks = panel.league_breaks(pan)
    n_leagues = pan[pan.groupby("Division").Division.transform("size") >= 10].Division.nunique()
    print(f"  leagues tested (≥10 seasons): {n_leagues}")
    print(f"  breaks detected: {len(bks)} across {bks.Division.nunique()} leagues")
    if len(bks):
        print(bks.sort_values("break_season").to_string(index=False,
              formatters={"shift": "{:+.3f}".format}))
        print("\n  Histogram of break YEAR (market-wide regime = common year):")
        h = bks.break_season.value_counts().sort_index()
        for yr, c in h.items():
            print(f"    {yr}: {'█'*c} ({c})")
        print(f"  → max leagues breaking in the SAME year: {h.max()} "
              f"({'no common regime' if h.max() <= 2 else 'possible common regime'})")
        sh = bks["shift"]  # bks.shift would clash with DataFrame.shift()
        print(f"  → mean |shift| at the breaks: {sh.abs().mean():.3f} "
              f"(vs between-league sd 0.052) | mixed sign: "
              f"{(sh>0).sum()}↑ / {(sh<0).sum()}↓")

    print("\n=== EPL focus (E0) — Lee & Fort find PRE-1995/2003 regimes ===")
    e0 = pan[pan.Division == "E0"].sort_values("season")
    print(f"  E0 skewness 2005–2025: mean={e0.skew_exante.mean():.3f} "
          f"sd={e0.skew_exante.std():.3f} "
          f"range=[{e0.skew_exante.min():.3f},{e0.skew_exante.max():.3f}]")
    e0bk = bks[bks.Division == "E0"]
    print(f"  E0 breaks in our sample: {len(e0bk)} "
          f"→ {'within-regime stable (consistent: EPL shocks are pre-2005)' if len(e0bk)==0 else 'investigate'}")

    print("\n=== Framing ===")
    print("  Regime shocks (Bosman 95, CL 94/95, ~2003) are PRIOR to the sample.")
    print("  2005–2025 ≈ a single modern regime → 'no trend' = WITHIN-REGIME")
    print("  invariance, not absolute timelessness. Baseline is league-specific.")


if __name__ == "__main__":
    main()
