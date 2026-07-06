"""Front O — the third observer: player-informed p from a disjoint information set.

The invariance thesis says ANY observer's (p, skew) lands on (1−2p)/√(p(1−p)).
This module builds an observer whose team-strength STATE never sees a match
result or a market price: strength = log market value of the matchday starting
lineup (Transfermarkt valuations, CC0 mirror — see docs/SPIKE-O0.md). Results
touch only the low-dimensional link (MNLogit, the `elo.calibrate_outcomes`
idiom), fitted on a train era disjoint from evaluation.

Pipeline: `lineup_values` (DuckDB ASOF join: latest valuation ≤ match date) →
`build_club_map` (frozen archive team → TM club, matched globally on names seen
in that competition's games — NOT `clubs.domestic_competition_id`, which only
reflects current membership) → `attach_values` (join on date + club pair) →
`calibrate_value_link` / `apply_value_link` (z = log(hv/av)).
"""
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd

TM_DB = Path("data/transfermarkt.duckdb")
TM_URL = ("https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/"
          "data/transfermarkt-datasets.duckdb")
CLUB_MAP = Path(__file__).resolve().parent / "data" / "tm_club_map.json"
VALUE_LINK = Path(__file__).resolve().parent / "data" / "value_link.json"

# frozen-archive division → TM competition (first tiers only; docs/SPIKE-O0.md)
DIV2COMP = {"E0": "GB1", "SP1": "ES1", "I1": "IT1", "F1": "FR1", "D1": "L1",
            "N1": "NL1", "P1": "PO1", "B1": "BE1", "T1": "TR1", "G1": "GR1",
            "SC0": "SC1", "ARG": "ARG1", "USA": "MLS1", "BRA": "BRA1",
            "JAP": "JAP1", "MEX": "MEX1", "RUS": "RU1", "DEN": "DK1",
            "SWE": "SE1", "NOR": "NO1", "POL": "PL1", "ROM": "RO1",
            "SUI": "C1", "AUT": "A1"}


def ensure_tm(path=TM_DB):
    """Download the CC0 Transfermarkt DuckDB mirror if absent (~200 MB)."""
    import urllib.request
    p = Path(path)
    if p.exists():
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(TM_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(p, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    return p


def lineup_values(db_path=TM_DB):
    """Per TM game: starting-lineup market value of each side at match date.

    ASOF join takes each starter's latest valuation ≤ the game date; a side
    counts only when ≥8 of its 11 starters carry a valuation (guards early
    seasons where coverage is thin).
    """
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.sql("""
        WITH lv AS (
            SELECT l.game_id, l.club_id, v.market_value_in_eur AS mv
            FROM (SELECT * FROM game_lineups WHERE type = 'starting_lineup') l
            ASOF JOIN player_valuations v
              ON l.player_id = v.player_id AND v.date <= l.date
        ), side AS (
            SELECT game_id, club_id, SUM(mv) AS value, COUNT(*) AS n_valued
            FROM lv GROUP BY 1, 2
        )
        SELECT g.game_id, g.date, g.competition_id,
               g.home_club_id, g.away_club_id, h.value AS hv, a.value AS av
        FROM games g
        JOIN side h ON h.game_id = g.game_id AND h.club_id = g.home_club_id
        JOIN side a ON a.game_id = g.game_id AND a.club_id = g.away_club_id
        WHERE h.n_valued >= 8 AND a.n_valued >= 8 AND h.value > 0 AND a.value > 0
    """).df()
    df["date"] = pd.to_datetime(df.date)
    return df


def tm_names_by_comp(db_path=TM_DB):
    """{competition_id: {club_id: most recent display name}} from the games
    table itself — includes relegated clubs, unlike `clubs`."""
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.sql("""
        SELECT competition_id, club_id, name FROM (
            SELECT competition_id, home_club_id AS club_id, home_club_name AS name,
                   ROW_NUMBER() OVER (PARTITION BY competition_id, home_club_id
                                      ORDER BY date DESC) rn
            FROM games WHERE home_club_name IS NOT NULL
            UNION ALL
            SELECT competition_id, away_club_id, away_club_name,
                   ROW_NUMBER() OVER (PARTITION BY competition_id, away_club_id
                                      ORDER BY date DESC)
            FROM games WHERE away_club_name IS NOT NULL
        ) WHERE rn = 1
    """).df()
    out = {}
    for r in rows.itertuples():
        out.setdefault(r.competition_id, {})[int(r.club_id)] = r.name
    return out


_STOP = re.compile(r"\b(fc|cf|sc|ac|as|cd|sd|rcd|afc|bk|if|fk|sk|ks|ca|club|de|"
                   r"deportivo|athletic|atletico|football|calcio|clube|the)\b")


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = _STOP.sub("", s)
    return re.sub(r"[^a-z0-9]", "", s)


def build_club_map(frozen_teams_by_div, names_by_comp, overrides=None, cutoff=0.75):
    """{division: {frozen team name: tm club_id}} by normalised fuzzy match
    against the clubs seen in that competition's games. Exact > containment >
    SequenceMatcher ≥ cutoff; a TM club is consumed at most once per division."""
    overrides = overrides or {}
    out, misses = {}, []
    for div, teams in frozen_teams_by_div.items():
        comp = DIV2COMP.get(div)
        pool = {cid: (nm, norm_name(nm)) for cid, nm in names_by_comp.get(comp, {}).items()}
        got = {}
        for t in sorted(teams):
            if (ov := overrides.get(div, {}).get(t)) is not None:
                got[t] = ov
                continue
            nt = norm_name(t)
            free = {cid: v for cid, v in pool.items() if cid not in got.values()}
            best, why = None, 0.0
            for cid, (_, nn) in free.items():
                if nt == nn:
                    best, why = cid, 2.0
                    break
                if len(nt) > 3 and len(nn) > 3 and (nt in nn or nn in nt):
                    if 1.0 > why:
                        best, why = cid, 1.0
                else:
                    r = SequenceMatcher(None, nt, nn).ratio()
                    if cutoff <= r > why and why < 1.0:
                        best, why = cid, r
            if best is not None:
                got[t] = int(best)
            else:
                misses.append((div, t))
        out[div] = got
    return out, misses


def attach_values(frozen, values, club_map):
    """Join frozen matches to TM lineup values on (date, home id, away id).
    Returns the joined frame (rows without a value pair are dropped) plus
    coverage per division."""
    d = frozen.copy()
    d["home_id"] = [club_map.get(dv, {}).get(t) for dv, t in zip(d.Division, d.HomeTeam)]
    d["away_id"] = [club_map.get(dv, {}).get(t) for dv, t in zip(d.Division, d.AwayTeam)]
    d = d.dropna(subset=["home_id", "away_id"])
    d["home_id"] = d.home_id.astype(int)
    d["away_id"] = d.away_id.astype(int)
    v = values.rename(columns={"home_club_id": "home_id", "away_club_id": "away_id"})
    j = d.merge(v[["date", "home_id", "away_id", "hv", "av"]],
                on=["date", "home_id", "away_id"], how="inner")
    j["lv_gap"] = np.log(j.hv / j.av)
    return j


def calibrate_value_link(train):
    """MNLogit (A,D,H) ~ const + z + z², z = log(lineup value ratio) — the same
    low-dimensional link the Elo observer uses (`elo.calibrate_outcomes`)."""
    import statsmodels.api as sm
    y = train.FTResult.map({"A": 0, "D": 1, "H": 2}).values
    z = train.lv_gap.values
    X = sm.add_constant(np.column_stack([z, z * z]))
    return sm.MNLogit(y, X).fit(disp=0)


def apply_value_link(m, z):
    """z = log(value ratio) → (pA, pD, pH) arrays."""
    import statsmodels.api as sm
    z = np.asarray(z, float)
    X = sm.add_constant(np.column_stack([z, z * z]), has_constant="add")
    P = np.asarray(m.predict(X))
    return P[:, 0], P[:, 1], P[:, 2]


def save_value_link(m, path=VALUE_LINK, meta=None):
    """Persist link coefficients (small, versioned) so downstream consumers —
    the World Cup overlay — never need the 200 MB dump."""
    payload = {"params": np.asarray(m.params).tolist(),
               "form": "MNLogit const+z+z2, z=log(hv/av), classes A,D,H",
               **(meta or {})}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1))
    return path


def load_value_link(path=VALUE_LINK):
    """Standalone predictor from the saved coefficients: z → (pA, pD, pH)."""
    params = np.asarray(json.loads(Path(path).read_text())["params"])

    def predict(z):
        z = np.atleast_1d(np.asarray(z, float))
        X = np.column_stack([np.ones_like(z), z, z * z])
        U = X @ params                                   # logits vs class A
        E = np.exp(np.column_stack([np.zeros(len(z)), U]))
        P = E / E.sum(1, keepdims=True)
        return P[:, 0], P[:, 1], P[:, 2]
    return predict
