"""09 — Invariância temporal (W3): painel liga×temporada.

Mostra que a skewness ex-ante é (i) sem tendência secular, (ii) dominada por
variância between-liga (o invariante estrutural) e não within-liga, (iii) sem
quebras por liga, e (iv) imune ao choque de vantagem de casa da COVID.
"""
from skewlib import io, returns, exante, panel, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = panel.league_season_panel(df)
    print(f"painel: {len(pan)} obs liga×temporada | "
          f"{pan.Division.nunique()} ligas | {pan.season.min()}–{pan.season.max()}")

    print("\n=== Tendência secular (FE de liga + ano, SE cluster) ===")
    t = panel.trend_test(pan)
    print(f"  β_ano = {t['beta_year']:+.5f}/ano  SE={t['se']:.5f}  p={t['p']:.3f}  "
          f"IC95%[{t['ci_lo']:+.5f},{t['ci_hi']:+.5f}]  (n={t['n_obs']})")
    print(f"  → deriva em 20 anos ≈ {t['beta_year']*20:+.4f} "
          f"(vs sd between-liga ~0.06) — {'sem tendência' if t['p']>0.05 else 'TENDÊNCIA'}")

    print("\n=== Decomposição de variância ===")
    v = panel.variance_decomp(pan)
    se = panel.sampling_se(df)
    print(f"  sd between-liga = {v['sd_between']:.4f}  (o invariante estrutural)")
    print(f"  sd within-liga  = {v['sd_within']:.4f}  (flutuação temporal)")
    print(f"  SE amostral médio (bootstrap dos jogos) = {se:.4f}")
    print(f"  → within ({v['sd_within']:.4f}) ≈ ruído amostral ({se:.4f}): "
          f"{'flutuação é amostral' if se >= 0.8*v['sd_within'] else 'há sinal temporal real'}")
    print(f"  ICC = {v['icc']:.3f}  → {v['icc']*100:.0f}% da variância é entre ligas")

    print("\n=== Tendências/quebras por liga ===")
    pl = panel.per_league_trends(pan)
    big = pl[pl.slope_per_year.abs() > 0.003]
    print(f"  ligas com |slope|>0.003/ano: {len(big)}/{len(pl)}")
    print(f"  slope médio |.| = {pl.slope_per_year.abs().mean():.5f}/ano | "
          f"quebras totais = {pl.n_breaks.clip(lower=0).sum()} "
          f"(ligas com ≥1 quebra: {(pl.n_breaks>0).sum()})")

    print("\n=== Vinheta COVID (estádios vazios 2020/21) ===")
    hw = panel.home_win_rate_by_year(df)
    for y in (2018, 2019, 2020, 2021, 2022):
        if y in hw.index:
            print(f"  taxa vitória mandante {y}: {hw[y]:.3f}")
    cov = panel.covid_vignette(pan)
    print(f"  desvio da skewness 2020 vs média da liga: z médio (com sinal) = "
          f"{cov.z.mean():+.2f} | |z| médio = {cov.z.abs().mean():.2f}  "
          f"(ligas com z>0: {(cov.z>0).sum()}/{len(cov)})")
    print("  → HFA cai (mandante mais fraco → mais paridade); a lei prevê skewness ↑.")
    print("    z médio com sinal positivo = choque de competitividade moveu a skewness")
    print("    na direção prevista (corrobora a causa; não contradiz a invariância secular).")

    C.OUTDIR.mkdir(exist_ok=True)
    pan.to_csv(C.OUTDIR / "panel_league_season.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'panel_league_season.csv'}")


if __name__ == "__main__":
    main()
