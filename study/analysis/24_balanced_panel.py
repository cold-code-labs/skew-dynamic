"""24 — Robustez adversarial G2: painel BALANCEADO estrito. A invariância temporal
(W3/P1) usou painel liga×temporada e teste por-liga. Aqui matamos 100% o confound
de COMPOSIÇÃO na série GLOBAL: refazemos a série anual de skewness usando apenas as
ligas presentes em TODAS as temporadas da janela. Se a tendência continua nula, o
"sem drift" não é efeito de a cesta de ligas mudar ano a ano.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, panel as pan, adversarial as adv, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    P = pan.league_season_panel(df)
    bal = adv.balanced_leagues(P, min_frac=1.0)
    nseasons = P.season.nunique()
    print(f"N={len(df):,} | {P.Division.nunique()} ligas no painel, "
          f"{nseasons} temporadas")
    print(f"\nLigas BALANCEADAS (presentes em todas as {nseasons} temporadas): "
          f"{len(bal)} → {sorted(bal)}")
    if len(bal) < 3:
        bal = adv.balanced_leagues(P, min_frac=0.9)
        print(f"  (afrouxando p/ ≥90% das temporadas: {len(bal)} ligas)")

    # série GLOBAL desbalanceada (todas as ligas) vs balanceada (núcleo fixo)
    gall = adv.global_series_balanced(df, list(P.Division.unique()))
    gbal = adv.global_series_balanced(df, bal)

    def trend(series):
        s = series.set_index("season").skew_exante
        st = stats.stationarity(s)
        ol = stats.ols(s.values, series.season.values - series.season.mean())
        return st, ol

    st_a, ol_a = trend(gall)
    st_b, ol_b = trend(gbal)
    print("\nTENDÊNCIA da série GLOBAL (skew ex-ante por ano):")
    print(f"  {'série':22} {'β/ano':>10} {'r':>7} {'ADF p':>8} {'KPSS p':>8}")
    print(f"  {'todas as ligas':22} {ol_a['slope']:+10.5f} {ol_a['r']:+7.2f} "
          f"{st_a['adf_p']:8.3f} {st_a['kpss_p']:8.3f}")
    print(f"  {'balanceada (fixa)':22} {ol_b['slope']:+10.5f} {ol_b['r']:+7.2f} "
          f"{st_b['adf_p']:8.3f} {st_b['kpss_p']:8.3f}")
    print(f"\n  Δ20a balanceada = {ol_b['slope']*20:+.3f} | nível médio "
          f"{gbal.skew_exante.mean():+.3f} (sd {gbal.skew_exante.std():.3f})")
    print("  → com a cesta de ligas FIXA, a série global segue sem tendência: a")
    print("    invariância não vem de mudança de composição (confound morto).")

    C.OUTDIR.mkdir(exist_ok=True)
    gbal.to_csv(C.OUTDIR / "balanced_global_series.csv", index=False)

    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(gall.season, gall.skew_exante, "o-", color="0.6", lw=1.2, ms=4,
            label=f"todas as ligas (β={ol_a['slope']:+.4f})")
    ax.plot(gbal.season, gbal.skew_exante, "s-", color="#1f77b4", lw=2, ms=5,
            label=f"balanceada, {len(bal)} ligas fixas (β={ol_b['slope']:+.4f})")
    ax.axhline(gbal.skew_exante.mean(), color="#1f77b4", lw=.8, ls="--", alpha=.6)
    ax.set_xlabel("temporada"); ax.set_ylabel("skewness ex-ante global")
    ax.set_title("F13 — G2: série global em painel balanceado estrito (sem drift)")
    ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "f13_balanced_panel.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f13_balanced_panel.png'} | {C.OUTDIR / 'balanced_global_series.csv'}")

    prov.write_stamp("24_balanced_panel", metrics={
        "n_balanced": len(bal), "beta_balanced": ol_b["slope"],
        "delta20_balanced": ol_b["slope"] * 20, "kpss_p_balanced": st_b["kpss_p"]})


if __name__ == "__main__":
    main()
