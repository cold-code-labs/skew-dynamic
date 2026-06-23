"""Testes do adaptador de tênis — sintéticos, SEM dataset (rodam em CI).

Validam o mapeamento winner/loser → canônico e a semântica do favourite-longshot
(favorito = menor odd; venceu quando o vencedor era o favorito).
    cd study && python -m pytest tests/test_tennis_adapter.py -q
"""
import sys
import pathlib
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from skewlib import canonical            # noqa: E402
from skewlib.adapters import tennis      # noqa: E402


def _raw():
    """Dado bruto tennis-data-like. Partida 0: favorito venceu (W odd baixa).
    Partida 1: ZEBRA — o vencedor era o azarão (W odd alta)."""
    return pd.DataFrame({
        "Date": ["2020-01-06", "2020-01-07"],
        "Series": ["ATP250", "Grand Slam"],
        "Surface": ["Hard", "Clay"],
        "Winner": ["Player A", "Player D"],
        "Loser": ["Player B", "Player C"],
        "B365W": [1.30, 4.50],     # odd do vencedor
        "B365L": [3.50, 1.22],     # odd do perdedor
    })


def test_to_canonical_schema_and_invariants():
    can = tennis.to_canonical(_raw())
    assert canonical.validate(can)
    assert set(can.outcome) == {"winner", "loser"}
    assert can.market.iloc[0] == "match_odds" and can.sport.iloc[0] == "tennis"
    # 2 eventos × 2 resultados
    assert len(can) == 4 and can.event_id.nunique() == 2


def test_favourite_longshot_semantics():
    can = tennis.to_canonical(_raw())
    fav = canonical.select(can, "fav")        # menor odd por evento
    # evento 0: favorito = vencedor (odd 1.30) → bet do favorito GANHOU (won=1)
    e0 = fav[fav.event_id == 0].iloc[0]
    assert e0.o == 1.30 and e0.won == 1
    # evento 1: favorito = perdedor (odd 1.22) → favorito PERDEU (zebra, won=0)
    e1 = fav[fav.event_id == 1].iloc[0]
    assert e1.o == 1.22 and e1.won == 0
    # sem objeto de empate
    assert tennis.DRAW_ROLE is None
    assert canonical.signature(canonical.select(can, "draw", draw_role="draw")) is None


def test_signature_runs_on_two_outcomes():
    can = tennis.to_canonical(_raw())
    sig = canonical.signature(canonical.select(can, "fav"), "fav")
    assert sig is not None and np.isfinite(sig["skew"]) and sig["n"] == 2
