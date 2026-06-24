"""50 — downloads the CANONICAL football-data.co.uk (one CSV per league-season) into
`data/canonical/`. Source for the EXTERNAL DATA fronts: D1 (opening→closing, needs the
closing *C* columns, ~2019/20+) and pre-2005 (historical multi-book 1X2, 2000/01+).
The frozen mirror (data/matches.csv) carries neither separate opening/closing odds nor
pre-2005 depth.

Idempotent: skips files already present. The server is burst-sensitive — uses urllib
with a User-Agent and a pause between requests (a fast curl loop gets blocked).
"""
import sys, time, urllib.request
from pathlib import Path
from skewlib import config as C

DST = C.DATA_PATH.parent / "canonical"
# main leagues covered by the mmz4281 path (top + 2nd European divisions)
DIVS = ["E0", "E1", "E2", "E3", "SC0", "SC1", "SC2", "SC3", "D1", "D2", "I1", "I2",
        "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
# football-data seasons: SSSS = 2 digits of the start year + 2 of the end year
SEASONS = [f"{y%100:02d}{(y+1)%100:02d}" for y in range(2000, 2025)]   # 0001 … 2425
UA = "Mozilla/5.0 (research; skew-dynamic; coldcodelabs.com)"


def fetch(seasons=SEASONS, divs=DIVS, pause=0.25):
    DST.mkdir(parents=True, exist_ok=True)
    ok = miss = skip = 0
    for s in seasons:
        for d in divs:
            f = DST / f"{s}_{d}.csv"
            if f.exists() and f.stat().st_size > 0:
                skip += 1; continue
            url = f"https://www.football-data.co.uk/mmz4281/{s}/{d}.csv"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    b = r.read()
                if b[:4].startswith(b"Div,"):
                    f.write_bytes(b); ok += 1
                else:
                    miss += 1
            except Exception:
                miss += 1
            time.sleep(pause)
    print(f"canonical: new {ok} | no data {miss} | already had {skip} | "
          f"total {len(list(DST.glob('*.csv')))} files in {DST}")


if __name__ == "__main__":
    fetch()
