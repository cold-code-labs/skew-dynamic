"""Downloads NBA results+odds (sportsbookreviewsonline.com) to data/basketball.csv.

One HTML page per season; each GAME appears on two rows (visitor V, home H) with
per-period scores, final score and the American moneyline (ML). Keeps a normalised
subset, ONE GAME per row: season, date, visitor, home, pts_v, pts_h, ml_v, ml_h
(integer American moneyline). The pair is treated as a valid game only if both
scores and both moneylines are numeric, there was no tie and |ML| ≥ 100 (a real
moneyline never sits between −100 and +100; smaller values are spreads that leaked
into the column). The de-vig, conversion to decimal odds and overround cleanup
live in the adapter (`skewlib/adapters/basketball.py`).

No extra dependencies: the table is read with the stdlib `html.parser` (the site no
longer serves .xlsx). The sportsbookreviewsonline ToS restricts redistribution — the
data/basketball.csv is NOT versioned (regenerable by this script).

Usage:
    python analysis/00c_fetch_basketball.py                 # NBA, 2007–08 … 2022–23
    python analysis/00c_fetch_basketball.py --from 2010 --to 2022
"""
import argparse
import ssl
import sys
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import pandas as pd

BASE = "https://www.sportsbookreviewsonline.com/scoresoddsarchives"
DEST = Path("data/basketball.csv")
KEEP = ["season", "date", "visitor", "home", "pts_v", "pts_h", "ml_v", "ml_h"]
# the certificate sometimes fails validation; the content is public and checked by hash
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE
_UA = {"User-Agent": "Mozilla/5.0"}


class _Rows(HTMLParser):
    """Extracts all <tr> rows of <td>/<th> cells (text), without external libs."""
    def __init__(self):
        super().__init__()
        self.rows, self._cur, self._cell, self._buf = [], None, False, []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._cur = []
        elif tag in ("td", "th") and self._cur is not None:
            self._cell, self._buf = True, []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell:
            self._cur.append("".join(self._buf).strip())
            self._cell = False
        elif tag == "tr" and self._cur is not None:
            if self._cur:
                self.rows.append(self._cur)
            self._cur = None

    def handle_data(self, data):
        if self._cell:
            self._buf.append(data)


def _biggest_table(html):
    """The games table is the one with the modal (most common) width (Date, Rot, VH, …, ML, …)."""
    p = _Rows()
    p.feed(html)
    if not p.rows:
        raise ValueError("no table on the page")
    width = Counter(len(r) for r in p.rows).most_common(1)[0][0]
    rows = [r for r in p.rows if len(r) == width]
    t = pd.DataFrame(rows)
    t.columns = list(t.iloc[0])
    return t.iloc[1:].reset_index(drop=True)


def _mk_date(mmdd, y0, y1):
    """Date 'MMDD' (3–4 digits) + season → real date (Oct–Dec=y0, Jan–Jun=y1)."""
    s = str(mmdd).strip()
    if not s.isdigit() or len(s) < 3:
        return pd.NaT
    mm, dd = int(s[:-2]), int(s[-2:])
    yr = y0 if mm >= 8 else y1
    return pd.Timestamp(year=yr, month=mm, day=dd) if 1 <= mm <= 12 and 1 <= dd <= 31 else pd.NaT


def _season(season, y0, y1):
    url = f"{BASE}/nba-odds-{season}"
    req = urllib.request.Request(url, headers=_UA)
    html = urllib.request.urlopen(req, timeout=120, context=_CTX).read().decode("latin-1")
    t = _biggest_table(html)
    t = t[t["VH"].isin(["V", "H"])].reset_index(drop=True)
    rows = []
    for i in range(0, len(t) - 1, 2):
        a, b = t.iloc[i], t.iloc[i + 1]
        if a["VH"] != "V" or b["VH"] != "H":          # misaligned pair: skip
            continue
        fa = pd.to_numeric(a["Final"], errors="coerce")
        fb = pd.to_numeric(b["Final"], errors="coerce")
        ma = pd.to_numeric(a["ML"], errors="coerce")
        mb = pd.to_numeric(b["ML"], errors="coerce")
        if np.isnan([fa, fb, ma, mb]).any() or fa == fb:
            continue
        if abs(ma) < 100 or abs(mb) < 100:            # real moneyline: |ML| ≥ 100
            continue
        rows.append({"season": season, "date": _mk_date(a["Date"], y0, y1),
                     "visitor": a.get("Team", ""), "home": b.get("Team", ""),
                     "pts_v": int(fa), "pts_h": int(fb), "ml_v": int(ma), "ml_h": int(mb)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="y0", type=int, default=2007)
    ap.add_argument("--to", dest="y1", type=int, default=2022)   # starting year of the season
    a = ap.parse_args()

    frames = []
    for y in range(a.y0, a.y1 + 1):
        season = f"{y}-{str(y + 1)[2:]}"
        try:
            df = _season(season, y, y + 1)
        except Exception as e:
            print(f"  skipped {season}: {e}")
            continue
        if len(df):
            frames.append(df)
            print(f"  ok {season}: {len(df)} games")

    if not frames:
        sys.exit("nothing downloaded (no network or source unavailable).")
    out = pd.concat(frames, ignore_index=True)[KEEP]
    DEST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(DEST, index=False)
    print(f"-> {DEST} ({len(out):,} games, {out.season.nunique()} seasons)")


if __name__ == "__main__":
    main()
