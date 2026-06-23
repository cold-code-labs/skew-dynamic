"""Carga do football-data.co.uk CANÔNICO (um CSV por liga-temporada), que traz o
que o mirror congelado NÃO tem: odds de ABERTURA (Avg*/Max*/PS*) e FECHAMENTO
(Avg*C/Max*C/PS*C), e histórico multi-book pré-2005 (WH/Ladbrokes/…). Fonte das
frentes D1 (descoberta de preço abertura→fechamento) e pré-2005 (quebra de regime).

Arquivos em `data/canonical/<SSSS>_<DIV>.csv` (SSSS = temporada football-data, ex.
2324; DIV = E0, SP1, …). Baixados por `analysis/50_fetch_canonical.py`. Não são
versionados (data/ é gitignored); congelados por `canonical_hash()`.
"""
import hashlib
import numpy as np, pandas as pd
from pathlib import Path
from . import config as C

CANON = C.DATA_PATH.parent / "canonical"

# tripletos 1X2 (favorito = argmax prob = argmin odd, invariante ao de-vig)
OPEN_AVG = ("AvgH", "AvgD", "AvgA")        # média do mercado na ABERTURA
CLOSE_AVG = ("AvgCH", "AvgCD", "AvgCA")    # média do mercado no FECHAMENTO
OPEN_MAX = ("MaxH", "MaxD", "MaxA")
CLOSE_MAX = ("MaxCH", "MaxCD", "MaxCA")
WH = ("WHH", "WHD", "WHA")                 # William Hill (book contínuo 2000→2025)


def _read_one(path):
    # CSVs antigos do football-data têm linhas raggadas (vírgulas sobrando) e
    # colunas-fantasma sem nome — pulamos linhas ruins e colunas Unnamed.
    df = pd.read_csv(path, encoding="latin1", low_memory=False, on_bad_lines="skip")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df[df["Div"].notna()] if "Div" in df.columns else df.iloc[0:0]


def load(seasons=None, divs=None, dirpath=CANON):
    """Empilha os CSVs canônicos, normaliza nomes/datas e marca a temporada.
    `seasons`/`divs` filtram (códigos football-data: '2324', 'E0'). Devolve um
    DataFrame com Division, date, season, HomeTeam, AwayTeam, FTResult, FTHome,
    FTAway, HTHome, HTAway e todas as colunas de odds presentes na fonte."""
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
        raise FileNotFoundError(f"sem CSVs canônicos em {dirpath} (rode 50_fetch_canonical.py)")
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={"Div": "Division", "FTHG": "FTHome", "FTAG": "FTAway",
                            "FTR": "FTResult", "HTHG": "HTHome", "HTAG": "HTAway"})
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date", "FTResult", "Division"])
    df = df[df.FTResult.isin(["H", "D", "A"])]
    # temporada: agosto→junho (jul como corte, igual ao resto do estudo)
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    return df.sort_values("date").reset_index(drop=True)


def with_odds(df, cols):
    """Filtra linhas com o tripleto `cols` válido (numérico > MIN_ODD) e devolve um
    frame com OddHome/OddDraw/OddAway apontando para ele — pronto p/ devig/exante."""
    g = df.copy()
    for c in cols:
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g = g[(g[cols[0]] > C.MIN_ODD) & (g[cols[1]] > C.MIN_ODD) & (g[cols[2]] > C.MIN_ODD)]
    g = g.rename(columns={cols[0]: "OddHome", cols[1]: "OddDraw", cols[2]: "OddAway"})
    return g


def canonical_hash(dirpath=CANON):
    """Hash determinístico do conjunto canônico (lista de arquivos + bytes), p/
    congelar a proveniência das frentes que usam dado externo."""
    h = hashlib.sha256()
    files = sorted(Path(dirpath).glob("*.csv"))
    for f in files:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return {"sha256": h.hexdigest()[:16], "files": len(files)}
