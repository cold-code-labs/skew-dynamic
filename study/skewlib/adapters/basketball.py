"""BASKETBALL adapter → canonical table (moneyline market, 2 outcomes, no draw).

Source: sportsbookreviewsonline.com — one page per season (NBA), each GAME on
TWO rows (away V, home H) with the final score + the American moneyline (ML). The
odds are labelled by side (away/home); each game has two betting objects — the
away side (odd V) and the home side (odd H) — and the FAVOURITE is the one with the
lower odd (= higher p), which wins most of the time but occasionally suffers an
upset. Basketball has no draw (goes to overtime). It is the standard
favourite-longshot setup, identical to tennis, and maps exactly onto the canonical
contract.

Fetch the data with `python analysis/00c_fetch_basketball.py` (needs network; no
extra dependencies — uses `html.parser` from the stdlib). Then:
    from skewlib.adapters import basketball
    can = basketball.to_canonical()             # reads data/basketball.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path
from .. import canonical, config as C

SPORT = "basketball"
MARKET = "moneyline"
OUTCOMES = ["away", "home"]
ROLES = {"away": "away", "home": "home"}
DRAW_ROLE = None                                   # basketball has no draw

DATA = Path("data/basketball.csv")
MAX_OVERROUND = 1.25                                # sane band for the sum of implied p
COMP_COL = "season"                                # analogue of "league" (NBA season)


def _ml_to_dec(ml):
    """American moneyline → decimal odd. +150 → 2.50; -200 → 1.50."""
    ml = pd.to_numeric(ml, errors="coerce").to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(ml > 0, 1.0 + ml / 100.0, 1.0 + 100.0 / np.abs(ml))


def _load(path=None):
    path = Path(path or DATA)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run `python analysis/00c_fetch_basketball.py` "
            f"(needs network).")
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    return df


def to_canonical(df=None, comp_col=COMP_COL):
    """Maps the basketball data to the canonical table. `comp_col` = grouping
    column (default: season — league competitiveness varies year to year)."""
    if df is None:
        df = _load()
    df = df.copy()
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    oV = _ml_to_dec(df["ml_v"])
    oH = _ml_to_dec(df["ml_h"])
    over = 1.0 / oV + 1.0 / oH
    keep = (np.isfinite(oV) & np.isfinite(oH)
            & (oV > C.MIN_ODD) & (oH > C.MIN_ODD)
            & (over > 1.0) & (over < MAX_OVERROUND)
            & df["pts_v"].notna().to_numpy() & df["pts_h"].notna().to_numpy()
            & (df["pts_v"].to_numpy() != df["pts_h"].to_numpy()))
    d = df[keep].reset_index(drop=True)
    oV, oH = oV[keep], oH[keep]
    won_v = (d["pts_v"].to_numpy(float) > d["pts_h"].to_numpy(float)).astype(int)
    comp = (d[comp_col].astype(str) if comp_col in d.columns
            else pd.Series([SPORT] * len(d)))
    n = len(d)
    base = pd.DataFrame({
        "event_id": np.arange(n),
        "sport": SPORT, "market": MARKET,
        "competition": comp.to_numpy(),
        "date": d["date"].to_numpy(),
    })
    parts = []
    for oc, odds, won in [("away", oV, won_v), ("home", oH, 1 - won_v)]:
        part = base.copy()
        part["outcome"] = oc
        part["role"] = ROLES[oc]
        part["odds"] = np.asarray(odds, float)
        part["p"] = np.nan
        part["won"] = won
        parts.append(part)
    out = pd.concat(parts, ignore_index=True)
    return canonical.devig(out)[canonical.SCHEMA]
