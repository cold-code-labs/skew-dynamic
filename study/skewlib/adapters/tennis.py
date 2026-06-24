"""TENNIS adapter → canonical table (match-odds market, 2 outcomes, no draw).

Source: tennis-data.co.uk (sister of football-data.co.uk) — ATP/WTA, one file per
year with results + bookmaker odds. The odds are labelled by the realised outcome:
B365W/B365L = odds of the match WINNER / LOSER (likewise PSW/PSL, AvgW/AvgL,
MaxW/MaxL). So each match has two betting objects — the winner (odds W,
won=1) and the loser (odds L, won=0) — and the FAVOURITE is the one with the lower
odd (= higher p), which is sometimes the winner and sometimes the loser (upset). It
is the standard favourite-longshot setup in tennis, and maps exactly onto the
canonical contract.

Fetch the data with `python analysis/00b_fetch_tennis.py` (see there: the ToS
restricts redistribution; the raw data is not versioned). Then:
    from skewlib.adapters import tennis
    can = tennis.to_canonical()               # reads data/tennis.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path
from .. import canonical, config as C

SPORT = "tennis"
MARKET = "match_odds"
OUTCOMES = ["winner", "loser"]
ROLES = {"winner": "won", "loser": "lost"}
DRAW_ROLE = None                                   # tennis has no draw

DATA = Path("data/tennis.csv")
# odds sources, in order of preference (winner/loser pair)
ODDS_SOURCES = [("B365W", "B365L"), ("PSW", "PSL"), ("AvgW", "AvgL"), ("MaxW", "MaxL")]
COMP_CANDIDATES = ["Series", "Tier", "Surface"]    # analogue of "league" in tennis


def _load(path=None):
    path = Path(path or DATA)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run `python analysis/00b_fetch_tennis.py` "
            f"(needs network + openpyxl).")
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    return df


def _pick(df, candidates, label):
    """First candidate present. Each candidate is a column (str) or a pair
    of columns (tuple) that must exist together."""
    for c in candidates:
        if isinstance(c, str):
            if c in df.columns:
                return c
        elif all(x in df.columns for x in c):
            return c
    raise KeyError(f"no {label} column found: {candidates}")


def to_canonical(df=None, odds=None, comp_col=None):
    """Maps the tennis data to the canonical table. `odds` = pair (winner_col,
    loser_col); `comp_col` = grouping column (default: Series/Tier/Surface)."""
    if df is None:
        df = _load()
    df = df.copy()
    if "date" not in df.columns:                       # raw df passed directly
        df["date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    ow, ol = odds or _pick(df, ODDS_SOURCES, "odds")
    d = df.dropna(subset=[ow, ol, "Winner", "Loser", "date"]).copy()
    d = d[(d[ow] > C.MIN_ODD) & (d[ol] > C.MIN_ODD)].reset_index(drop=True)
    # competition: coalesce the candidates (ATP uses Series, WTA uses Tier, …)
    if comp_col:
        comp = d[comp_col].astype(str)
    else:
        present = [c for c in COMP_CANDIDATES if c in d.columns]
        if not present:
            raise KeyError(f"no competition column: {COMP_CANDIDATES}")
        comp = d[present[0]]
        for c in present[1:]:
            comp = comp.fillna(d[c])
        comp = comp.astype(str)
    n = len(d)
    base = pd.DataFrame({
        "event_id": np.arange(n),
        "sport": SPORT, "market": MARKET,
        "competition": comp.to_numpy(),
        "date": d["date"].to_numpy(),
    })
    parts = []
    for oc, oddcol, won in [("winner", ow, 1), ("loser", ol, 0)]:
        part = base.copy()
        part["outcome"] = oc
        part["role"] = ROLES[oc]
        part["odds"] = d[oddcol].to_numpy(float)
        part["p"] = np.nan
        part["won"] = won
        parts.append(part)
    out = pd.concat(parts, ignore_index=True)
    return canonical.devig(out)[canonical.SCHEMA]
