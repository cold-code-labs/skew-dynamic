"""47 — camada CANÔNICA: validação + demonstração multi-mercado.

Não é uma frente nova de evidência: é a verificação de que a abstração canônica
(skewlib/canonical + adapters) REPRODUZ o caminho de futebol congelado e generaliza
para mercados de 2 resultados. Ver docs/DATA-SCHEMA.md.

  A) Equivalência: canonical.bettype_by(football:1x2) == exante.bettype_by — bit-a-bit.
  B) Generalidade: o mesmo núcleo mede o mercado over/under 2.5 (n=2 resultados).
"""
import numpy as np
from skewlib import io, returns, exante, canonical
from skewlib.adapters import football


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,}", flush=True)

    # A) EQUIVALÊNCIA — a via canônica reproduz exante.bettype_by exatamente
    ref = exante.bettype_by(df, min_n=2000).set_index("Division").sort_index()
    can = football.to_canonical(df)
    canonical.validate(can)
    bt = canonical.bettype_by(can, by="competition", min_n=2000) \
        .set_index("competition").sort_index()
    cols = ["skew_fav", "skew_draw", "skew_dog", "p_fav_mean"]
    diff = float(np.max(np.abs(ref[cols].to_numpy() - bt.loc[ref.index, cols].to_numpy())))
    print(f"\nA) EQUIVALÊNCIA canônico vs congelado ({len(ref)} ligas): "
          f"max|Δ| = {diff:.2e}")
    assert diff < 1e-9, f"DRIFT: a via canônica divergiu do congelado ({diff:.2e})"
    print("   ✓ bit-idêntico — a abstração não muda nenhum número de futebol.")

    # B) GENERALIDADE — o mesmo núcleo mede um mercado de 2 resultados (over/under)
    ou = football.OU.to_canonical(df)
    canonical.validate(ou)
    n_ev = ou.event_id.nunique()
    sig_over = canonical.signature(canonical.select(ou, "fav"), "fav")
    sig_dog = canonical.signature(canonical.select(ou, "dog"), "dog")
    sig_draw = canonical.signature(canonical.select(ou, "draw", football.OU.DRAW_ROLE))
    print(f"\nB) MERCADO over/under 2.5 ({n_ev:,} eventos, 2 resultados):")
    print(f"   skew do favorito (lado mais provável) = {sig_over['skew']:+.3f}")
    print(f"   skew do azarão  (lado menos provável) = {sig_dog['skew']:+.3f}")
    print(f"   aposta de 'empate' = {sig_draw}  (mercado sem empate → None)")
    assert sig_draw is None, "O/U não deveria ter objeto de empate"
    print("\n  → o núcleo (canonical + skewmeter) é sport/mercado-agnóstico; "
          "adicionar um esporte = um adaptador.")


if __name__ == "__main__":
    main()
