"""33 — C3: Kelly / optimal staking under the skewness structure. What does the
asymmetry imply for bankroll growth? (1) under the real margin, Kelly dictates NOT
betting on almost everything — the structure gives no growth (efficiency, echoes C1);
(2) the moment decomposition of the log-growth isolates the ROLE of skewness and
explains why the underdog bettor tolerates negative EV: the positive skew ADDS to the
log utility, a "skewness premium" they pay in EV.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, staking as st, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    p = df.p_fav_dv.values; o = df.o_fav.values
    print(f"N={len(df):,}")

    # (1) Kelly under the real margin: almost everything f*=0
    f_real = st.kelly_fraction(p, o)
    pos = float((f_real > 0).mean())
    print(f"\n(1) KELLY under the real margin (odds with vig):")
    print(f"  fraction of bets with f*>0 (EV>0) = {pos:.1%}; mean f* = {f_real.mean():.4f}")
    print(f"  → after the margin, there is no growth to extract (efficient market, ~C1).")

    # (2) role of skewness in growth — favourite (skew−) vs underdog (skew+)
    #     at a fixed small fraction f0, decomposes g ≈ μ·f − σ²f²/2 + m₃f³/3
    f0 = 0.05
    pud = 1 - p; oud = 1.0 / np.clip(pud, 1e-6, None)        # underdog at the dog's fair odd
    # real underdog: the "other side" — uses the implied odd of the non-favourite
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    O = df[["OddHome", "OddDraw", "OddAway"]].to_numpy(float)
    j = P.argmax(1); i = np.arange(len(P))
    # underdog = lowest prob (highest odd)
    k = P.argmin(1)
    p_dog, o_dog = P[i, k], O[i, k]

    tf = st.moment_growth_terms(p, o, np.full_like(p, f0))     # favourite
    td = st.moment_growth_terms(p_dog, o_dog, np.full_like(p_dog, f0))  # underdog
    print(f"\n(2) DECOMPOSITION of the log-growth at f={f0} (×1e3):")
    print(f"  {'bet':10} {'μ (mean)':>10} {'−σ²/2 (var)':>12} {'skew':>10} {'sum':>10}")
    for lab, t in [("favourite", tf), ("underdog", td)]:
        m, v, s = t["mean"].mean()*1e3, t["var"].mean()*1e3, t["skew"].mean()*1e3
        print(f"  {lab:10} {m:>10.3f} {v:>12.3f} {s:>+10.3f} {m+v+s:>10.3f}")
    print("  → for the underdog the SKEWNESS term is positive and large: the asymmetry")
    print("    compensates part of the negative EV in growth/utility — the channel")
    print("    by which the FLB (skew preference) survives being EV-negative.")

    # curve: skewness term along p_fav (the unit fraction)
    grid = np.linspace(0.05, 0.95, 60)
    skew_unit = np.array([st.moment_growth_terms(np.array([q]), np.array([1.0/q]),
                          np.array([f0]))["skew"][0] for q in grid]) * 1e3

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].hist(f_real, bins=40, color="#1f77b4")
    axes[0].set_xlabel("Kelly fraction f* (real odds)"); axes[0].set_ylabel("matches")
    axes[0].set_title(f"Kelly ≈ 0 after the margin ({pos:.0%} with EV>0)")
    axes[1].axhline(0, color="0.7", lw=.8); axes[1].axvline(0.5, color="0.85", lw=.8)
    axes[1].plot(grid, skew_unit, color="#d62728", lw=2)
    axes[1].set_xlabel("probability p of the bet side"); axes[1].set_ylabel("skew term in g (×1e3)")
    axes[1].set_title("Skewness drives growth in the underdog (p<0.5)")
    fig.suptitle("F21 — C3: Kelly/growth under the skewness structure", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f21_kelly.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f21_kelly.png'}")

    prov.write_stamp("33_kelly_staking", metrics={
        "frac_positive_ev": pos, "skew_term_dog": float(td["skew"].mean()*1e3),
        "skew_term_fav": float(tf["skew"].mean()*1e3)})


if __name__ == "__main__":
    main()
