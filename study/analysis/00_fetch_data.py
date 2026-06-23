"""Baixa o dataset multi-liga 2000–2025 para data/matches.csv.

Na sua infra (rede liberada) você pode trocar pela fonte canônica
football-data.co.uk e empilhar todas as temporadas/ligas que quiser.
"""
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/xgabora/"
       "Club-Football-Match-Data-2000-2025/main/data/Matches.csv")
DEST = Path("data/matches.csv")


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"baixando {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"OK -> {DEST} ({DEST.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
