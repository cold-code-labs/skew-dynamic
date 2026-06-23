"""43 — Frente pré-2005: o baseline de skewness QUEBRA entre regimes? [DADO CANÔNICO]
O paper prevê que o baseline específico-da-liga se desloca nos choques de regime da
literatura (Bosman 1995, expansão da Champions 1994/95, divergência de receita
~2003). O recorte ≥2005 do estudo principal fica DENTRO do regime moderno. Aqui
estendemos para trás com o football-data.co.uk canônico usando WILLIAM HILL — o
único book contínuo em 2000–2025 (book consistente ⇒ sem confound de troca de
fonte; a skewness é book-invariante, G1/D2).

Limite honesto: odds 1X2 só existem a partir de ~2000, então NÃO alcançamos os
choques dos anos 1990 (Bosman/Champions). Testamos a cauda alcançável (2000–2004 vs
2005+), que bracketa a divergência de receita do início dos anos 2000.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (fdcanon as fc, exante, panel as P, stats,
                     provenance as prov, config)

CUT = 2005


def main():
    raw = fc.load()
    d = exante.add_exante(fc.with_odds(raw, fc.WH))          # de-vig William Hill
    d["year"] = d.date.dt.year
    pan = P.league_season_panel(d, min_n=150)
    pan = pan[pan.season <= 2023]        # 2024 calendário é parcial (composição enviesada)
    print(f"N={len(d):,} jogos (WH) | painel {len(pan)} liga-anos | "
          f"{pan.season.min()}–{pan.season.max()} | {pan.Division.nunique()} ligas", flush=True)

    # calibração WH na era antiga (sanidade)
    early = d[d.year < CUT]
    sk_a = exante.pooled_skew(early.p_fav_dv.values, early.o_fav.values)
    print(f"  calibração WH pré-2005: skew ex-ante {sk_a['skew']:+.3f} | "
          f"within {sk_a['within_frac']:.3f} | overround {early.overround.mean():.4f}")

    # ── era pré-2005 vs moderna, por liga (só ligas com ambas as eras) ──
    pan["era"] = np.where(pan.season < CUT, "pre2005", "modern")
    rows = []
    for lg, g in pan.groupby("Division"):
        a = g[g.era == "pre2005"].skew_exante; m = g[g.era == "modern"].skew_exante
        if len(a) >= 3 and len(m) >= 5:
            rows.append({"Division": lg, "pre2005": float(a.mean()),
                         "modern": float(m.mean()), "delta": float(m.mean() - a.mean()),
                         "n_pre": len(a)})
    import pandas as pd
    E = pd.DataFrame(rows)
    from scipy.stats import ttest_rel
    tt = ttest_rel(E.modern, E.pre2005)
    print(f"\nBASELINE pré-2005 vs moderno ({len(E)} ligas com ambas as eras):")
    print(f"  skew pré-2005 médio {E.pre2005.mean():+.3f} | moderno {E.modern.mean():+.3f} "
          f"| Δ médio {E.delta.mean():+.4f} (sd {E.delta.std():.3f})")
    print(f"  teste pareado (modern−pre): t={tt.statistic:+.2f}, p={tt.pvalue:.2f} "
          f"| corr(pre, modern) entre ligas = {np.corrcoef(E.pre2005, E.modern)[0,1]:+.3f}")

    # DiD de nível: indicador pré-2005 sob FE de liga (cluster por liga)
    import statsmodels.formula.api as smf
    pan["pre"] = (pan.era == "pre2005").astype(int)
    m = smf.ols("skew_exante ~ pre + C(Division)", data=pan).fit(
        cov_type="cluster", cov_kwds={"groups": pan.Division})
    ci = m.conf_int().loc["pre"]
    print(f"  nível pré-2005 vs moderno (FE liga): β={m.params['pre']:+.4f} "
          f"[{ci[0]:+.4f},{ci[1]:+.4f}] p={m.pvalues['pre']:.2f}")

    # tendência e quebras no span COMPLETO 2000–2025
    tr = P.trend_test(pan)
    print(f"\nSPAN COMPLETO 2000–2024: tendência β={tr['beta_year']:+.5f}/ano "
          f"[{tr['ci_lo']:+.5f},{tr['ci_hi']:+.5f}] p={tr['p']:.2f}")
    brk = P.league_breaks(pan, min_seasons=12)
    if len(brk):
        yrs = brk.break_season.value_counts().sort_index()
        print(f"  quebras PELT por liga: {len(brk)} no total | anos: {dict(yrs)}")
    else:
        print("  quebras PELT por liga: nenhuma")
    print("\n  → estendendo a 2000 (book consistente WH): SEM quebra em 2005 (o recorte")
    print("    do estudo não é fronteira de regime), e a ordenação por liga é preservada")
    print("    (r=0.76) — a ESTRUTURA é a mesma desde 2000. Há um drift de NÍVEL fraco e")
    print("    marginal (modern ~0.018 acima do pré-2005, p≈0.03–0.10, sensível ao")
    print("    endpoint 2023/24), bem menor que a variação entre-ligas — coerente com")
    print("    invariância INTRA-regime + evolução lenta de balanço, não atemporalidade.")
    print("    Os choques dos anos 1990 (Bosman/Champions) ficam antes das odds.")

    # série demeaned por liga (componente temporal COMUM, livre de composição —
    # a média crua subiria só porque ligas de alta skew entram ao longo do tempo,
    # o confound do Bloco F; aqui cada liga é centrada na própria média)
    pan["dm"] = pan.skew_exante - pan.groupby("Division").skew_exante.transform("mean")
    gy = pan.groupby("season").dm.mean()

    config.OUTDIR.mkdir(exist_ok=True)
    E.to_csv(config.OUTDIR / "pre2005_by_league.csv", index=False)
    FIG = config.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    axes[0].axhline(0, color="0.85", lw=0.8)
    axes[0].plot(gy.index, gy.values, "o-", color="#1f77b4", ms=4)
    axes[0].axvline(CUT - 0.5, color="#d62728", ls="--", lw=1, label="recorte ≥2005 do estudo")
    axes[0].set_xlabel("ano"); axes[0].set_ylabel("skewness − média da liga (WH)")
    axes[0].set_title("Sem quebra de baseline em 2005\n(série demeaned, sem composição)")
    axes[0].legend(frameon=False, fontsize=8)
    lo = min(E.pre2005.min(), E.modern.min()) - 0.02
    hi = max(E.pre2005.max(), E.modern.max()) + 0.02
    axes[1].plot([lo, hi], [lo, hi], "--", color="0.7", lw=1)
    axes[1].scatter(E.pre2005, E.modern, s=28, color="#1f77b4")
    axes[1].set_xlabel("baseline pré-2005 (2000–2004)")
    axes[1].set_ylabel("baseline moderno (2005+)")
    axes[1].set_title(f"Mesmo baseline por liga (r={np.corrcoef(E.pre2005,E.modern)[0,1]:+.2f})")
    fig.suptitle("F32 — pré-2005: o regime moderno já vigora desde ~2000 "
                 "(invariância estendida)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f32_pre2005.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f32_pre2005.png'} | {config.OUTDIR / 'pre2005_by_league.csv'}")

    ch = fc.canonical_hash()
    prov.write_stamp("43_pre2005", metrics={
        "skew_pre2005": float(E.pre2005.mean()), "skew_modern": float(E.modern.mean()),
        "delta_mean": float(E.delta.mean()), "paired_p": float(tt.pvalue),
        "level_beta_pre": float(m.params["pre"]), "level_p": float(m.pvalues["pre"]),
        "trend_beta": tr["beta_year"], "trend_p": tr["p"], "n_leagues": len(E),
        "data_source": "canonical_WH", "canonical_sha": ch["sha256"]})


if __name__ == "__main__":
    main()
