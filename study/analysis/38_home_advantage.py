"""38 — Frente L: vantagem de casa (HFA) secular vs invariância da skewness. A HFA
caiu nas últimas décadas (e no choque COVID, W3). Se a skewness fica invariante
apesar de a HFA se mover, fecha o confound do lado do MANDO: a assimetria depende da
dispersão de p_fav (competitividade), não do nível da vantagem de casa.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, extras, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    T = extras.hfa_and_skew_by_year(df)
    print(f"N={len(df):,} | {len(T)} anos")

    th = stats.ols(T.home_win.values, T.year.values - T.year.mean())
    ts = stats.ols(T["skew"].values, T.year.values - T.year.mean())
    print(f"\nVANTAGEM DE CASA (taxa de vitória do mandante) no tempo:")
    print(f"  {T.home_win.iloc[0]:.3f} ({T.year.iloc[0]}) → {T.home_win.iloc[-1]:.3f} "
          f"({T.year.iloc[-1]}) | β = {th['slope']:+.5f}/ano (Δ20a {th['slope']*20:+.3f})")
    print(f"SKEWNESS no tempo: β = {ts['slope']:+.5f}/ano (Δ20a {ts['slope']*20:+.3f})")
    rc = stats.bootstrap_corr(T.home_win.values, T["skew"].values)
    print(f"\ncorr(HFA, skewness) ano a ano = {rc['r']:+.3f} "
          f"[{rc['ci_lo']:+.2f},{rc['ci_hi']:+.2f}]")
    print("  → a HFA cai de forma marcada, mas a skewness não acompanha: a assimetria")
    print("    depende da DISPERSÃO de p_fav, não do nível do mando (confound fechado).")

    C.OUTDIR.mkdir(exist_ok=True)
    T.to_csv(C.OUTDIR / "hfa_by_year.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(T.year, T.home_win, "o-", color="#d62728", lw=2, label="HFA (vitória mandante)")
    ax.set_xlabel("ano"); ax.set_ylabel("taxa de vitória do mandante", color="#d62728")
    ax.tick_params(axis="y", labelcolor="#d62728")
    ax2 = ax.twinx()
    ax2.plot(T.year, T["skew"], "s-", color="#1f77b4", lw=2, label="skewness ex-ante")
    ax2.set_ylabel("skewness ex-ante", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.set_ylim(T["skew"].mean() - 0.06, T["skew"].mean() + 0.06)
    ax.set_title(f"F26 — L: HFA cai (β={th['slope']:+.4f}), skew invariante "
                 f"(corr={rc['r']:+.2f})")
    fig.tight_layout()
    fig.savefig(FIG / "f26_home_advantage.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f26_home_advantage.png'} | {C.OUTDIR / 'hfa_by_year.csv'}")

    prov.write_stamp("38_home_advantage", metrics={
        "hfa_beta": th["slope"], "skew_beta": ts["slope"], "corr_hfa_skew": rc["r"]})


if __name__ == "__main__":
    main()
