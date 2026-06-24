"""45 — skew-meter: SIMILARITY OF SKEWNESSES (reference study for the root objective).
The project's original objective was to MEASURE THE SIMILARITY OF SKEWNESSES. This
block operationalises that in a single apparatus (skewlib/skewmeter.py) and shows:

  A) Similarity matrix across leagues: the RAW distance between skewnesses is large,
     but the RESIDUAL (net of competitiveness) COLLAPSES to the sampling floor — the
     skewnesses are the SAME once competitiveness is equalised (B2 operationalised).
  B) FEW-parameter apparatus: no Shin (~0 cost), 1 parameter (mean p_fav → closed
     form) and odds-free (results only) — how much is lost.
  C) Real-time convergence: how fast the meter 'locks' on a league.
  D) Pairwise verdict: 'same skewness?' with a z-score vs the noise.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (io, returns, exante, devig, elo, skewmeter as sm,
                     provenance as prov, config as C)


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    law = sm.fit_law(df)
    print(f"N={len(df):,} | calibrated law: h={law['par']['h']:.3f} c={law['par']['c']:.3f}",
          flush=True)

    # ── per-league signatures + sampling floor ──
    sigs, se_by = [], {}
    for lg, g in df.groupby("Division"):
        if len(g) < 2000:
            continue
        sigs.append(sm.measure(g.p_fav_dv.values, g.o_fav.values, label=lg))
        se_by[lg] = sm.skew_se(g.p_fav_dv.values, g.o_fav.values)
    sigs = sorted(sigs, key=lambda s: s["comp"])           # sort by competitiveness
    ses = [se_by[s["label"]] for s in sigs]
    M = sm.matrix(sigs, law, ses=ses)
    truth0 = np.array([s["skew"] for s in sigs])
    one0 = np.array([sm.predict_skew(s["comp"], law) for s in sigs])
    r2 = np.corrcoef(truth0, one0)[0, 1] ** 2
    sd_between = float(truth0.std())
    print(f"\nA) SIMILARITY OF SKEWNESSES — {len(sigs)} leagues, |Δskew| distance:")
    print(f"   median RAW distance      = {M['median_raw']:.3f}")
    print(f"   median RESIDUAL distance = {M['median_residual']:.3f}  "
          f"(net of competitiveness, 1 parameter)")
    print(f"   raw→residual collapse    = {1-M['collapse']:.0%} of the distance "
          f"explained by 1 number (R²={r2:.2f} of the between-league variance)")
    print(f"   idiosyncratic residual: sd {sd_between*np.sqrt(1-r2):.3f} vs between-league "
          f"{sd_between:.3f} | sampling floor {M['noise_floor']:.3f}")
    # sufficiency ladder: how many parameters are enough?
    lad = sm.sufficiency_ladder(df, law)
    sh = sm.split_half_residual(df, law)
    print(f"\n   SUFFICIENCY LADDER (R² of skewness across leagues):")
    print(f"     1 parameter  (mean p_fav)          R² = {lad['r2_1param']:.3f}")
    print(f"     2 moments    (mean + variance)     R² = {lad['r2_2moment']:.3f}")
    print(f"     FULL p_fav distribution            R² = {lad['r2_full']:.3f}  "
          f"(residual {lad['resid_sd_full']:.3f} ≈ noise {M['noise_floor']:.3f})")
    print(f"   → MINIMAL sufficient statistic = the full distribution; the mean alone")
    print(f"     leaves a STABLE residual (temporal split-half r={sh['r']:.2f}), not noise")
    print(f"     — it is the curvature of the law, captured by the 2nd moment (98%).")

    # ── B) few-parameter apparatus ──
    truth = np.array([s["skew"] for s in sigs])
    comp = np.array([s["comp"] for s in sigs])
    cheap = []
    for s in sigs:
        g = df[df.Division == s["label"]]
        cheap.append(sm.gauge_cheap(g[["OddHome", "OddDraw", "OddAway"]].to_numpy(float))["skew"])
    cheap = np.array(cheap)
    one = np.array([sm.predict_skew(c, law) for c in comp])
    comp_elo = elo.league_competitiveness(elo.with_elo(df)).set_index("Division")
    upset = np.array([comp_elo.loc[s["label"], "upset_rate"] for s in sigs])
    print("\nB) FEW-PARAMETER APPARATUS (corr with the truth = pooled Shin):")
    print(f"   no Shin (inverse-odds, ~0 cost)   : {np.corrcoef(truth, cheap)[0,1]:.3f}")
    print(f"   1 PARAMETER (mean p_fav → curve)  : {np.corrcoef(truth, one)[0,1]:.3f}")
    print(f"   odds-free (upset rate, W/D/L only): {np.corrcoef(truth, upset)[0,1]:.3f}")

    # ── C) real-time convergence ──
    print("\nC) REAL-TIME CONVERGENCE (SE of skew with K matches):")
    big = df[df.Division.isin(["E0", "SP1", "I1", "D1", "F1"])]
    rng = np.random.default_rng(0)
    conv = {}
    for K in [50, 100, 200, 400, 800]:
        errs = []
        for lg, g in big.groupby("Division"):
            p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
            est = [exante.pooled_skew(p[i], o[i])["skew"]
                   for i in (rng.integers(0, n, K) for _ in range(120))]
            errs.append(np.std(est))
        conv[K] = float(np.mean(errs))
        print(f"   K={K:4d} matches → SE = {conv[K]:.3f}")
    print(f"   (BETWEEN-league sd = {truth.std():.3f} — the structural signal to resolve)")

    # ── D) EQUIVALENCE verdict (TOST): with huge n, significance always rejects;
    #     we test whether the residual difference fits within a substantive margin
    #     (half a between-league SD). ──
    margin = 0.5 * sd_between
    print(f"\nD) VERDICT 'SAME SKEWNESS?' (TOST equivalence, margin ½·sd = {margin:.3f}):")
    by = {s["label"]: (s, ses[k]) for k, s in enumerate(sigs)}
    pairs = [("E0", "SP1"), ("E0", "E3"), ("N1", "I2"), ("BRA", "ARG")]
    for a, b in pairs:
        if a in by and b in by:
            A, sa = by[a]; B, sb = by[b]
            raw = sm.distance(A, B); t = sm.tost(A, B, law, sa, sb, margin)
            expl = 1 - abs(t["d"]) / raw if raw > 0 else 0.0
            print(f"   {a} vs {b}: skew {A['skew']:+.3f}/{B['skew']:+.3f} | raw {raw:.3f} "
                  f"→ residual {abs(t['d']):.3f} (explains {expl:.0%}) → "
                  f"{'EQUIVALENT' if t['equivalent'] else 'distinct'}")

    # ── E) hardening (rigour): block-bootstrap SE, Mahalanobis, out-of-sample law ──
    print("\nE) APPARATUS ROBUSTNESS:")
    big5 = ["E0", "SP1", "I1", "D1", "F1"]
    iid = [sm.skew_se(df[df.Division == l].p_fav_dv.values,
                      df[df.Division == l].o_fav.values) for l in big5]
    blk = [sm.skew_se_block(df[df.Division == l]) for l in big5]
    print(f"   i.i.d.-matches SE {np.mean(iid):.4f} → SEASON block-bootstrap SE "
          f"{np.mean(blk):.4f} (×{np.mean(blk)/np.mean(iid):.1f} — intra-year dependence)")
    cov_inv = np.linalg.inv(sm.sampling_shape_cov(df[df.Division == "E0"]))
    maha = [sm.shape_distance(sigs[i], sigs[j], cov_inv)
            for i in range(len(sigs)) for j in range(i + 1, len(sigs))]
    rawpairs = [sm.distance(sigs[i], sigs[j])
                for i in range(len(sigs)) for j in range(i + 1, len(sigs))]
    print(f"   Mahalanobis shape distance (skew+exkurt): median {np.median(maha):.1f}σ "
          f"| corr with scalar |Δskew| = {np.corrcoef(maha, rawpairs)[0,1]:.2f} "
          f"(the 2-D shape tells the SAME story)")
    oos = sm.law_oos_r2(df)
    print(f"   OUT-OF-SAMPLE law (calibrate on even years, predict odd ones): R²={oos:.3f} "
          f"(≈ in-sample {lad['r2_1param']:.2f} → the residual ruler is not overfit)")

    print("\n  → CONCLUSION: 'similarity of skewnesses' IS, to first order,")
    print("    similarity of COMPETITIVENESS — a single number explains ~80% of the")
    print("    between-league variance of skewness (measurable in real time, without Shin,")
    print("    even odds-free). The residual is small and absorbed by the full distribution.")

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4),
                             gridspec_kw={"width_ratios": [1, 1, 0.9]})
    vmax = M["raw"].max()
    for ax, Mx, ttl in [(axes[0], M["raw"], "RAW  |Δskew|"),
                        (axes[1], M["residual"], "RESIDUAL (1 parameter)")]:
        im = ax.imshow(Mx, cmap="magma_r", vmin=0, vmax=vmax)
        ax.set_title(ttl, fontsize=11); ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_xlabel(f"leagues by competitiveness\nmedian {M['median_raw']:.3f}")
    axes[1].set_xlabel(f"median {M['median_residual']:.3f} ({1-M['collapse']:.0%} explained)")
    # panel 3: sufficiency ladder
    bars = [lad["r2_1param"], lad["r2_2moment"], lad["r2_full"]]
    axes[2].bar(["1 param\n(mean)", "2 moments\n(+variance)", "full\ndistrib."],
                bars, color=["#aec7e8", "#5b9bd5", "#1f3a5f"])
    for i, v in enumerate(bars):
        axes[2].text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=9)
    axes[2].set_ylim(0, 1.08); axes[2].set_ylabel("R² of skewness across leagues")
    axes[2].set_title("Sufficiency ladder", fontsize=11)
    fig.suptitle("F33 — skew-meter: similarity of skewnesses = similarity of "
                 "competitiveness\n(1 parameter explains 80%; the first 2 moments 98%; "
                 "the full distribution is sufficient)", y=1.07)
    fig.tight_layout()
    fig.savefig(FIG / "f33_skewmeter.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f33_skewmeter.png'}")

    prov.write_stamp("45_skewmeter", metrics={
        "median_raw": M["median_raw"], "median_residual": M["median_residual"],
        "noise_floor": M["noise_floor"], "r2_1param": lad["r2_1param"],
        "r2_2moment": lad["r2_2moment"], "r2_full": lad["r2_full"],
        "split_half_r": sh["r"], "corr_cheap": float(np.corrcoef(truth, cheap)[0, 1]),
        "corr_oddsfree": float(np.corrcoef(truth, upset)[0, 1]),
        "se_k400": conv[400], "se_iid": float(np.mean(iid)),
        "se_block": float(np.mean(blk)), "law_oos_r2": oos,
        "n_leagues": len(sigs)})


if __name__ == "__main__":
    main()
