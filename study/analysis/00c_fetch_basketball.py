"""Baixa resultados+odds da NBA (sportsbookreviewsonline.com) para data/basketball.csv.

Uma página HTML por temporada; cada JOGO aparece em duas linhas (visitante V, casa H)
com placares por período, placar final e a moneyline americana (ML). Mantém um
subconjunto normalizado, UM JOGO por linha: season, date, visitor, home, pts_v, pts_h,
ml_v, ml_h (moneyline americana inteira). O par é considerado um jogo válido só se
ambos os placares e ambas as moneylines são numéricos, não houve empate e |ML| ≥ 100
(uma moneyline de verdade nunca fica entre −100 e +100; valores menores são spreads que
vazaram para a coluna). A de-vig, a conversão p/ odd decimal e a limpeza de overround
ficam no adaptador (`skewlib/adapters/basketball.py`).

Sem dependências extras: a tabela é lida com `html.parser` da stdlib (o site não serve
mais .xlsx). ToS do sportsbookreviewsonline restringe redistribuição — o
data/basketball.csv NÃO é versionado (regenerável por este script).

Uso:
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
# o certificado às vezes falha a validação; o conteúdo é público e conferido por hash
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE
_UA = {"User-Agent": "Mozilla/5.0"}


class _Rows(HTMLParser):
    """Extrai todas as linhas <tr> de células <td>/<th> (texto), sem libs externas."""
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
    """A tabela de jogos é a de maior largura modal (Date, Rot, VH, …, ML, …)."""
    p = _Rows()
    p.feed(html)
    if not p.rows:
        raise ValueError("nenhuma tabela na página")
    width = Counter(len(r) for r in p.rows).most_common(1)[0][0]
    rows = [r for r in p.rows if len(r) == width]
    t = pd.DataFrame(rows)
    t.columns = list(t.iloc[0])
    return t.iloc[1:].reset_index(drop=True)


def _mk_date(mmdd, y0, y1):
    """Date 'MMDD' (3–4 dígitos) + temporada → data real (Out–Dez=y0, Jan–Jun=y1)."""
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
        if a["VH"] != "V" or b["VH"] != "H":          # par desalinhado: pula
            continue
        fa = pd.to_numeric(a["Final"], errors="coerce")
        fb = pd.to_numeric(b["Final"], errors="coerce")
        ma = pd.to_numeric(a["ML"], errors="coerce")
        mb = pd.to_numeric(b["ML"], errors="coerce")
        if np.isnan([fa, fb, ma, mb]).any() or fa == fb:
            continue
        if abs(ma) < 100 or abs(mb) < 100:            # moneyline real: |ML| ≥ 100
            continue
        rows.append({"season": season, "date": _mk_date(a["Date"], y0, y1),
                     "visitor": a.get("Team", ""), "home": b.get("Team", ""),
                     "pts_v": int(fa), "pts_h": int(fb), "ml_v": int(ma), "ml_h": int(mb)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="y0", type=int, default=2007)
    ap.add_argument("--to", dest="y1", type=int, default=2022)   # ano inicial da temporada
    a = ap.parse_args()

    frames = []
    for y in range(a.y0, a.y1 + 1):
        season = f"{y}-{str(y + 1)[2:]}"
        try:
            df = _season(season, y, y + 1)
        except Exception as e:
            print(f"  pulado {season}: {e}")
            continue
        if len(df):
            frames.append(df)
            print(f"  ok {season}: {len(df)} jogos")

    if not frames:
        sys.exit("nada baixado (sem rede ou fonte indisponível).")
    out = pd.concat(frames, ignore_index=True)[KEEP]
    DEST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(DEST, index=False)
    print(f"-> {DEST} ({len(out):,} jogos, {out.season.nunique()} temporadas)")


if __name__ == "__main__":
    main()
