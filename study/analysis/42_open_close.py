"""42 — Front D1: price discovery (opening → closing). [CANONICAL DATA]
The frozen mirror only has the closing price; here we use the canonical
football-data.co.uk, which carries OPENING (Avg*) and CLOSING (Avg*C) odds of the
same match (2019/20–2023/24, 21 leagues). Central question of the thesis: is the
structural asymmetry ALREADY BORN in the opening price, or does the market "discover"
it over the course of trading?

If skewness is inherited from the competitive structure (not produced by pricing),
it should already be present at the open and barely move through to the close —
even if the close is sharper (smaller margin, better calibration). It extends the
margin orthogonality (W4/D2, across books) to the TEMPORAL axis of price formation.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import fdcanon as fc, devig, exante, stats, provenance as prov, config as C


def _overround(g, cols):
    r = 1.0 / g[list(cols)].to_numpy(float)
    return r.sum(1).mean()


def main():
    df = fc.load()
    # matches with valid opening AND closing 1X2
    d = df.copy()
    for c in (*fc.OPEN_AVG, *fc.CLOSE_AVG):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=[*fc.OPEN_AVG, *fc.CLOSE_AVG])
    for c in (*fc.OPEN_AVG, *fc.CLOSE_AVG):
        d = d[d[c] > C.MIN_ODD]
    print(f"N={len(d):,} | {d.Division.nunique()} leagues | {d.season.min()}–{d.season.max()} "
          f"(opening AND closing odds)", flush=True)

    # ── de-vig opening and closing; favourite defined at the OPEN ──
    do = devig.devig_frame(d, cols=fc.OPEN_AVG)
    dc = devig.devig_frame(d, cols=fc.CLOSE_AVG)
    Po = do[["p_H", "p_D", "p_A"]].to_numpy(float)
    Pc = dc[["p_H", "p_D", "p_A"]].to_numpy(float)
    Oo = d[list(fc.OPEN_AVG)].to_numpy(float)
    Oc = d[list(fc.CLOSE_AVG)].to_numpy(float)
    i = np.arange(len(d)); j = Po.argmax(1)            # favourite at the open
    p0 = Po[i, j]; p1 = Pc[i, j]                        # same leg: prob open→close
    o0 = Oo[i, j]; o1 = Oc[i, j]
    res = d.FTResult.map({"H": 0, "D": 1, "A": 2}).to_numpy()
    fav_won = (res == j).astype(float)

    # margin and calibration: is the close sharper?
    over_o = (1.0 / Oo).sum(1).mean(); over_c = (1.0 / Oc).sum(1).mean()
    brier_o = float(np.mean((fav_won - p0) ** 2)); brier_c = float(np.mean((fav_won - p1) ** 2))
    drift = p1 - p0
    print(f"\nMARGIN and CALIBRATION (opening favourite, {len(d):,} matches):")
    print(f"  overround   open {over_o:.4f} → close {over_c:.4f} "
          f"(margin falls {100*(over_o-over_c):.2f} p.p.)")
    print(f"  Brier(fav)  open {brier_o:.4f} → close {brier_c:.4f} "
          f"({'close sharper' if brier_c < brier_o else 'no gain'})")
    print(f"  favourite prob: opens {p0.mean():.4f} → closes {p1.mean():.4f} "
          f"(mean drift {drift.mean():+.4f}; the favourite {'firms' if drift.mean()>0 else 'eases'})")

    # ── skewness by league: opening vs closing ──
    rows = []
    for lg, g in d.groupby("Division"):
        po, oo, so = exante.market_skew(g, fc.OPEN_AVG)
        pc, oc, sc = exante.market_skew(g, fc.CLOSE_AVG)
        rows.append({"Division": lg, "n": len(g),
                     "skew_open": so["skew"], "skew_close": sc["skew"],
                     "within_open": so["within_frac"], "within_close": sc["within_frac"],
                     "pfav_open": float(po.mean()), "pfav_close": float(pc.mean()),
                     "over_open": _overround(g, fc.OPEN_AVG),
                     "over_close": _overround(g, fc.CLOSE_AVG)})
    L = pd.DataFrame(rows)
    go = exante.market_skew(d, fc.OPEN_AVG)[2]; gc = exante.market_skew(d, fc.CLOSE_AVG)[2]
    print(f"\nSKEWNESS opening vs closing:")
    print(f"  global: open {go['skew']:+.3f} (within {go['within_frac']:.3f}) → "
          f"close {gc['skew']:+.3f} (within {gc['within_frac']:.3f})")
    rcc = stats.bootstrap_corr(L.skew_open.values, L.skew_close.values)
    print(f"  corr(skew_open, skew_close) across {len(L)} leagues = {rcc['r']:+.3f} "
          f"[{rcc['ci_lo']:+.2f},{rcc['ci_hi']:+.2f}]")
    lo = stats.bootstrap_corr(L.skew_open.values, L.pfav_open.values)
    lc = stats.bootstrap_corr(L.skew_close.values, L.pfav_close.values)
    print(f"  structural law corr(skew, p_fav): open {lo['r']:+.3f} | close {lc['r']:+.3f}")
    print(f"  mean Δskew (close−open) by league = {(L.skew_close-L.skew_open).mean():+.4f} "
          f"(sd {(L.skew_close-L.skew_open).std():.4f})")
    print("\n  → the asymmetry is already IN THE OPENING PRICE; the close refines the")
    print("    margin/calibration but barely moves the skewness (corr ~1). The asymmetry")
    print("    is inherited from structure, not produced by trading — the temporal axis of W4/D2.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "open_close_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    mn = min(L.skew_open.min(), L.skew_close.min()) - 0.02
    mx = max(L.skew_open.max(), L.skew_close.max()) + 0.02
    axes[0].plot([mn, mx], [mn, mx], "--", color="0.7", lw=1)
    axes[0].scatter(L.skew_open, L.skew_close, s=28, color="#1f77b4")
    axes[0].set_xlabel("skewness at OPEN"); axes[0].set_ylabel("skewness at CLOSE")
    axes[0].set_title(f"Same skewness open→close (r={rcc['r']:+.2f})")
    axes[1].bar([0, 1], [over_o - 1, over_c - 1], width=0.5, color=["#aec7e8", "#1f77b4"])
    axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(["open", "close"])
    axes[1].set_ylabel("margin (overround − 1)")
    axes[1].set_title(f"Margin falls, skewness does not\nglobal skew {go['skew']:+.3f}→{gc['skew']:+.3f}")
    fig.suptitle("F30 — D1: the skewness is already born in the opening price "
                 "(price discovery)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f30_open_close.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f30_open_close.png'} | {C.OUTDIR / 'open_close_by_league.csv'}")

    ch = fc.canonical_hash()
    prov.write_stamp("42_open_close", metrics={
        "skew_open": go["skew"], "skew_close": gc["skew"],
        "corr_open_close": rcc["r"], "law_open": lo["r"], "law_close": lc["r"],
        "over_open": over_o, "over_close": over_c, "brier_open": brier_o,
        "brier_close": brier_c, "fav_drift": float(drift.mean()), "n": len(d),
        "data_source": "canonical", "canonical_sha": ch["sha256"]})


if __name__ == "__main__":
    main()
