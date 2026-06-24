"""Source adapters → CANONICAL table (see docs/DATA-SCHEMA.md).

Each adapter maps a raw dataset of a sport/market to the canonical contract
and declares its outcome taxonomy. The core (`skewlib.canonical` +
`skewlib.skewmeter`) is sport-agnostic and never changes. Adding a sport =
writing a module here and registering it in REGISTRY.
"""
from . import football, tennis, basketball

REGISTRY = {
    "football:1x2": football,            # 3 outcomes (H/D/A)
    "football:ou25": football.OU,        # 2 outcomes (over/under 2.5)
    "tennis:match_odds": tennis,         # 2 outcomes (winner/loser), no draw
    "basketball:moneyline": basketball,  # 2 outcomes (home/away), no draw
}


def get(name):
    """Adapter by name 'sport:market' (e.g. 'football:1x2')."""
    if name not in REGISTRY:
        raise KeyError(f"unknown adapter: {name}. Available: {list(REGISTRY)}")
    return REGISTRY[name]
