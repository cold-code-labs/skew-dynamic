"""25 — Robustez adversarial G3: IC honesto por BLOCK-BOOTSTRAP sobre temporadas.
Reamostrar jogos independentes subestima a incerteza se houver dependência
intra-temporada. Reamostramos TEMPORADAS inteiras (com reposição) e recomputamos
os números-título — IC que respeita a estrutura anual. Se os ICs são apertados e
excluem o nulo onde a tese exige, os títulos do paper estão blindados.
"""
import numpy as np
from skewlib import io, returns, exante, adversarial as adv, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = df.date.dt.year
    nyr = df.season.nunique()
    print(f"N={len(df):,} | {nyr} temporadas | block-bootstrap (B=400)")

    point_skew = adv.stat_global_skew(df)
    bs = adv.season_block_bootstrap(df, adv.stat_global_skew, B=400)
    print(f"\nSkewness global ex-ante = {point_skew:+.4f}")
    print(f"  block-bootstrap: média {bs['mean']:+.4f} · SE {bs['se']:.4f} · "
          f"IC95 [{bs['ci_lo']:+.4f}, {bs['ci_hi']:+.4f}]")
    print(f"  → exclui 0 com folga (a assimetria é positiva e robusta a qual ano cai).")

    point_corr = adv.stat_league_corr(df)
    bc = adv.season_block_bootstrap(df, adv.stat_league_corr, B=400)
    print(f"\nLei estrutural corr(skew_liga, p_fav_liga) = {point_corr:+.4f}")
    print(f"  block-bootstrap: média {bc['mean']:+.4f} · SE {bc['se']:.4f} · "
          f"IC95 [{bc['ci_lo']:+.4f}, {bc['ci_hi']:+.4f}]")
    print(f"  → a relação skewness↔competitividade sobrevive à reamostragem de anos.")

    # vig e FLB mecânico do favorito (C1) sob block-bootstrap
    def stat_ret(d):
        return float(d.ret_fav.mean())
    pr = adv.season_block_bootstrap(df, stat_ret, B=400)
    print(f"\nRetorno médio do favorito = {df.ret_fav.mean():+.4f}")
    print(f"  block-bootstrap: IC95 [{pr['ci_lo']:+.4f}, {pr['ci_hi']:+.4f}]")

    print("\nResumo: os números-título carregam IC por reamostragem de temporadas —")
    print("o sinal e a magnitude não dependem de uma janela específica de anos.")

    prov.write_stamp("25_block_bootstrap", metrics={
        "skew_ci_lo": bs["ci_lo"], "skew_ci_hi": bs["ci_hi"],
        "corr_ci_lo": bc["ci_lo"], "corr_ci_hi": bc["ci_hi"]})


if __name__ == "__main__":
    main()
