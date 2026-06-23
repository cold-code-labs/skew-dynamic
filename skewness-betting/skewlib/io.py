"""Carga e limpeza do dataset."""
import pandas as pd
from . import config as C

ODD_COLS = ["OddHome", "OddDraw", "OddAway"]
MAX_COLS = ["MaxHome", "MaxDraw", "MaxAway"]


def load(path=None, year_min=None):
    """Carrega o CSV, parseia datas, remove linhas inválidas e ordena por data."""
    path = path or C.DATA_PATH
    year_min = year_min if year_min is not None else C.YEAR_MIN
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df["MatchDate"], errors="coerce")
    df = df.dropna(subset=["date", *ODD_COLS, "FTResult", "Division"])
    df = df[df["date"].dt.year >= year_min]
    for c in ODD_COLS:                      # remove odds inválidas (dado sujo)
        df = df[df[c] > C.MIN_ODD]
    return df.sort_values("date").reset_index(drop=True)
