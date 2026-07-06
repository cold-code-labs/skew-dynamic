"""Tournament title odds — the single-bet law, propagated through the bracket.

The skew law prices ONE match from its favourite probability p. A knockout cup is
a tree of such matches. Here we take the SAME odds-free engine (results-only Elo +
calibrated MNLogit) that priced every ledger fixture and propagate it *exactly*
through the round-of-16 bracket to each team's probability of reaching every round
and winning the cup. No odds, no Monte-Carlo noise — exact convolution over a fixed
tree (feeder sub-brackets are disjoint, so the product form is exact).

The bracket pairing is the official 2026 tree: the eight R16 ties feed the
quarter-finals sequentially, QFs feed the semis, semis the final. Regulation draws
are resolved by a shootout shrunk towards a coin-flip (the ledger's `pen_home`).

    python analysis/predict_worldcup_winner.py     # -> site/src/data/wc_forecast.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import worldcup as wc

DATA = Path("data/intl_results.csv")
SITE = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data"
OUT = SITE / "wc_forecast.json"
LEDGER = SITE / "wc_predictions.json"     # reconciled ledger = source of decided R16 ties

# Official 2026 round-of-16 bracket. Ties pair sequentially into the four QFs
# (0,1)->QF1, (2,3)->QF2, (4,5)->QF3, (6,7)->QF4; QFs (0,1)->SF1, (2,3)->SF2.
# Home team first (matters only where the tie is non-neutral — a co-host at home).
BRACKET_R16 = [
    ("Canada", "Morocco"),
    ("Paraguay", "France"),
    ("Brazil", "Norway"),
    ("Mexico", "England"),
    ("Portugal", "Spain"),
    ("United States", "Belgium"),
    ("Argentina", "Egypt"),
    ("Switzerland", "Colombia"),
]
# which R16 tie indices feed each QF / SF, for the bracket payload
QF_FEEDERS = [(0, 1), (2, 3), (4, 5), (6, 7)]
SF_FEEDERS = [(0, 1), (2, 3)]


def main():
    wc.ensure_dataset(DATA)
    fp = wc.dataset_fingerprint(DATA)
    intl = wc.load_internationals(DATA)
    R, model = wc.elo_state(intl)

    # neutral flag per tie, read from the live fixtures (co-hosts play some at home)
    fx = wc.upcoming_wc_fixtures(DATA)
    neu_by_pair = {frozenset([r.HomeTeam, r.AwayTeam]): bool(r.neutral) for r in fx.itertuples()}
    r16 = [(h, a, neu_by_pair.get(frozenset([h, a]), True)) for (h, a) in BRACKET_R16]

    # decided ties, straight from the reconciled ledger: the forecast conditions
    # on results already in the books instead of re-randomising played games
    winners = {}
    if LEDGER.exists():
        for p in json.loads(LEDGER.read_text())["predictions"]:
            pair = frozenset([p["home"], p["away"]])
            adv = (p.get("realized") or {}).get("advanced")
            if adv and pair in {frozenset(t) for t in BRACKET_R16}:
                winners[pair] = adv
    missing = [t for (h, a, _) in r16 for t in (h, a)
               if frozenset([h, a]) not in neu_by_pair
               and frozenset([h, a]) not in winners]
    if missing:
        print(f"WARN: {len(missing)} bracket teams neither in pending fixtures nor "
              f"decided in the ledger: {sorted(set(missing))}")
    if winners:
        print(f"conditioning on {len(winners)} decided R16 ties: "
              f"{', '.join(sorted(winners.values()))} through")

    reach, ctx = wc.simulate_bracket(R, model, r16, winners=winners)

    teams = []
    for (h, a, neu) in r16:
        for t in (h, a):
            rc = reach[t]
            teams.append({
                "team": t, "flag": wc.flag_iso(t), "elo": round(R.get(t, 1500.0), 1),
                "r16_opp": ctx[t]["opp"], "r16_opp_flag": wc.flag_iso(ctx[t]["opp"]),
                "r16_neutral": bool(neu),
                "p_r16": round(ctx[t]["adv"], 4),        # win the round of 16
                "p_qf": round(rc["qf"], 4),              # == p_r16 (reach QF = win R16)
                "p_sf": round(rc["sf"], 4),              # reach the semi-final
                "p_final": round(rc["final"], 4),        # reach the final
                "p_win": round(rc["win"], 4)})           # lift the cup
    teams.sort(key=lambda x: -x["p_win"])

    def tie(i):
        h, a, neu = r16[i]
        return {"home": h, "away": a, "home_flag": wc.flag_iso(h),
                "away_flag": wc.flag_iso(a), "neutral": bool(neu),
                "fav": h if ctx[h]["adv"] >= 0.5 else a,
                "p_fav": round(max(ctx[h]["adv"], ctx[a]["adv"]), 4)}

    bracket = {
        "r16": [tie(i) for i in range(8)],
        "qf_feeders": QF_FEEDERS, "sf_feeders": SF_FEEDERS,
        "note": "R16 ties pair sequentially into the QFs; QFs into the SFs; SFs into the final.",
    }

    data = {
        "schema": "wc-forecast@1",
        "generated_asof": fp["date_max"],
        "data_sha256": fp["sha256"][:16],
        "model": "elo-results-only",
        "method": "exact bracket propagation (no odds, no Monte-Carlo)",
        "n_intl": fp["n_intl"], "n_wc": fp["n_wc"],
        "bracket": bracket,
        "teams": teams,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))

    tot = sum(t["p_win"] for t in teams)
    print(f"as-of {fp['date_max']} | 16 teams | sum(p_win)={tot:.4f} (sanity ~1.0)")
    print(f"{'team':<16}{'elo':>7}{'R16':>8}{'SF':>8}{'final':>8}{'WIN':>8}")
    for t in teams:
        print(f"{t['team']:<16}{t['elo']:>7.0f}{t['p_r16']*100:>7.1f}%"
              f"{t['p_sf']*100:>7.1f}%{t['p_final']*100:>7.1f}%{t['p_win']*100:>7.1f}%")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
