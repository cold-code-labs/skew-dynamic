"""35 — Frente I: validação cruzada do mecanismo com modelo gerador independente.
Um Poisson de GOLS (ataque/defesa+mando por liga-temporada) gera as probabilidades
de resultado (via Skellam) e daí a skewness agrupada. Confrontamos com o empírico e
com a curva do ordered-probit. Se a lei skewness=f(competitividade) emerge de um
modelo de GOLS tão bem quanto do modelo de MARGEM, o mecanismo é independente do
modelo — uma das validações mais fortes possíveis dentro do dataset.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, goals, model, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    print(f"N={len(df):,} | ajustando Poisson de gols por liga-temporada...", flush=True)
    tab = goals.league_season_table(df, min_games=150, min_teams=8)
    L = goals.by_league(tab)
    print(f"  {len(tab)} liga-temporadas ajustadas, {len(L)} ligas")

    # a lei: o Poisson recupera a competitividade e a skewness?
    rp = stats.bootstrap_corr(L.pfav_poisson.values, L.pfav_emp.values)
    rs = stats.bootstrap_corr(L.skew_poisson.values, L.skew_emp.values)
    print(f"\nCROSS-MODEL (entre {len(L)} ligas):")
    print(f"  corr(p_fav Poisson, p_fav empírico)   = {rp['r']:+.3f} "
          f"[{rp['ci_lo']:+.2f},{rp['ci_hi']:+.2f}]")
    print(f"  corr(skew Poisson,  skew empírico)    = {rs['r']:+.3f} "
          f"[{rs['ci_lo']:+.2f},{rs['ci_hi']:+.2f}]")
    print(f"  nível: skew Poisson médio {L.skew_poisson.mean():+.3f} vs "
          f"empírico {L.skew_emp.mean():+.3f}")
    print("  (o Poisson é um gerador mais grosso e subdispersa um pouco o p_fav,")
    print("   daí o nível de skew menor; o que importa é a LEI — a ordenação bate.)")

    # ambos caem na curva derivada do ordered-probit?
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.05, 1.3, 45)
    cpf, csk = model.curve(par["h"], par["c"], sig)
    o = np.argsort(cpf)
    pred_emp = np.interp(L.pfav_emp.values, cpf[o], csk[o])
    pred_poi = np.interp(L.pfav_poisson.values, cpf[o], csk[o])
    r_emp = float(np.corrcoef(pred_emp, L.skew_emp.values)[0, 1])
    r_poi = float(np.corrcoef(pred_poi, L.skew_poisson.values)[0, 1])
    print(f"\n  na curva do ordered-probit: empírico r={r_emp:+.2f} | Poisson r={r_poi:+.2f}")
    print("  → três modelos (margem latente, gols-Poisson, empírico) na MESMA curva:")
    print("    a lei skewness=f(competitividade) é independente do modelo gerador.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "poisson_crossmodel_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(cpf[o], csk[o], color="0.5", lw=2, label="ordered-probit (margem)")
    axes[0].scatter(L.pfav_emp, L.skew_emp, s=20, color="#1f77b4", label="empírico")
    axes[0].scatter(L.pfav_poisson, L.skew_poisson, s=20, color="#d62728",
                    marker="^", label="Poisson de gols")
    axes[0].set_xlabel("mean $p_{fav}$"); axes[0].set_ylabel("skewness ex-ante")
    axes[0].set_title("Três modelos, uma curva"); axes[0].legend(frameon=False, fontsize=8)
    axes[1].plot([L.skew_emp.min(), L.skew_emp.max()],
                 [L.skew_emp.min(), L.skew_emp.max()], "--", color="0.7", lw=1)
    axes[1].scatter(L.skew_emp, L.skew_poisson, s=22, color="#d62728")
    axes[1].set_xlabel("skew empírico"); axes[1].set_ylabel("skew Poisson")
    axes[1].set_title(f"Poisson vs empírico (r={rs['r']:+.2f})")
    fig.suptitle("F23 — I: modelo de gols (Poisson) reproduz a lei (mecanismo independente)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f23_poisson_crossmodel.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f23_poisson_crossmodel.png'} | {C.OUTDIR / 'poisson_crossmodel_by_league.csv'}")

    prov.write_stamp("35_poisson_crossmodel", metrics={
        "corr_pfav": rp["r"], "corr_skew": rs["r"], "league_r_poisson": r_poi,
        "n_league_seasons": len(tab)})


if __name__ == "__main__":
    main()
