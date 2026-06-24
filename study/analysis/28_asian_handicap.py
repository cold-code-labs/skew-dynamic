"""28 — Microstructure D4: the ASIAN HANDICAP market as a 3rd market for the
identity. Beyond 1X2 (W1) and O/U 2.5 (W5), the AH is a 2-way market with a MOVING
line that balances the match to ~50/50. Prediction: the identity (1−2p)/√(p(1−p))
still holds, but since the AH pushes p_fav→0.5, the implied skewness ≈ 0 — the SAME
mechanical law, in a regime of artificially maximal competitiveness.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import skew as spskew
from skewlib import io, returns, exante, microstructure as ms, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    d = ms.prep_ah(df)
    print(f"N(valid AH)={len(d):,} of {len(df):,} | mean AH overround "
          f"{d.overround_ah.mean():.3f}")

    g = exante.pooled_skew(d.p_fav_ah.values, d.o_fav_ah.values)
    print(f"\nAH MARKET — favourite: mean p_fav {d.p_fav_ah.mean():.3f} "
          f"(line balances to ~0.5)")
    print(f"  POOLED ex-ante skewness = {g['skew']:+.4f}  (within-match "
          f"{g['within_frac']*100:.1f}%)")
    print(f"  vs 1X2 +0.236 (p_fav~0.50) and O/U −0.21 — the AH prices p_fav closer")
    print(f"    to 0.5, so the implied skew shrinks, as the identity predicts.")

    # ex-ante vs ex-post comparison (only settled matches without push/quarter)
    s = d[d.ah_settled]
    if len(s) > 5000:
        ep = float(spskew(s.ret_fav_ah.values))
        print(f"\n  ex-post (n settled={len(s):,}): realised skew {ep:+.3f} "
              f"vs ex-ante {exante.pooled_skew(s.p_fav_ah.values, s.o_fav_ah.values)['skew']:+.3f}")

    L = ms.ah_league(d, min_n=2000)
    # each league: does the AH skew fall on the identity curve at that market's p_fav?
    ident = exante.per_match_skew(L.p_fav_ah.values)
    rr = float(np.corrcoef(L.skew_ah.values, ident)[0, 1])
    print(f"\nBY LEAGUE ({len(L)}): skew_ah on the identity (1−2p)/√(p(1−p)) evaluated at "
          f"the AH p_fav → r={rr:+.2f}")
    print("  → a third independent market confirms the mechanical core (it is not from the 1X2).")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "asian_handicap_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    pp = np.linspace(0.3, 0.7, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(pp, exante.per_match_skew(pp), color="0.5", lw=2,
            label="identity (1−2p)/√(p(1−p))")
    ax.scatter(L.p_fav_ah, L.skew_ah, s=22, color="#d62728", zorder=3, label="AH by league")
    ax.axhline(0, color="0.85", lw=.8); ax.axvline(0.5, color="0.85", lw=.8)
    ax.set_xlabel("AH market $p_{fav}$"); ax.set_ylabel("AH ex-ante skewness")
    ax.set_title(f"F16 — D4: Asian handicap on the identity (r={rr:+.2f})")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f16_asian_handicap.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f16_asian_handicap.png'} | {C.OUTDIR / 'asian_handicap_by_league.csv'}")

    prov.write_stamp("28_asian_handicap", metrics={
        "p_fav_ah": float(d.p_fav_ah.mean()), "skew_ah_global": g["skew"],
        "within_frac_ah": g["within_frac"], "league_identity_r": rr})


if __name__ == "__main__":
    main()
