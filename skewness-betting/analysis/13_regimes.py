"""13 — Regime vs invariância (P1): a tese é invariância INTRA-REGIME.

A literatura (Lee & Fort 2012; Basini et al. 2023) acha quebras estruturais reais
na competitividade da EPL, ligadas a choques institucionais — Champions League
(1994/95), Bosman (1995), desigualdade de receita (~2003). TODOS anteriores ao
nosso recorte ≥2005. Predição sob a visão de regime: DENTRO de 2005–2025
(regime moderno único) deve haver poucas quebras e SEM ano comum entre ligas.
Testamos exatamente isso.
"""
from skewlib import io, returns, exante, panel, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = panel.league_season_panel(df)

    print("=== Quebras por liga dentro de 2005–2025 (PELT conservador) ===")
    bks = panel.league_breaks(pan)
    n_leagues = pan[pan.groupby("Division").Division.transform("size") >= 10].Division.nunique()
    print(f"  ligas testadas (≥10 temporadas): {n_leagues}")
    print(f"  quebras detectadas: {len(bks)} em {bks.Division.nunique()} ligas")
    if len(bks):
        print(bks.sort_values("break_season").to_string(index=False,
              formatters={"shift": "{:+.3f}".format}))
        print("\n  Histograma de ANO de quebra (regime market-wide = ano comum):")
        h = bks.break_season.value_counts().sort_index()
        for yr, c in h.items():
            print(f"    {yr}: {'█'*c} ({c})")
        print(f"  → máx. de ligas quebrando no MESMO ano: {h.max()} "
              f"({'sem regime comum' if h.max() <= 2 else 'possível regime comum'})")
        sh = bks["shift"]  # bks.shift colidiria com DataFrame.shift()
        print(f"  → salto médio |.| nas quebras: {sh.abs().mean():.3f} "
              f"(vs sd between-liga 0.052) | sinal misto: "
              f"{(sh>0).sum()}↑ / {(sh<0).sum()}↓")

    print("\n=== Foco EPL (E0) — Lee & Fort acham regimes PRÉ-1995/2003 ===")
    e0 = pan[pan.Division == "E0"].sort_values("season")
    print(f"  E0 skewness 2005–2025: média={e0.skew_exante.mean():.3f} "
          f"sd={e0.skew_exante.std():.3f} "
          f"range=[{e0.skew_exante.min():.3f},{e0.skew_exante.max():.3f}]")
    e0bk = bks[bks.Division == "E0"]
    print(f"  quebras E0 no nosso recorte: {len(e0bk)} "
          f"→ {'estável intra-regime (consistente: choques EPL são pré-2005)' if len(e0bk)==0 else 'investigar'}")

    print("\n=== Enquadramento ===")
    print("  Choques de regime (Bosman 95, CL 94/95, ~2003) são ANTERIORES ao recorte.")
    print("  2005–2025 ≈ regime moderno único → 'sem tendência' = invariância")
    print("  INTRA-REGIME, não atemporalidade absoluta. Baseline é específico da liga.")


if __name__ == "__main__":
    main()
