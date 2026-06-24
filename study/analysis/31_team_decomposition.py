"""31 — Micro F3: clubes dominantes "puxam" a assinatura da liga? Decomposição por
time: para cada clube, sua dominância (Elo médio) e a skewness ex-ante média dos
jogos que disputa. Clubes dominantes geram jogos desequilibrados (favoritos fortes
⇒ skew negativa); a assinatura de skew da liga reflete sua dispersão de força no
nível dos times — a versão micro da lei skewness=f(competitividade).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, intraleague as il, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    T = il.team_dominance(df, min_games=200).dropna(subset=["elo"])
    print(f"N={len(df):,} | {len(T)} times com Elo e ≥200 jogos")

    r = stats.bootstrap_corr(T.elo.values, T.skew_games.values)
    print(f"\ncorr(Elo do time, skew média dos seus jogos) = {r['r']:+.3f} "
          f"[{r['ci_lo']:+.2f},{r['ci_hi']:+.2f}]")
    print("  (Elo alto ⇒ jogos mais desequilibrados ⇒ skew dos jogos mais baixa)")
    top = T.nlargest(5, "elo")[["team", "elo", "fav_rate", "skew_games"]]
    bot = T.nsmallest(5, "elo")[["team", "elo", "fav_rate", "skew_games"]]
    print("\n  clubes mais DOMINANTES (Elo):")
    for x in top.itertuples():
        print(f"    {x.team:18} Elo {x.elo:.0f} · favorito {x.fav_rate:.0%} · "
              f"skew jogos {x.skew_games:+.3f}")
    print("  clubes mais FRACOS:")
    for x in bot.itertuples():
        print(f"    {x.team:18} Elo {x.elo:.0f} · favorito {x.fav_rate:.0%} · "
              f"skew jogos {x.skew_games:+.3f}")

    # dispersão de Elo da liga prevê a skew da liga?
    lg = T.groupby("Division").agg(elo_sd=("elo", "std")).reset_index()
    lsk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante"]]
    M = lg.merge(lsk, on="Division")
    rl = stats.bootstrap_corr(M.elo_sd.values, M.skew_exante.values)
    print(f"\ncorr(dispersão de Elo da liga, skew da liga) = {rl['r']:+.3f} "
          f"[{rl['ci_lo']:+.2f},{rl['ci_hi']:+.2f}]")
    print("  → a assinatura de skew da liga é função da sua dispersão de força no")
    print("    nível dos TIMES (a lei skewness=f(competitividade), vista por dentro).")

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
