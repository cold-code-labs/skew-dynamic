"""Adaptador FUTEBOL → tabela canônica. Dois mercados:

  football:1x2   — 3 resultados (casa/empate/fora). A de-vig é DELEGADA a
                   `devig.devig_frame` (método primário Shin), então o `p` é
                   bit-idêntico ao pipeline congelado: a via canônica reproduz
                   `exante.bettype_by` exatamente (asserção em analysis/47 + testes).
  football:ou25  — 2 resultados (over/under 2.5 gols). Prova que o núcleo lida com
                   n ≠ 3; a de-vig usa a via genérica `canonical.devig`.
"""
import numpy as np
import pandas as pd
from .. import io, devig, canonical, elo, config as C

SPORT = "football"
MARKET = "1x2"
OUTCOMES = ["H", "D", "A"]
ROLES = {"H": "home", "D": "draw", "A": "away"}
DRAW_ROLE = "draw"


def to_canonical(df=None, method=None):
    """Mapeia o dataset 1X2 para a tabela canônica (de-vig congelada via devig_frame)."""
    if df is None:
        df = io.load()
    dv = devig.devig_frame(df, method=method)
    n = len(dv)
    base = pd.DataFrame({
        "event_id": np.arange(n),
        "sport": SPORT, "market": MARKET,
        "competition": dv["Division"].to_numpy(),
        "date": dv["date"].to_numpy(),
    })
    parts = []
    for oc, oddcol, pcol in [("H", "OddHome", "p_H"), ("D", "OddDraw", "p_D"),
                             ("A", "OddAway", "p_A")]:
        part = base.copy()
        part["outcome"] = oc
        part["role"] = ROLES[oc]
        part["odds"] = dv[oddcol].to_numpy(float)
        part["p"] = dv[pcol].to_numpy(float)
        part["won"] = (dv["FTResult"].to_numpy() == oc).astype(int)
        parts.append(part)
    return pd.concat(parts, ignore_index=True)[canonical.SCHEMA]


def competitiveness(df=None):
    """Competitividade ODDS-FREE por liga (taxa de zebra do Elo de resultados)."""
    if df is None:
        df = io.load()
    c = elo.league_competitiveness(elo.with_elo(df))
    return c.rename(columns={"Division": "competition"})[["competition", "upset_rate"]]


class _OU:
    """Mercado over/under 2.5 (binário) como adaptador independente."""
    SPORT = "football"
    MARKET = "ou25"
    OUTCOMES = ["over", "under"]
    ROLES = {"over": "over", "under": "under"}
    DRAW_ROLE = None                       # sem empate neste mercado

    def to_canonical(self, df=None, method=None):
        if df is None:
            df = io.load()
        d = df.dropna(subset=["Over25", "Under25", "FTHome", "FTAway"]).copy()
        d = d[(d["Over25"] > C.MIN_ODD) & (d["Under25"] > C.MIN_ODD)].reset_index(drop=True)
        n = len(d)
        over_won = ((d["FTHome"].to_numpy(float) + d["FTAway"].to_numpy(float)) > 2.5).astype(int)
        base = pd.DataFrame({
            "event_id": np.arange(n),
            "sport": self.SPORT, "market": self.MARKET,
            "competition": d["Division"].to_numpy(),
            "date": d["date"].to_numpy(),
        })
        parts = []
        for oc, oddcol, won in [("over", "Over25", over_won), ("under", "Under25", 1 - over_won)]:
            part = base.copy()
            part["outcome"] = oc
            part["role"] = self.ROLES[oc]
            part["odds"] = d[oddcol].to_numpy(float)
            part["p"] = np.nan                       # preenchida pela de-vig genérica
            part["won"] = won
            parts.append(part)
        out = pd.concat(parts, ignore_index=True)
        return canonical.devig(out, method=method)[canonical.SCHEMA]


OU = _OU()
