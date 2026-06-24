"""47 — CANONICAL layer: validation + multi-market demonstration.

Not a new evidence front: it is the verification that the canonical abstraction
(skewlib/canonical + adapters) REPRODUCES the frozen football path and generalises
to 2-outcome markets. See docs/DATA-SCHEMA.md.

  A) Equivalence: canonical.bettype_by(football:1x2) == exante.bettype_by — bit-for-bit.
  B) Generality: the same core measures the over/under 2.5 market (n=2 outcomes).
"""
import numpy as np
from skewlib import io, returns, exante, canonical
from skewlib.adapters import football


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,}", flush=True)

    # A) EQUIVALENCE — the canonical path reproduces exante.bettype_by exactly
    ref = exante.bettype_by(df, min_n=2000).set_index("Division").sort_index()
    can = football.to_canonical(df)
    canonical.validate(can)
    bt = canonical.bettype_by(can, by="competition", min_n=2000) \
        .set_index("competition").sort_index()
    cols = ["skew_fav", "skew_draw", "skew_dog", "p_fav_mean"]
    diff = float(np.max(np.abs(ref[cols].to_numpy() - bt.loc[ref.index, cols].to_numpy())))
    print(f"\nA) EQUIVALENCE canonical vs frozen ({len(ref)} leagues): "
          f"max|Δ| = {diff:.2e}")
    assert diff < 1e-9, f"DRIFT: the canonical path diverged from the frozen one ({diff:.2e})"
    print("   ✓ bit-identical — the abstraction changes no football number.")

    # B) GENERALITY — the same core measures a 2-outcome market (over/under)
    ou = football.OU.to_canonical(df)
    canonical.validate(ou)
    n_ev = ou.event_id.nunique()
    sig_over = canonical.signature(canonical.select(ou, "fav"), "fav")
    sig_dog = canonical.signature(canonical.select(ou, "dog"), "dog")
    sig_draw = canonical.signature(canonical.select(ou, "draw", football.OU.DRAW_ROLE))
    print(f"\nB) over/under 2.5 MARKET ({n_ev:,} events, 2 outcomes):")
    print(f"   favourite skew (more likely side)  = {sig_over['skew']:+.3f}")
    print(f"   underdog skew  (less likely side)  = {sig_dog['skew']:+.3f}")
    print(f"   'draw' bet = {sig_draw}  (market without draw → None)")
    assert sig_draw is None, "O/U should not have a draw object"
    print("\n  → the core (canonical + skewmeter) is sport/market-agnostic; "
          "adding a sport = one adapter.")


if __name__ == "__main__":
    main()
