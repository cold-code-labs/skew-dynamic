"""Downloads tennis results+odds (tennis-data.co.uk) to data/tennis.csv.

One .xlsx file per year and per tour (ATP/WTA). Keeps a normalised subset:
tour, Date, Series/Tier, Surface, Round, Winner, Loser, and the winner/loser odds
(B365W/L, PSW/L, AvgW/L, MaxW/L) when present.

ToS: tennis-data.co.uk is free for research but restricts redistribution — the
data/tennis.csv is NOT versioned (regenerable by this script). Needs network and
`openpyxl` (pip install openpyxl).

Usage:
    python analysis/00b_fetch_tennis.py                 # ATP+WTA, 2010–2025
    python analysis/00b_fetch_tennis.py --tour atp --from 2005 --to 2025
"""
import argparse
import sys
import pandas as pd
from pathlib import Path

# NB: tennis-data.co.uk HTTPS is broken (TLSV1_ALERT_INTERNAL_ERROR);
# the site serves the files over plain HTTP.
BASE = "http://www.tennis-data.co.uk"
KEEP = ["tour", "Date", "Series", "Tier", "Surface", "Court", "Round", "Best of",
        "Winner", "Loser", "WRank", "LRank",
        "B365W", "B365L", "PSW", "PSL", "AvgW", "AvgL", "MaxW", "MaxL"]
DEST = Path("data/tennis.csv")


def _url(tour, year):
    # ATP: /<year>/<year>.xlsx ; WTA: /<year>w/<year>.xlsx
    suffix = "" if tour == "atp" else "w"
    return f"{BASE}/{year}{suffix}/{year}.xlsx"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tour", choices=["atp", "wta", "both"], default="both")
    ap.add_argument("--from", dest="y0", type=int, default=2010)
    ap.add_argument("--to", dest="y1", type=int, default=2025)
    a = ap.parse_args()

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        sys.exit("ERROR: install openpyxl (`pip install openpyxl`) to read the .xlsx files.")

    tours = ["atp", "wta"] if a.tour == "both" else [a.tour]
    frames = []
    for tour in tours:
        for year in range(a.y0, a.y1 + 1):
            url = _url(tour, year)
            try:
                df = pd.read_excel(url)
            except Exception as e:
                print(f"  skipped {tour} {year}: {e}")
                continue
            df["tour"] = tour.upper()
            frames.append(df[[c for c in KEEP if c in df.columns]])
            print(f"  ok {tour} {year}: {len(df)} matches")

    if not frames:
        sys.exit("nothing downloaded (no network or source unavailable).")
    out = pd.concat(frames, ignore_index=True)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(DEST, index=False)
    print(f"-> {DEST} ({len(out):,} matches, {out.tour.nunique()} tours)")


if __name__ == "__main__":
    main()
