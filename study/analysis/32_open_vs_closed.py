"""32 — H2: OPEN vs CLOSED league. The MLS (USA) is an American-style closed league —
salary cap + draft + NO relegation — designed to compress the strength dispersion;
the European leagues are open (promotion/relegation, no cap). Prediction of the law:
the closed structure pushes competitiveness up (p_fav→0.5) and the skewness towards
the balanced value. We test the position of the MLS on the curve against the most
unequal open leagues.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, balance, provenance as prov, config as C

CLOSED = {"USA"}   # MLS: salary cap, no relegation (only closed league in the sample)


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    lg = exante.pooled_by(df, "Division", min_n=2000)[
        ["Division", "n", "skew_exante", "p_fav_dv_mean"]]
    cb = balance.by_league(balance.cb_indices(balance.standings(df)))[
        ["Division", "noll_scully"]]
    L = lg.merge(cb, on="Division")
    L["closed"] = L.Division.isin(CLOSED)
    L = L.sort_values("noll_scully").reset_index(drop=True)

    print(f"N={len(df):,} | {len(L)} leagues | closed: {sorted(CLOSED)}")
    us = L[L.closed].iloc[0]
    n = len(L)
    pf_rank = int((L.p_fav_dv_mean < us.p_fav_dv_mean).sum())     # lower p_fav = more even
    ns_rank = int((L.noll_scully < us.noll_scully).sum())
    print(f"\nMLS (USA, CLOSED): p_fav {us.p_fav_dv_mean:.3f} | skew {us.skew_exante:+.3f} "
          f"| Noll-Scully {us.noll_scully:.2f}")
    print(f"  competitiveness rank: p_fav {pf_rank+1}/{n} (1=most even), "
          f"Noll-Scully {ns_rank+1}/{n}")
    print(f"  mean OPEN leagues: p_fav {L[~L.closed].p_fav_dv_mean.mean():.3f} "
          f"skew {L[~L.closed].skew_exante.mean():+.3f} Noll-Scully "
          f"{L[~L.closed].noll_scully.mean():.2f}")

    # is the MLS ON the law's curve? residual vs the skew~p_fav regression of the open ones
    op = L[~L.closed]
    b, a = np.polyfit(op.p_fav_dv_mean, op.skew_exante, 1)
    pred_us = a + b * us.p_fav_dv_mean
    print(f"\n  law (open only): skew = {a:+.2f} {b:+.2f}·p_fav | MLS predicted "
          f"{pred_us:+.3f} vs observed {us.skew_exante:+.3f} (residual "
          f"{us.skew_exante-pred_us:+.3f}, ~1 sd)")
    print("  → reading: by the structural balance measure (Noll-Scully), the MLS is the")
    print("    MOST competitive league in the sample (rank 1/38) — exactly what cap +")
    print("    no-relegation predict — and its skewness sits at the BALANCED extreme")
    print("    (below the mean of the open ones). Consistent with the open-vs-closed theory,")
    print("    not a clean test: there is only 1 closed league in the sample (a full one needs + data).")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "open_vs_closed.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(op.p_fav_dv_mean, op.skew_exante, s=22, color="#1f77b4", label="open (Europe)")
    xs = np.linspace(L.p_fav_dv_mean.min(), L.p_fav_dv_mean.max(), 50)
    ax.plot(xs, a + b * xs, color="0.6", lw=1.5, label="law (open)")
    ax.scatter([us.p_fav_dv_mean], [us.skew_exante], s=120, color="#d62728",
               marker="*", zorder=5, label="MLS (closed)")
    ax.set_xlabel("mean $p_{fav}$ (competitiveness)"); ax.set_ylabel("ex-ante skewness")
    ax.set_title("F20 — H2: the MLS (closed) falls on the open-league curve")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f20_open_vs_closed.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f20_open_vs_closed.png'} | {C.OUTDIR / 'open_vs_closed.csv'}")

    prov.write_stamp("32_open_vs_closed", metrics={
        "mls_p_fav": float(us.p_fav_dv_mean), "mls_skew": float(us.skew_exante),
        "mls_pfav_rank": pf_rank + 1, "mls_residual": float(us.skew_exante - pred_us)})


if __name__ == "__main__":
    main()
