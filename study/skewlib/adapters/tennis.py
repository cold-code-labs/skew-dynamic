"""Adaptador TÊNIS → tabela canônica (mercado match-odds, 2 resultados, sem empate).

Fonte: tennis-data.co.uk (irmã da football-data.co.uk) — ATP/WTA, um arquivo por
ano com resultados + odds de casas. As odds são rotuladas pelo resultado realizado:
B365W/B365L = odds do VENCEDOR / PERDEDOR da partida (idem PSW/PSL, AvgW/AvgL,
MaxW/MaxL). Logo cada partida tem dois objetos de aposta — o vencedor (odds W,
won=1) e o perdedor (odds L, won=0) — e o FAVORITO é o de menor odd (= maior p),
que às vezes é o vencedor e às vezes o perdedor (zebra). É o setup padrão do
favourite-longshot em tênis, e cai exatamente no contrato canônico.

Baixe o dado com `python analysis/00b_fetch_tennis.py` (ver lá: ToS restringe
redistribuição; o bruto não é versionado). Depois:
    from skewlib.adapters import tennis
    can = tennis.to_canonical()               # lê data/tennis.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path
from .. import canonical, config as C

SPORT = "tennis"
MARKET = "match_odds"
OUTCOMES = ["winner", "loser"]
ROLES = {"winner": "won", "loser": "lost"}
DRAW_ROLE = None                                   # tênis não tem empate

DATA = Path("data/tennis.csv")
# fontes de odds, em ordem de preferência (par vencedor/perdedor)
ODDS_SOURCES = [("B365W", "B365L"), ("PSW", "PSL"), ("AvgW", "AvgL"), ("MaxW", "MaxL")]
COMP_CANDIDATES = ["Series", "Tier", "Surface"]    # análogo de "liga" em tênis


def _load(path=None):
    path = Path(path or DATA)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} ausente — rode `python analysis/00b_fetch_tennis.py` "
            f"(precisa de rede + openpyxl).")
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    return df


def _pick(df, candidates, label):
    """Primeiro candidato presente. Cada candidato é uma coluna (str) ou um par
    de colunas (tupla) que precisam existir juntas."""
    for c in candidates:
        if isinstance(c, str):
            if c in df.columns:
                return c
        elif all(x in df.columns for x in c):
            return c
    raise KeyError(f"nenhuma coluna de {label} encontrada: {candidates}")


def to_canonical(df=None, odds=None, comp_col=None):
    """Mapeia o dado de tênis para a tabela canônica. `odds` = par (col_vencedor,
    col_perdedor); `comp_col` = coluna de agrupamento (default: Series/Tier/Surface)."""
    if df is None:
        df = _load()
    df = df.copy()
    if "date" not in df.columns:                       # df cru passado direto
        df["date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    ow, ol = odds or _pick(df, ODDS_SOURCES, "odds")
    comp = comp_col or _pick(df, COMP_CANDIDATES, "competição")
    d = df.dropna(subset=[ow, ol, "Winner", "Loser", "date"]).copy()
    d = d[(d[ow] > C.MIN_ODD) & (d[ol] > C.MIN_ODD)].reset_index(drop=True)
    n = len(d)
    base = pd.DataFrame({
        "event_id": np.arange(n),
        "sport": SPORT, "market": MARKET,
        "competition": d[comp].astype(str).to_numpy(),
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
