"""50 — baixa o football-data.co.uk CANÔNICO (um CSV por liga-temporada) para
`data/canonical/`. Fonte das frentes de DADO EXTERNO: D1 (abertura→fechamento,
precisa das colunas *C* de fechamento, ~2019/20+) e pré-2005 (histórico 1X2
multi-book, 2000/01+). O mirror congelado (data/matches.csv) não traz nem
abertura/fechamento separados nem profundidade pré-2005.

Idempotente: pula arquivos já presentes. Servidor sensível a rajadas — usa urllib
com User-Agent e pausa entre requisições (curl em loop rápido é bloqueado).
"""
import sys, time, urllib.request
from pathlib import Path
from skewlib import config as C

DST = C.DATA_PATH.parent / "canonical"
# ligas principais cobertas pelo caminho mmz4281 (top + 2ª divisões europeias)
DIVS = ["E0", "E1", "E2", "E3", "SC0", "SC1", "SC2", "SC3", "D1", "D2", "I1", "I2",
        "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
# temporadas football-data: SSSS = 2 dígitos do ano de início + 2 do fim
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
    print(f"canonical: novos {ok} | sem dado {miss} | já tinha {skip} | "
          f"total {len(list(DST.glob('*.csv')))} arquivos em {DST}")


if __name__ == "__main__":
    fetch()
