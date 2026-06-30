"""Pre-registered ledger of World Cup predictions + predicted×realised reconcile.

The live practical demonstration: for every UPCOMING World Cup game (a fixture
with no score in the dump) the odds-free Elo model predicts the favourite, its
probability and the **skewness of the favourite bet** — and freezes that into an
append-only ledger (`site/src/data/wc_predictions.json`). When the score arrives,
the row is reconciled (realised filled in, prediction untouched). It is a
pre-registration: the prediction is never rewritten. Also exports `wc_live.json`,
compact, for the /worldcup page.

    python analysis/predict_worldcup.py        # predict upcoming + reconcile + export
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skewlib import worldcup as wc, exante

DATA = Path("data/intl_results.csv")
SITE = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data"
LEDGER = SITE / "wc_predictions.json"     # append-only pre-registration (versioned)
LIVE = SITE / "wc_live.json"              # compact payload for the page
MANUAL = Path(__file__).resolve().parents[1] / "wc_manual_results.json"  # web-sourced KO results
BOOK = Path(__file__).resolve().parents[1] / "wc_book_odds.json"  # web-sourced bookmaker odds


def _mid(date, home, away):
    return f"{date}|{home}|{away}"


def main():
    wc.ensure_dataset(DATA)
    fp = wc.dataset_fingerprint(DATA)
    intl = wc.load_internationals(DATA)
    played = wc.world_cup(wc.add_favorite_bet(wc.fit(intl)))
    played["match_id"] = [_mid(d.strftime("%Y-%m-%d"), h, a)
                          for d, h, a in zip(played.date, played.HomeTeam, played.AwayTeam)]
    played_by_id = {r.match_id: r for r in played.itertuples()}

    fixtures = wc.upcoming_wc_fixtures(DATA)
    preds = wc.predict_upcoming(intl, fixtures) if len(fixtures) else fixtures
    asof = fp["date_max"]

    # per-fixture display extras (3-way probs, flags, goals forecast, penalties)
    extras = {}
    gmodel, gteams = wc.fit_intl_goals(intl) if len(preds) else (None, set())
    for r in (preds.itertuples() if len(preds) else []):
        pH, pD, pA = float(r.pH_elo), float(r.pD_elo), float(r.pA_elo)
        cond = pH / (pH + pA) if (pH + pA) > 0 else 0.5
        s_home = 0.5 + 0.4 * (cond - 0.5)            # shootout win prob (shrunk to ~coin-flip)
        adv_home = pH + pD * s_home                  # advance: win in 90'/ET, or win the shootout
        ex = {"p_home": round(pH, 4), "p_draw": round(pD, 4), "p_away": round(pA, 4),
              "home_flag": wc.flag_iso(r.HomeTeam), "away_flag": wc.flag_iso(r.AwayTeam),
              "adv_home": round(adv_home, 4), "adv_away": round(1 - adv_home, 4),
              "pen_home": round(s_home, 4)}
        g = wc.predict_match_goals(gmodel, gteams, r.HomeTeam, r.AwayTeam, bool(r.neutral))
        if g:
            lh, la = g
            i, j, _ = wc.top_scoreline(lh, la)
            ex.update({"xg_home": round(float(lh), 2), "xg_away": round(float(la), 2),
                       "score_home": i, "score_away": j})
        extras[r.match_id] = ex

    # ── append-only ledger: freeze new predictions, reconcile resolved ones ──
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"predictions": []}
    by_id = {p["match_id"]: p for p in ledger["predictions"]}

    for r in preds.itertuples() if len(preds) else []:
        if r.match_id in by_id:
            continue                                   # NEVER rewrite a prediction
        by_id[r.match_id] = {
            "match_id": r.match_id, "date": r.date.strftime("%Y-%m-%d"),
            "home": r.HomeTeam, "away": r.AwayTeam, "neutral": bool(r.neutral),
            "fav_team": r.fav_team, "fav_pick": r.fav_pick,
            "p_fav": round(float(r.p_fav), 4),
            "skew_pred": round(float(r.skew_exante_match), 4),
            "o_fair": round(float(r.o_fav), 4),
            "predicted_asof": asof, "model": "elo-results-only",
            "realized": None}

    resolved_now = 0
    for mid, p in by_id.items():
        if p.get("realized") is None and mid in played_by_id:
            g = played_by_id[mid]
            p["realized"] = {
                "result": g.FTResult, "fav_won": bool(g.fav_pick == g.FTResult),
                "ret_fav": round(float(g.ret_fav), 4),
                "settled_asof": asof}
            resolved_now += 1

    # web-sourced knockout results not yet in the dump (persistent + sourced).
    # A knockout draw (reg=D) settles the favourite 1X2 bet as a loss; the shootout
    # only decides who advances, which we keep separately.
    manual = json.loads(MANUAL.read_text()) if MANUAL.exists() else {}
    for mid, p in by_id.items():
        if p.get("realized") is None and mid in manual:
            r = manual[mid]
            won = p["fav_pick"] == r["reg"]
            p["realized"] = {
                "result": r["reg"], "fav_won": won,
                "ret_fav": round(p["o_fair"] - 1.0, 4) if won else -1.0,
                "score": f'{r["fh"]}-{r["fa"]}', "advanced": r.get("advanced"),
                "pens": bool(r.get("pens")), "pens_score": r.get("pens_score"),
                "note": r.get("note"), "source": r.get("source"), "settled_asof": asof}
            resolved_now += 1

    # ── market overlay (Box A): freeze the pre-match book quote alongside our p ──
    # The book and the model price the SAME bet (the model's favourite pick). De-vig
    # gives the market's fair p; the law (1−2p)/√(p(1−p)) gives its implied skew. The
    # block is frozen once — a pre-match snapshot, never rewritten (like predictions).
    book_odds = wc.load_book_odds(BOOK)
    for mid, p in by_id.items():
        if mid in book_odds and "book" not in p:
            b = book_odds[mid]
            pb, ob, ovr = wc.book_pfav(b, p["fav_pick"])
            p["book"] = {
                "p_fav": round(pb, 4), "o_fav": round(ob, 4),
                "skew": round(float(exante.per_match_skew(pb)), 4),
                "overround": round(ovr, 4), "edge": round(p["p_fav"] - pb, 4),
                "book": b["book"], "source": b["source"], "asof": b["asof"]}

    ledger = {"schema": "wc-predictions@1", "updated_asof": asof,
              "data_sha256": fp["sha256"][:16],
              "predictions": sorted(by_id.values(), key=lambda p: (p["date"], p["home"]))}
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=1))

    # ── model backtest on the 2026 World Cup played so far (immediate, reproducible) ──
    w26 = played[played.edition == 2026]
    bt = {"n": int(len(w26)),
          "skew_pred_pool": round(exante.pooled_skew(w26.p_fav.values, w26.o_fav.values)["skew"], 4),
          "skew_real_pool": round(float(skew(w26.ret_fav)), 4),
          "p_fav_mean": round(float(w26.p_fav.mean()), 4),
          "fav_hit_rate": round(float((w26.fav_pick.values == w26.FTResult.values).mean()), 4),
          "brier": round(float(np.mean((w26.p_fav.values
                          - (w26.fav_pick.values == w26.FTResult.values)) ** 2)), 4)}

    # ── state of the pre-registered ledger ──
    res = [p for p in ledger["predictions"] if p.get("realized")]
    pend = [p for p in ledger["predictions"] if not p.get("realized")]
    led = {"n_pending": len(pend), "n_resolved": len(res)}
    if len(res) >= 3:
        rr = np.array([p["realized"]["ret_fav"] for p in res])
        led["resolved_skew_real"] = round(float(skew(rr)), 4)
        led["resolved_p_fav"] = round(float(np.mean([p["p_fav"] for p in res])), 4)
        led["resolved_hit_rate"] = round(float(np.mean([p["realized"]["fav_won"] for p in res])), 4)

    def card(p):
        o = p["o_fair"]
        return {"match_id": p["match_id"], "date": p["date"], "home": p["home"],
                "away": p["away"], "neutral": p["neutral"], "fav_team": p["fav_team"],
                "fav_pick": p["fav_pick"], "p_fav": p["p_fav"], "skew_pred": p["skew_pred"],
                "win_payoff": round(o - 1, 2), "lose_payoff": -1.0,
                "verdict": _verdict(p["skew_pred"]),
                **extras.get(p["match_id"], {})}

    upcoming = [card(p) for p in pend]

    # resolved predictions (predicted vs actual) — the retrospective payload
    resolved_detail = []
    for p in sorted(res, key=lambda x: x["date"]):
        ex = extras.get(p["match_id"], {})
        rz = p["realized"]
        resolved_detail.append({
            "home": p["home"], "away": p["away"],
            "home_flag": wc.flag_iso(p["home"]), "away_flag": wc.flag_iso(p["away"]),
            "fav_team": p["fav_team"], "p_fav": p["p_fav"], "skew_pred": p["skew_pred"],
            "xg_home": ex.get("xg_home"), "xg_away": ex.get("xg_away"),
            "score_pred": (f'{ex.get("score_home")}-{ex.get("score_away")}'
                           if ex.get("score_home") is not None else None),
            "adv_home": ex.get("adv_home"),
            "score": rz.get("score"), "reg_result": rz.get("result"),
            "fav_won": rz.get("fav_won"), "advanced": rz.get("advanced"),
            "pens": rz.get("pens"), "pens_score": rz.get("pens_score"),
            "note": rz.get("note")})

    # recent played 2026 games (with scorelines) — the "results" strip
    w26s = w26.sort_values("date").tail(8)
    recent_games = [{
        "home": g.HomeTeam, "away": g.AwayTeam,
        "home_flag": wc.flag_iso(g.HomeTeam), "away_flag": wc.flag_iso(g.AwayTeam),
        "fh": int(g.FTHome), "fa": int(g.FTAway),
        "fav_team": (g.HomeTeam if g.fav_pick == "H" else g.AwayTeam if g.fav_pick == "A" else "Draw"),
        "fav_won": bool(g.fav_pick == g.FTResult),
        "p_fav": round(float(g.p_fav), 4),
        "skew_pred": round(float(g.skew_exante_match), 4),
    } for g in w26s.itertuples()][::-1]

    # ── Box A: model vs market — same bet, two probabilities, one law ──
    # Each resolved game with a frozen book quote gives a (p, skew) point for the
    # model AND for the market. The structural claim: both sit on (1−2p)/√(p(1−p));
    # they differ only in WHERE on the curve, never in the curve. Box B: whose p was
    # better calibrated against the realised outcome (Brier / log-loss, model vs book).
    tri = []
    for p in sorted([q for q in res if "book" in q], key=lambda x: x["date"]):
        bk, rz = p["book"], p["realized"]
        tri.append({
            "home": p["home"], "away": p["away"],
            "home_flag": wc.flag_iso(p["home"]), "away_flag": wc.flag_iso(p["away"]),
            "fav_team": p["fav_team"], "fav_pick": p["fav_pick"],
            "p_model": p["p_fav"], "p_book": bk["p_fav"],
            "skew_model": p["skew_pred"], "skew_book": bk["skew"],
            "o_model": p["o_fair"], "o_book": bk["o_fav"],
            "overround": bk["overround"], "edge": bk["edge"], "book": bk["book"],
            "fav_won": rz.get("fav_won"), "score": rz.get("score"),
            "pens": rz.get("pens"), "advanced": rz.get("advanced")})

    both = [p for p in res if "book" in p]
    mvb = None
    if both:
        y = np.array([1.0 if p["realized"]["fav_won"] else 0.0 for p in both])
        pm = np.array([p["p_fav"] for p in both])
        pb = np.array([p["book"]["p_fav"] for p in both])
        eps = 1e-9
        mvb = {
            "n": len(both),
            "p_model_mean": round(float(pm.mean()), 4), "p_book_mean": round(float(pb.mean()), 4),
            "hit_rate": round(float(y.mean()), 4),
            "brier_model": round(float(np.mean((pm - y) ** 2)), 4),
            "brier_book": round(float(np.mean((pb - y) ** 2)), 4),
            "logloss_model": round(float(-np.mean(y * np.log(pm + eps) + (1 - y) * np.log(1 - pm + eps))), 4),
            "logloss_book": round(float(-np.mean(y * np.log(pb + eps) + (1 - y) * np.log(1 - pb + eps))), 4),
            "agree_corr": round(float(np.corrcoef(pm, pb)[0, 1]), 4) if len(both) > 1 else None,
            "mean_abs_edge": round(float(np.mean(np.abs(pm - pb))), 4)}

    live = {
        "meta": {"data_date": asof, "n_played_wc": fp["n_wc"],
                 "n_upcoming": len(upcoming), "source": "martj42/international_results",
                 "sha256": fp["sha256"][:12]},
        "next": upcoming[0] if upcoming else None,
        "upcoming": upcoming,
        "backtest2026": bt,
        "ledger": led,
        "triangulation": tri,
        "model_vs_book": mvb,
        "resolved_detail": resolved_detail,
        "recent_games": recent_games,
        "recent_resolved": [
            {"home": p["home"], "away": p["away"], "fav_team": p["fav_team"],
             "home_flag": wc.flag_iso(p["home"]), "away_flag": wc.flag_iso(p["away"]),
             "p_fav": p["p_fav"], "skew_pred": p["skew_pred"],
             "fav_won": p["realized"]["fav_won"], "ret_fav": p["realized"]["ret_fav"]}
            for p in sorted(res, key=lambda p: p["date"], reverse=True)[:6]],
    }
    LIVE.write_text(json.dumps(live, ensure_ascii=False, indent=0))

    print(f"as-of {asof} | fixtures {len(fixtures)} | ledger: "
          f"{led['n_pending']} pending, {led['n_resolved']} resolved "
          f"(+{resolved_now} now)")
    print(f"backtest 2026 ({bt['n']} games): predicted skew {bt['skew_pred_pool']:+.3f} | "
          f"realised {bt['skew_real_pool']:+.3f} | favourite wins "
          f"{bt['fav_hit_rate']:.0%} (Brier {bt['brier']:.3f})")
    if live["next"]:
        n = live["next"]
        print(f"NEXT: {n['home']} × {n['away']} ({n['date']}) → favourite "
              f"{n['fav_team']} p={n['p_fav']:.2f}, predicted skew {n['skew_pred']:+.3f}")


def _verdict(s):
    if s <= -0.4: return "neg_strong"
    if s < -0.1:  return "neg"
    if s <= 0.1:  return "flat"
    if s < 0.4:   return "pos"
    return "pos_strong"


if __name__ == "__main__":
    main()
