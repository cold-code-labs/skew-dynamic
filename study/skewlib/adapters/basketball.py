"""Adaptador BASQUETE → tabela canônica (mercado moneyline, 2 resultados, sem empate).

Fonte: sportsbookreviewsonline.com — uma página por temporada (NBA), cada JOGO em
DUAS linhas (visitante V, casa H) com placar final + a moneyline americana (ML). As
odds são rotuladas pelo lado (visitante/casa); cada jogo tem dois objetos de aposta —
o visitante (odd V) e a casa (odd H) — e o FAVORITO é o de menor odd (= maior p), que
vence na maioria das vezes mas às vezes leva a zebra. Basquete não tem empate (vai à
prorrogação). É o setup padrão do favourite-longshot, idêntico ao do tênis, e cai
exatamente no contrato canônico.

Baixe o dado com `python analysis/00c_fetch_basketball.py` (precisa de rede; sem
dependências extras — usa `html.parser` da stdlib). Depois:
    from skewlib.adapters import basketball
    can = basketball.to_canonical()             # lê data/basketball.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path
from .. import canonical, config as C

SPORT = "basketball"
MARKET = "moneyline"
OUTCOMES = ["away", "home"]
ROLES = {"away": "away", "home": "home"}
DRAW_ROLE = None                                   # basquete não tem empate

DATA = Path("data/basketball.csv")
MAX_OVERROUND = 1.25                                # banda sã da soma de p implícitas
COMP_COL = "season"                                # análogo de "liga" (temporada NBA)


def _ml_to_dec(ml):
    """Moneyline americana → odd decimal. +150 → 2.50; -200 → 1.50."""
    ml = pd.to_numeric(ml, errors="coerce").to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(ml > 0, 1.0 + ml / 100.0, 1.0 + 100.0 / np.abs(ml))


def _load(path=None):
    path = Path(path or DATA)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} ausente — rode `python analysis/00c_fetch_basketball.py` "
            f"(precisa de rede).")
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    return df


def to_canonical(df=None, comp_col=COMP_COL):
    """Mapeia o dado de basquete para a tabela canônica. `comp_col` = coluna de
    agrupamento (default: season — a competitividade da liga varia ano a ano)."""
    if df is None:
        df = _load()
    df = df.copy()
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
    oV = _ml_to_dec(df["ml_v"])
    oH = _ml_to_dec(df["ml_h"])
    over = 1.0 / oV + 1.0 / oH
    keep = (np.isfinite(oV) & np.isfinite(oH)
            & (oV > C.MIN_ODD) & (oH > C.MIN_ODD)
            & (over > 1.0) & (over < MAX_OVERROUND)
            & df["pts_v"].notna().to_numpy() & df["pts_h"].notna().to_numpy()
            & (df["pts_v"].to_numpy() != df["pts_h"].to_numpy()))
    d = df[keep].reset_index(drop=True)
    oV, oH = oV[keep], oH[keep]
    won_v = (d["pts_v"].to_numpy(float) > d["pts_h"].to_numpy(float)).astype(int)
    comp = (d[comp_col].astype(str) if comp_col in d.columns
            else pd.Series([SPORT] * len(d)))
    n = len(d)
    base = pd.DataFrame({
        "event_id": np.arange(n),
        "sport": SPORT, "market": MARKET,
        "competition": comp.to_numpy(),
        "date": d["date"].to_numpy(),
    })
    parts = []
    for oc, odds, won in [("away", oV, won_v), ("home", oH, 1 - won_v)]:
        part = base.copy()
        part["outcome"] = oc
        part["role"] = ROLES[oc]
        part["odds"] = np.asarray(odds, float)
        part["p"] = np.nan
        part["won"] = won
        parts.append(part)
    out = pd.concat(parts, ignore_index=True)
    return canonical.devig(out)[canonical.SCHEMA]
