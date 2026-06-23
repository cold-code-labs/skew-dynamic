"""Camada CANÔNICA, sport-agnóstica — mede e compara assimetrias de qualquer
mercado de apostas (2, 3, … resultados), de qualquer esporte.

O núcleo do estudo (identidade de Bernoulli, decomposição, skew-meter) só precisa,
por aposta, de (p de-vigado, o de mercado, won). Esta camada consome uma tabela
CANÔNICA em forma longa (uma linha por evento×resultado; ver docs/DATA-SCHEMA.md) e
expõe seleção de objeto de aposta + assinatura, reusando `exante` sem duplicar a
matemática. O específico-de-esporte (de-vig por mercado, taxonomia de resultados,
competitividade odds-free) vive nos adaptadores (`skewlib/adapters/`).
"""
import numpy as np
import pandas as pd
from . import exante
from . import devig as _devig

SCHEMA = ["event_id", "sport", "market", "competition", "date",
          "outcome", "role", "odds", "p", "won"]


def validate(df):
    """Checa o contrato canônico: colunas + invariantes por evento (Σp≈1, exatamente
    um vencedor, odds≥1, p∈(0,1)). Levanta AssertionError com a 1ª violação."""
    miss = [c for c in SCHEMA if c not in df.columns]
    assert not miss, f"colunas canônicas ausentes: {miss}"
    assert (df.odds >= 1.0).all(), "há odds < 1"
    g = df.groupby("event_id")
    psum = g.p.sum()
    bad = psum[(psum - 1.0).abs() > 1e-6]
    assert bad.empty, f"Σp ≠ 1 em {len(bad)} eventos (ex.: {bad.index[:3].tolist()})"
    wins = g.won.sum()
    assert (wins == 1).all(), "todo evento precisa de exatamente um resultado vencedor"
    assert df.p.between(0, 1).all(), "há p fora de (0,1)"
    return True


def devig(df, method=None):
    """Preenche/sobrescreve `p` de-vigando as odds por evento (vetorizado por
    mercado de largura fixa). Para o adaptador de futebol, a de-vig é delegada ao
    `devig.devig_frame` (números congelados); aqui é a via genérica p/ outros."""
    wide = df.pivot(index="event_id", columns="outcome", values="odds")
    P = _devig.devig_odds(wide.to_numpy(float), method)
    pwide = pd.DataFrame(P, index=wide.index, columns=wide.columns)
    pl = pwide.reset_index().melt(id_vars="event_id", var_name="outcome", value_name="p")
    out = df.drop(columns=[c for c in ("p",) if c in df.columns]).merge(
        pl, on=["event_id", "outcome"], how="left")
    return out


# ── seleção do objeto de aposta ──────────────────────────────────────────────
def select(df, kind, draw_role="draw"):
    """Devolve uma linha por evento (competition, date, p, o, won) para o objeto:
    'fav' = argmax p, 'dog' = argmin p, 'draw' = papel == draw_role (vazio se o
    esporte não tem empate)."""
    if kind == "draw":
        sel = df[df.role == draw_role].copy()
    elif kind in ("fav", "dog"):
        idx = (df.groupby("event_id").p.idxmax() if kind == "fav"
               else df.groupby("event_id").p.idxmin())
        sel = df.loc[idx].copy()
    else:
        raise ValueError(f"kind desconhecido: {kind}")
    return sel.rename(columns={"odds": "o"})[
        ["event_id", "competition", "date", "p", "o", "won"]].reset_index(drop=True)


def signature(sel, label=None):
    """Assinatura de assimetria (skew/var/exkurt + competitividade) de uma seleção
    já feita, via a mistura ex-ante. Reusa exante.pooled_moments (mesmos números)."""
    p = sel.p.to_numpy(float); o = sel.o.to_numpy(float)
    if len(p) == 0:
        return None
    m = exante.pooled_moments(p, o, max_order=4)
    return {"label": label, "n": int(len(p)), "skew": m["skew"], "var": m["var"],
            "exkurt": m["exkurt"], "comp": float(p.mean())}


def bettype_by(df, by="competition", kinds=("fav", "draw", "dog"),
               draw_role="draw", min_n=2000):
    """Skewness ex-ante de cada objeto de aposta, por grupo (liga/torneio) — a
    generalização sport-agnóstica de `exante.bettype_by`. Uma linha por grupo."""
    rows = []
    for key, g in df.groupby(by, observed=True):
        n_events = g.event_id.nunique()
        if n_events < min_n:
            continue
        row = {by: key, "n": int(n_events)}
        fav = select(g, "fav", draw_role)
        row["p_fav_mean"] = float(fav.p.mean())
        for kind in kinds:
            sel = select(g, kind, draw_role)
            row[f"skew_{kind}"] = (exante.pooled_skew(sel.p.values, sel.o.values)["skew"]
                                   if len(sel) else float("nan"))
        rows.append(row)
    return pd.DataFrame(rows)
