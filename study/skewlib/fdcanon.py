"""Loading of the CANONICAL football-data.co.uk (one CSV per league-season), which
brings what the frozen mirror does NOT have: OPENING odds (Avg*/Max*/PS*) and
CLOSING odds (Avg*C/Max*C/PS*C), and pre-2005 multi-book history
(WH/Ladbrokes/…). Source for fronts D1 (opening→closing price discovery) and
pre-2005 (regime break).

Files in `data/canonical/<SSSS>_<DIV>.csv` (SSSS = football-data season, e.g.
2324; DIV = E0, SP1, …). Fetched by `analysis/50_fetch_canonical.py`. They are not
versioned (data/ is gitignored); frozen by `canonical_hash()`.
"""
import hashlib
import numpy as np, pandas as pd
from pathlib import Path
from . import config as C

CANON = C.DATA_PATH.parent / "canonical"

# 1X2 triplets (favourite = argmax prob = argmin odd, invariant to the de-vig)
OPEN_AVG = ("AvgH", "AvgD", "AvgA")        # market average at the OPENING
CLOSE_AVG = ("AvgCH", "AvgCD", "AvgCA")    # market average at the CLOSING
OPEN_MAX = ("MaxH", "MaxD", "MaxA")
CLOSE_MAX = ("MaxCH", "MaxCD", "MaxCA")
WH = ("WHH", "WHD", "WHA")                 # William Hill (continuous book 2000→2025)


def _read_one(path):
    # old football-data CSVs have ragged rows (extra commas) and unnamed
    # phantom columns — we skip bad lines and Unnamed columns.
    df = pd.read_csv(path, encoding="latin1", low_memory=False, on_bad_lines="skip")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df[df["Div"].notna()] if "Div" in df.columns else df.iloc[0:0]


def load(seasons=None, divs=None, dirpath=CANON):
    """Stacks the canonical CSVs, normalises names/dates and marks the season.
    `seasons`/`divs` filter (football-data codes: '2324', 'E0'). Returns a
    DataFrame with Division, date, season, HomeTeam, AwayTeam, FTResult, FTHome,
    FTAway, HTHome, HTAway and all the odds columns present in the source."""
    frames = []
    for f in sorted(Path(dirpath).glob("*.csv")):
        try:
            season, div = f.stem.split("_", 1)
        except ValueError:
            continue
        if seasons and season not in seasons:
            continue
        if divs and div not in divs:
            continue
        g = _read_one(f)
        if len(g):
            frames.append(g)
    if not frames:
        raise FileNotFoundError(f"no canonical CSVs in {dirpath} (run 50_fetch_canonical.py)")
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={"Div": "Division", "FTHG": "FTHome", "FTAG": "FTAway",
                            "FTR": "FTResult", "HTHG": "HTHome", "HTAG": "HTAway"})
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date", "FTResult", "Division"])
    df = df[df.FTResult.isin(["H", "D", "A"])]
    # season: august→june (jul as the cutoff, same as the rest of the study)
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    return df.sort_values("date").reset_index(drop=True)


def with_odds(df, cols):
    """Filters rows with a valid `cols` triplet (numeric > MIN_ODD) and returns a
    frame with OddHome/OddDraw/OddAway pointing to it — ready for devig/exante."""
    g = df.copy()
    for c in cols:
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g = g[(g[cols[0]] > C.MIN_ODD) & (g[cols[1]] > C.MIN_ODD) & (g[cols[2]] > C.MIN_ODD)]
    g = g.rename(columns={cols[0]: "OddHome", cols[1]: "OddDraw", cols[2]: "OddAway"})
    return g


def canonical_hash(dirpath=CANON):
    """Deterministic hash of the canonical set (file list + bytes), to
    freeze the provenance of the fronts that use external data."""
    h = hashlib.sha256()
    files = sorted(Path(dirpath).glob("*.csv"))
    for f in files:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return {"sha256": h.hexdigest()[:16], "files": len(files)}
