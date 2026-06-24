"""36 — Front J: information arrival (HT→FT). The half-time scoreline updates the
pre-match favourite's win probability; the skewness of the "rest of the match" is
again the identity (1−2q)/√(q(1−q)) in the conditional probability q. Shows that
(i) the mechanical core is DYNAMIC (it holds at every information state) and (ii) the
asymmetry RESOLVES with the scoreline: favourite ahead ⇒ high q ⇒ negative skew;
behind ⇒ low q ⇒ positive skew.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, inplay, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = inplay.fav_state(df)
    print(f"N(valid HT)={len(d):,} of {len(df):,} | pre-match favourite, half-time state")

    sk0 = exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)["skew"]
    print(f"\nPRE-MATCH: p_fav {d.p0.mean():.3f} | pooled skew {sk0:+.3f}")

    tab = inplay.conditional_table(d)
    print("\nFAVOURITE STATE AT HALF-TIME → conditional probability and skewness of the rest of the match:")
    print(f"  {'state':12} {'share':>7} {'q (win)':>9} {'skew rest':>11} {'n':>8}")
    for r in tab.itertuples():
        print(f"  {r.state:12} {r.share:>7.1%} {r.q_cond:>9.3f} {r.skew_cond:>+11.3f} {r.n:>8,}")
    print("  → the asymmetry RESOLVES: ahead, the bet turns NEGATIVELY skewed (the")
    print("    favourite has nearly won), behind it turns POSITIVE (it becomes lottery-like)")
    print("    — the mechanical identity holds DYNAMICALLY, not only at kick-off.")

    mc = inplay.martingale_check(d)
    print("\nDYNAMIC CALIBRATION (E[HT q | p0 band] ≈ p0 — martingale refinement):")
    for r in mc.itertuples():
        print(f"  {r.p_bin:14} p0 {r.p0_mean:.3f} → mean FT q {r.q_mean:.3f} (n={r.n:,})")
    err = float(np.mean(np.abs(mc.p0_mean - mc.q_mean)))
    print(f"  mean error |p0 − q| = {err:.4f} (≈0 ⇒ the pre-match probability is well calibrated")
    print("    and HT refines it without bias: implied skewness is coherent at every information state.)")

    C.OUTDIR.mkdir(exist_ok=True)
    tab.to_csv(C.OUTDIR / "inplay_conditional.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    pp = np.linspace(0.05, 0.95, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(pp, exante.per_match_skew(pp), color="0.5", lw=2,
                 label="identity (1−2q)/√(q(1−q))")
    axes[0].axhline(0, color="0.85", lw=.8); axes[0].axvline(0.5, color="0.85", lw=.8)
    cols = {"atrás": "#2ca02c", "empatado": "#1f77b4", "+1": "#ff7f0e", "+2 ou mais": "#d62728"}
    state_en = {"atrás": "behind", "empatado": "level", "+1": "+1", "+2 ou mais": "+2 or more"}
    for r in tab.itertuples():
        axes[0].scatter([r.q_cond], [r.skew_cond], s=90, color=cols.get(r.state, "#333"),
                        zorder=4, label=f"HT {state_en.get(r.state, r.state)}")
    axes[0].set_xlabel("q = P(favourite wins | HT state)")
    axes[0].set_ylabel("skewness of the rest of the match")
    axes[0].set_title("The asymmetry resolves with information"); axes[0].legend(frameon=False, fontsize=7)
    axes[1].plot([0.4, 0.75], [0.4, 0.75], "--", color="0.7", lw=1, label="calibration")
    axes[1].scatter(mc.p0_mean, mc.q_mean, s=40, color="#1f77b4", zorder=3)
    axes[1].set_xlabel("pre-match p0 (band mean)"); axes[1].set_ylabel("mean q at FT")
    axes[1].set_title(f"Martingale refinement (|Δ|={err:.3f})"); axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F24 — J: the mechanical core is dynamic (HT→FT)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f24_inplay.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f24_inplay.png'} | {C.OUTDIR / 'inplay_conditional.csv'}")

    prov.write_stamp("36_inplay_resolution", metrics={
        "skew_pregame": sk0, "skew_behind": float(tab[tab.state == "atrás"].skew_cond.iloc[0]),
        "skew_ahead2": float(tab[tab.state == "+2 ou mais"].skew_cond.iloc[0]),
        "martingale_err": err})


if __name__ == "__main__":
    main()
