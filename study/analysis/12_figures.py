"""12 — Paper figures (F1–F4). Saves PNGs to outputs/fig/.

F1 FLB: skew (ex-ante & ex-post) vs p_fav + identity curve (1-2p)/√(p(1-p))
F2 Law: skewness by league vs odds-free competitiveness (Elo upset rate)
F3 Decomposition of M₃ (within/cov/between)
F4 League×season panel: absence of trend
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import skew
from skewlib import io, returns, exante, elo, panel, config as C

FIG = C.OUTDIR / "fig"


def fig1_flb(df):
    edges = [0, .4, .45, .5, .55, .6, .7, 1.0]
    df = df.copy(); df["b"] = pd.cut(df.p_fav_dv, edges)
    xs, ea, ep = [], [], []
    for b, g in df.groupby("b", observed=True):
        if len(g) < 200: continue
        xs.append(g.p_fav_dv.mean())
        ea.append(exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"])
        ep.append(skew(g.ret_fav.values))
    p = np.linspace(0.30, 0.85, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(p, (1 - 2 * p) / np.sqrt(p * (1 - p)), color="0.6", lw=1.5,
            label=r"identity $(1-2p)/\sqrt{p(1-p)}$")
    ax.plot(xs, ea, "o-", color="#1f77b4", label="ex-ante (de-vigged)")
    ax.plot(xs, ep, "s--", color="#d62728", label="ex-post (realised)")
    ax.axhline(0, color="k", lw=.5); ax.axvline(0.5, color="k", lw=.5, ls=":")
    ax.set_xlabel("favourite probability $p_{fav}$"); ax.set_ylabel("skewness")
    ax.set_title("F1 — Favorite-longshot bias: skewness = image of $p$")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "f1_flb.png", dpi=C.FIG_DPI); plt.close(fig)


def fig2_law(league):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(league.upset_rate, league.skew_exante, s=18, color="#1f77b4")
    b, a = np.polyfit(league.upset_rate, league.skew_exante, 1)
    xs = np.linspace(league.upset_rate.min(), league.upset_rate.max(), 50)
    r = np.corrcoef(league.upset_rate, league.skew_exante)[0, 1]
    ax.plot(xs, a + b * xs, color="0.5", lw=1, label=f"r = {r:+.2f}")
    for _, row in league.iterrows():
        ax.annotate(row.Division, (row.upset_rate, row.skew_exante),
                    fontsize=6, alpha=.6, xytext=(2, 2), textcoords="offset points")
    ax.set_xlabel("upset rate (Elo, odds-free)"); ax.set_ylabel("league ex-ante skewness")
    ax.set_title("F2 — Structural law: skewness ~ competitiveness (odds-free)")
    ax.legend(frameon=False); fig.tight_layout()
    fig.savefig(FIG / "f2_law.png", dpi=C.FIG_DPI); plt.close(fig)


def fig3_decomp(df):
    g = exante.pooled_skew(df.p_fav_dv.values, df.o_fav.values)
    parts = [("within-match\n(mechanical/FLB)", g["within_frac"]),
             ("covariance", g["cov_frac"]), ("between matches", g["between_frac"])]
    fig, ax = plt.subplots(figsize=(5, 4))
    cols = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    ax.bar([p[0] for p in parts], [p[1] * 100 for p in parts], color=cols)
    for i, p in enumerate(parts):
        ax.text(i, p[1] * 100, f"{p[1]*100:+.1f}%", ha="center",
                va="bottom" if p[1] >= 0 else "top", fontsize=9)
    ax.axhline(0, color="k", lw=.5); ax.set_ylabel("% of 3rd moment $M_3$")
    ax.set_title("F3 — Skewness decomposition (total cumulants)")
    fig.tight_layout(); fig.savefig(FIG / "f3_decomp.png", dpi=C.FIG_DPI); plt.close(fig)


def fig4_panel(pan):
    fig, ax = plt.subplots(figsize=(6, 4))
    for _, g in pan.groupby("Division"):
        g = g.sort_values("season")
        ax.plot(g.season, g.skew_exante, color="0.8", lw=.6)
    m = pan.groupby("season").skew_exante.mean()
    ax.plot(m.index, m.values, color="#d62728", lw=2, label="between-league mean")
    b, a = np.polyfit(pan.season, pan.skew_exante, 1)
    ax.plot(m.index, a + b * m.index, color="k", ls="--", lw=1,
            label=f"trend {b:+.4f}/year")
    ax.set_xlabel("season"); ax.set_ylabel("ex-ante skewness (league×season)")
    ax.set_title("F4 — Temporal invariance: no drift over 20 years")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f4_panel.png", dpi=C.FIG_DPI); plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    df = exante.add_exante(returns.add_returns(io.load()))
    fig1_flb(df); print("F1 ok")
    fig3_decomp(df); print("F3 ok")
    fig4_panel(panel.league_season_panel(df)); print("F4 ok")
    print("running Elo for F2...", flush=True)
    d = elo.with_elo(df)
    league = exante.pooled_by(df, "Division", min_n=2000).merge(
        elo.league_competitiveness(d).drop(columns="n"), on="Division")
    fig2_law(league); print("F2 ok")
    print(f"-> {FIG}/*.png")


if __name__ == "__main__":
    main()
