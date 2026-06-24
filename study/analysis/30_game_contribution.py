"""30 — Micro F2: which MATCHES carry the league's skewness? Decomposes the pooled
3rd moment by match competitiveness band (p_fav). Makes the "tail cancellation"
explicit: WEAK-favourite matches (p≈0.5) contribute positive skew, STRONG-favourite
matches (high p) negative skew — the competitiveness at the MATCH level determines
the match's skew contribution.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, intraleague as il, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    tab, tot = il.m3_contribution_by_bin(df)
    print(f"N={len(df):,} | total pooled M₃ = {tot:.1f}")
    print("\nContribution to the 3rd moment by match competitiveness band (p_fav):")
    print(f"  {'band':16} {'n':>8} {'p_mid':>7} {'skew_match':>10} {'share M₃':>9}")
    for r in tab.itertuples():
        print(f"  {r.bin:16} {r.n:>8,} {r.p_mid:>7.3f} {r.skew_match:>+10.3f} "
              f"{r.m3_share:>+9.1%}")
    pos = tab[tab.skew_match > 0].m3_share.sum()
    neg = tab[tab.skew_match < 0].m3_share.sum()
    print(f"\n  WEAK-favourite matches (p<0.5) sum to {pos:+.0%} of M₃; "
          f"STRONG-favourite (p>0.5) {neg:+.0%}")
    print("  → the league skew is the net sum: the MATCH competitiveness fixes the")
    print("    sign and the magnitude of each match's contribution (law at the micro level).")

    C.OUTDIR.mkdir(exist_ok=True)
    tab.to_csv(C.OUTDIR / "m3_contribution_by_bin.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ["#2ca02c" if s > 0 else "#d62728" for s in tab.skew_match]
    ax.bar(range(len(tab)), tab.m3_share * 100, color=colors, alpha=.85)
    ax.axhline(0, color="0.5", lw=.8)
    ax.set_xticks(range(len(tab)))
    ax.set_xticklabels([f"{r.p_mid:.2f}" for r in tab.itertuples()])
    ax.set_xlabel("band mean $p_{fav}$ (match competitiveness)")
    ax.set_ylabel("contribution to M₃ (%)")
    ax.set_title("F18 — F2: even matches (green) pull +skew, unbalanced (red) −")
    fig.tight_layout()
    fig.savefig(FIG / "f18_game_contribution.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f18_game_contribution.png'} | {C.OUTDIR / 'm3_contribution_by_bin.csv'}")

    prov.write_stamp("30_game_contribution", metrics={
        "share_weak_fav": float(pos), "share_strong_fav": float(neg)})


if __name__ == "__main__":
    main()
