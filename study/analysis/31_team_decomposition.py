"""31 — Micro F3: do dominant clubs "pull" the league's signature? Decomposition by
team: for each club, its dominance (mean Elo) and the mean ex-ante skewness of the
matches it plays. Dominant clubs generate unbalanced matches (strong favourites
⇒ negative skew); the league's skew signature reflects its strength dispersion at the
team level — the micro version of the law skewness=f(competitiveness).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, intraleague as il, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    T = il.team_dominance(df, min_games=200).dropna(subset=["elo"])
    print(f"N={len(df):,} | {len(T)} teams with Elo and ≥200 matches")

    r = stats.bootstrap_corr(T.elo.values, T.skew_games.values)
    print(f"\ncorr(team Elo, mean skew of its matches) = {r['r']:+.3f} "
          f"[{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}]")
    print("  (high Elo ⇒ more unbalanced matches ⇒ lower match skew)")
    top = T.nlargest(5, "elo")[["team", "elo", "fav_rate", "skew_games"]]
    bot = T.nsmallest(5, "elo")[["team", "elo", "fav_rate", "skew_games"]]
    print("\n  most DOMINANT clubs (Elo):")
    for x in top.itertuples():
        print(f"    {x.team:18} Elo {x.elo:.0f} · favourite {x.fav_rate:.0%} · "
              f"match skew {x.skew_games:+.3f}")
    print("  WEAKEST clubs:")
    for x in bot.itertuples():
        print(f"    {x.team:18} Elo {x.elo:.0f} · favourite {x.fav_rate:.0%} · "
              f"match skew {x.skew_games:+.3f}")

    # does the league's Elo dispersion predict the league's skew?
    lg = T.groupby("Division").agg(elo_sd=("elo", "std")).reset_index()
    lsk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante"]]
    M = lg.merge(lsk, on="Division")
    rl = stats.bootstrap_corr(M.elo_sd.values, M.skew_exante.values)
    print(f"\ncorr(league Elo dispersion, league skew) = {rl['r']:+.3f} "
          f"[{rl['ci_lo']:+.2f},{rl['ci_hi']:+.2f}]")
    print("  → the league's skew signature is a function of its strength dispersion at the")
    print("    TEAM level (the law skewness=f(competitiveness), seen from within).")

    C.OUTDIR.mkdir(exist_ok=True)
    T.sort_values("elo").to_csv(C.OUTDIR / "team_dominance.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(T.elo, T.skew_games, s=10, color="#1f77b4", alpha=.5)
    axes[0].set_xlabel("team mean Elo (dominance)")
    axes[0].set_ylabel("mean skew of the team's matches")
    axes[0].set_title(f"Teams: dominance vs skew (r={r['r']:+.2f})")
    axes[1].scatter(M.elo_sd, M.skew_exante, s=22, color="#d62728")
    axes[1].set_xlabel("league Elo dispersion"); axes[1].set_ylabel("league skew")
    axes[1].set_title(f"Leagues: strength dispersion vs skew (r={rl['r']:+.2f})")
    fig.suptitle("F19 — F3: the league signature comes from the strength dispersion of teams", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f19_team_decomposition.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f19_team_decomposition.png'} | {C.OUTDIR / 'team_dominance.csv'}")

    prov.write_stamp("31_team_decomposition", metrics={
        "corr_elo_teamskew": r["r"], "corr_elosd_leagueskew": rl["r"]})


if __name__ == "__main__":
    main()
