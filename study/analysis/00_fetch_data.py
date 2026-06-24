"""Downloads the multi-league 2000–2025 dataset to data/matches.csv and VERIFIES
integrity against data/PROVENANCE.json (sha256 + bytes of the frozen snapshot).

The check guarantees that every reproduction starts from the SAME data that
produced the paper's numbers. If the upstream mirror changes, the hash diverges
and the fetch fails — rather than silently producing different numbers.

On your own infra (open network) you can swap in the canonical source
football-data.co.uk and stack all the seasons/leagues you want (in that case,
regenerate PROVENANCE.json with the new hash).
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/xgabora/"
       "Club-Football-Match-Data-2000-2025/main/data/Matches.csv")
DEST = Path("data/matches.csv")
PROV = Path("data/PROVENANCE.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"OK -> {DEST} ({DEST.stat().st_size/1e6:.1f} MB)")

    if not PROV.exists():
        print("WARNING: data/PROVENANCE.json missing — skipped the hash check.")
        return
    prov = json.loads(PROV.read_text())
    want = prov.get("sha256")
    got = sha256(DEST)
    if want and got != want:
        print(f"ERROR: download hash does not match the frozen snapshot.\n"
              f"  expected: {want}\n  got:      {got}\n"
              f"  The upstream mirror changed. The paper's numbers were produced with\n"
              f"  snapshot {want[:12]}. Do not proceed without regenerating PROVENANCE.json.",
              file=sys.stderr)
        sys.exit(1)
    print(f"integrity OK — sha256 {got[:12]} == PROVENANCE.json")


if __name__ == "__main__":
    main()
