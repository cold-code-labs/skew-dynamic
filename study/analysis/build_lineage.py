"""build_lineage — assembles the study's evidence LEDGER: links each PHASE (finding)
to the block(s) that produce it, to the KEY NUMBERS, to the git COMMIT that
established it, to the versioning TAGS and to the dataset HASH. Output:
  • lineage.json   — machine (source of truth for evidence versioning)
  • docs/LINEAGE.md — human (navigable table, matched to the timeline/FINDINGS)

Why it exists: the study evolves (we may improve a script and that moves a
result). The ledger pins each number to the exact version of the code + data that
produced it; git (tags `evidence/*`) allows returning to that state. `--check`
compares the recorded numbers with the most recent execution stamps
(outputs/_provenance/*.json) and flags DRIFT.

Usage:
  python analysis/build_lineage.py           # (re)generate lineage.json + LINEAGE.md
  python analysis/build_lineage.py --check    # only audit drift vs latest runs
  python analysis/build_lineage.py --tags     # print the suggested git tag commands
"""
import json, sys, subprocess
from pathlib import Path
from skewlib import provenance as prov, config as C

ROOT = Path(__file__).resolve().parents[1]
LJSON = ROOT / "lineage.json"
LMD = ROOT / "docs" / "LINEAGE.md"

# ── Curated registry: each phase, its blocks, headline numbers and the commit that
# established it (the evidence lives here, pinned to the version). Frente: agenda grouper.
PHASES = [
    {"id": "P0", "front": "Foundation", "tag": "evidence/phase-0", "commit": "d58840c",
     "title": "Freezing + reproduction", "blocks": ["00_fetch_data", "01_baseline"],
     "figures": [], "metrics": {"n_matches": 205435, "leagues": 38, "years": "2005-2025"}},
    {"id": "W1", "front": "Finding", "tag": "evidence/W1", "commit": "699f14c",
     "title": "Mechanical core (ex-ante skew)", "blocks": ["07_devig_exante", "03_decomposition"],
     "figures": ["f1", "f3"], "metrics": {"skew_exante": 0.236, "skew_expost": 0.230,
     "within_frac_m3": 1.026}},
    {"id": "W2", "front": "Mechanism", "tag": "evidence/W2", "commit": "730fda7",
     "title": "Odds-free law (Elo)", "blocks": ["08_mechanism_elo"],
     "figures": ["f2"], "metrics": {"corr_skew_upset": 0.826, "corr_elo_odds": 0.909}},
    {"id": "W3", "front": "Invariance", "tag": "evidence/W3", "commit": "c68eb69",
     "title": "Temporal invariance (panel)", "blocks": ["09_panel_temporal"],
     "figures": ["f4"], "metrics": {"trend_beta_year": 0.00015, "trend_p": 0.73, "icc": 0.70}},
    {"id": "W5", "front": "Robustness", "tag": "evidence/W5", "commit": "95d1a07",
     "title": "Binary O/U 2.5 market", "blocks": ["10_overunder"],
     "figures": [], "metrics": {"skew_ou": -0.210, "within_frac": 0.996}},
    {"id": "W4", "front": "Separation", "tag": "evidence/W4", "commit": "16b8c2e",
     "title": "Orthogonal margin + de-vig", "blocks": ["11_margin_robustness"],
     "figures": [], "metrics": {"overround_avg": 1.067, "overround_best": 1.009}},
    {"id": "P1", "front": "Reframe", "tag": "evidence/P1", "commit": "f2bc443",
     "title": "Intra-regime invariance", "blocks": ["13_regimes"],
     "figures": [], "metrics": {"breaks_38_leagues": 1, "epl_breaks": 0}},
    {"id": "P2", "front": "Hardening", "tag": "evidence/P2", "commit": "7f00792",
     "title": "Standings balance (odds-free)", "blocks": ["14_balance_indices"],
     "figures": [], "metrics": {"corr_skew_nollscully": -0.625}},
    {"id": "P3", "front": "Theory", "tag": "evidence/P3", "commit": "624547a",
     "title": "Derived law (ordered-probit)", "blocks": ["15_model"],
     "figures": ["f5"], "metrics": {"model_r": 0.904, "model_rmse": 0.024}},
    {"id": "P4", "front": "Confound", "tag": "evidence/P4", "commit": "2bcef94",
     "title": "Stable FLB (Angelini)", "blocks": ["16_flb_stability"],
     "figures": [], "metrics": {"mean_abs_ante_post": 0.015}},
    {"id": "B1", "front": "Shape", "tag": "evidence/frente-B", "commit": "6946fc6",
     "title": "SHAPE invariance (multi-moment)", "blocks": ["17_moments"],
     "figures": ["f6"], "metrics": {"model_r_var": 0.987, "model_r_skew": 0.904,
     "model_r_exkurt": 0.890}},
    {"id": "B2", "front": "Collapse", "tag": "evidence/frente-B", "commit": "6946fc6",
     "title": "Distribution collapse", "blocks": ["18_collapse"],
     "figures": ["f7"], "metrics": {"uncond_ks": 0.474, "cond_ks": 0.059, "drop": 0.87}},
    {"id": "C1", "front": "Pricing", "tag": "evidence/frente-C", "commit": "2b2d423",
     "title": "No premium beyond the mechanical FLB", "blocks": ["19_premium"],
     "figures": ["f8"], "metrics": {"ret": -0.0482, "vig": -0.0497, "flb": 0.0015,
     "resid_skew_r": 0.11}},
    {"id": "C2", "front": "Preference", "tag": "evidence/frente-C", "commit": "2b2d423",
     "title": "Invariant CPT (γ)", "blocks": ["20_cpt"],
     "figures": ["f9"], "metrics": {"gamma": 0.958, "gamma_sd_season": 0.020,
     "gamma_sd_league": 0.040, "trend_beta": 0.0003}},
    {"id": "E1", "front": "Theory", "tag": "evidence/frente-E", "commit": "a70b790",
     "title": "Closed form of S(σ_L)", "blocks": ["21_closed_form"],
     "figures": ["f10"], "metrics": {"max_mc_err": 0.0015, "p0": 0.4392, "S0": 0.2449,
     "sigma_peak": 0.1226, "league_r": 0.903}},
    {"id": "E2", "front": "Robustness", "tag": "evidence/frente-E", "commit": "a70b790",
     "title": "Robustness of the strength distribution", "blocks": ["22_force_robustness"],
     "figures": ["f11"], "metrics": {"max_dS_overall": 0.0320, "sd_between_leagues": 0.0518}},
    {"id": "G1", "front": "Reliability", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "Reliable de-vig + method invariance", "blocks": ["23_devig_reliability"],
     "figures": ["f12"], "metrics": {"rel_global": 0.0000, "rel_sd_league": 0.0003,
     "skew_devig_range": 0.039}},
    {"id": "G2", "front": "Robustness", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "Strict balanced panel (composition killed)", "blocks": ["24_balanced_panel"],
     "figures": ["f13"], "metrics": {"n_balanced": 15, "beta_balanced": -0.00013,
     "delta20_balanced": -0.003}},
    {"id": "G3", "front": "Confidence", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "CI by block-bootstrap over seasons", "blocks": ["25_block_bootstrap"],
     "figures": [], "metrics": {"skew_ci_lo": 0.232, "skew_ci_hi": 0.239,
     "corr_ci_lo": -0.922, "corr_ci_hi": -0.876}},
    {"id": "D2", "front": "Microstructure", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "Sharp vs soft (orthogonal margin at the best odd)", "blocks": ["26_sharp_soft"],
     "figures": ["f14"], "metrics": {"d_skew_mean": 0.020, "corr_soft_sharp": 0.993,
     "corr_sharp_pfav": -0.876}},
    {"id": "D3", "front": "Microstructure", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "Shin's z (informed money) as a series", "blocks": ["27_shin_z_series"],
     "figures": ["f15"], "metrics": {"z_global": 0.0343, "z_sd_league": 0.0043,
     "corr_z_overround": 0.999}},
    {"id": "D4", "front": "Third market", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "Asian handicap: identity in a 3rd market", "blocks": ["28_asian_handicap"],
     "figures": ["f16"], "metrics": {"p_fav_ah": 0.533, "skew_ah_global": -0.104,
     "within_frac_ah": 1.027, "league_identity_r": 0.80}},
    {"id": "F1", "front": "Within-season", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Intra-season seasonality (mild drift)", "blocks": ["29_intraseason"],
     "figures": ["f17"], "metrics": {"global_span": 0.0149, "shift_mean": -0.0078,
     "shift_ci_lo": -0.0131, "shift_ci_hi": -0.0015}},
    {"id": "F2", "front": "Tail cancellation", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Contribution to M₃ by match competitiveness", "blocks": ["30_game_contribution"],
     "figures": ["f18"], "metrics": {"share_weak_fav": 1.26, "share_strong_fav": -0.26}},
    {"id": "F3", "front": "Team structure", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Per-team decomposition (strength dispersion)", "blocks": ["31_team_decomposition"],
     "figures": ["f19"], "metrics": {"corr_elo_teamskew": -0.444, "corr_elosd_leagueskew": -0.601}},
    {"id": "H2", "front": "Open vs closed", "tag": "evidence/H2", "commit": "e0bc9fd",
     "title": "Open vs closed league (MLS on the law)", "blocks": ["32_open_vs_closed"],
     "figures": ["f20"], "metrics": {"mls_p_fav": 0.503, "mls_skew": 0.162,
     "mls_pfav_rank": 22, "mls_residual": -0.059}},
    {"id": "C3", "front": "Staking", "tag": "evidence/C3", "commit": "e0bc9fd",
     "title": "Kelly/staking under the skewness structure", "blocks": ["33_kelly_staking"],
     "figures": ["f21"], "metrics": {"frac_positive_ev": 0.0, "skew_term_dog": 0.598,
     "skew_term_fav": 0.010}},
    {"id": "E3", "front": "Theory", "tag": "evidence/E3", "commit": "e0bc9fd",
     "title": "Per-league calibration (endogenous draw cutoff)", "blocks": ["34_per_league_calibration"],
     "figures": ["f22"], "metrics": {"corr_sigma_pfav": 0.874, "corr_c_draw": 0.906,
     "skew_model_r": 0.905}},
    # ── 2nd round (frozen dataset) ──
    {"id": "I", "front": "Cross-model", "tag": "evidence/frente-I", "commit": "7a45759",
     "title": "Cross-validation of the mechanism (goals Poisson)", "blocks": ["35_poisson_crossmodel"],
     "figures": ["f23"], "metrics": {"corr_pfav": 0.972, "corr_skew": 0.925,
     "league_r_poisson": 0.85, "n_league_seasons": 617}},
    {"id": "J", "front": "Dynamic", "tag": "evidence/frente-J", "commit": "74f9c2e",
     "title": "Information arrival HT→FT (dynamic identity)", "blocks": ["36_inplay_resolution"],
     "figures": ["f24"], "metrics": {"skew_pregame": 0.239, "skew_behind": 2.084,
     "skew_ahead2": -3.908, "martingale_err": 0.0035}},
    {"id": "K", "front": "Diversification", "tag": "evidence/frente-K", "commit": "b4b90eb",
     "title": "Diversification (skewness = single-bet phenomenon)", "blocks": ["37_diversification"],
     "figures": ["f25"], "metrics": {"skew_single_fav": 0.230, "skew_single_dog": 2.254,
     "n_to_gaussian_dog": 509}},
    {"id": "L", "front": "Confound", "tag": "evidence/frente-LMN", "commit": "f22f163",
     "title": "Secular home advantage vs invariance", "blocks": ["38_home_advantage"],
     "figures": ["f26"], "metrics": {"hfa_beta": -0.00133, "skew_beta": -0.00009,
     "corr_hfa_skew": -0.244}},
    {"id": "M", "front": "Tail risk", "tag": "evidence/frente-LMN", "commit": "f22f163",
     "title": "Realised tail risk of the strategies", "blocks": ["39_tail_risk"],
     "figures": ["f27"], "metrics": {"skew_fav": 0.230, "skew_dog": 2.254,
     "maxdd_fav": -9922.9, "maxdd_dog": -20934.0}},
    {"id": "N", "front": "Indices", "tag": "evidence/frente-LMN", "commit": "f22f163",
     "title": "Entropy + cross-market co-moment", "blocks": ["40_entropy_comoment"],
     "figures": ["f28"], "metrics": {"corr_entropy_skew": 0.827, "corr_1x2_ou_skew": 0.146}},
    # ── 3rd round (model independence) ──
    {"id": "O", "front": "Model battery", "tag": "evidence/frente-O", "commit": "ece5117",
     "title": "Battery of generative models (model independence)",
     "blocks": ["41_model_battery"], "figures": ["f29"],
     "metrics": {"corr_skew_poisson": 0.925, "corr_skew_dixoncoles": 0.874,
     "corr_skew_btd": 0.840, "corr_skew_elo": 0.786, "r_curve_elo": 0.96,
     "n_league_seasons": 617, "n_models": 5}},
    # ── 4th round (EXTERNAL DATA: canonical football-data.co.uk; H1 uses the mirror) ──
    {"id": "D1", "front": "Price discovery", "tag": "evidence/frente-D1", "commit": "3b63b77",
     "title": "Price discovery: opening→closing [canonical]",
     "blocks": ["42_open_close"], "figures": ["f30"],
     "metrics": {"skew_open": 0.248, "skew_close": 0.249, "corr_open_close": 0.998,
     "law_open": -0.866, "n": 34659}},
    {"id": "H1", "front": "Natural experiment", "tag": "evidence/frente-H1", "commit": "3b63b77",
     "title": "Staggered VAR: institutional shock does not move skewness (placebo)",
     "blocks": ["44_var"], "figures": ["f31"],
     "metrics": {"did_skew_beta": -0.0066, "did_skew_p": 0.65, "did_skew_sd": -0.14,
     "n_obs": 321}},
    {"id": "P6", "front": "Regime", "tag": "evidence/frente-pre2005", "commit": "3b63b77",
     "title": "Pre-2005: the modern regime already holds since ~2000 [canonical]",
     "blocks": ["43_pre2005"], "figures": ["f32"],
     "metrics": {"skew_pre2005": 0.214, "skew_modern": 0.232, "level_beta_pre": -0.0194,
     "trend_beta": 0.00112, "n_leagues": 17}},
    # ── 4th round (synthesis: root objective 'similarity of skewnesses') ──
    {"id": "Q", "front": "Similarity", "tag": "evidence/frente-Q", "commit": "c2a3849",
     "title": "skew-meter: similarity of skewnesses (sufficiency ladder)",
     "blocks": ["45_skewmeter"], "figures": ["f33"],
     "metrics": {"r2_1param": 0.82, "r2_2moment": 0.98, "r2_full": 0.99,
     "split_half_r": 0.98, "corr_oddsfree": 0.826, "n_leagues": 38}},
    # ── 5th round (product: bet type — the law mirrored across the whole book) ──
    {"id": "R", "front": "Bet-type", "tag": "evidence/frente-R", "commit": "a67e465",
     "title": "Bet type: the law skew=f(competitiveness) across the book",
     "blocks": ["46_bettype"], "figures": ["f34"],
     "metrics": {"skew_fav": 0.236, "skew_draw": 1.294, "skew_dog": 2.349,
     "corr_fav_comp": -0.90, "corr_draw_comp": 0.95, "corr_dog_comp": 0.91,
     "n_leagues": 38}},
    # ── 6th round (external validity: 2nd sport on the canonical layer) ──
    {"id": "S", "front": "External validity", "tag": "evidence/frente-S", "commit": "4cf9084",
     "title": "Tennis: the law belongs to the sport, not to football (canonical layer)",
     "blocks": ["48_tennis"], "figures": ["f35"],
     "metrics": {"skew_fav": -0.571, "skew_dog": 2.314, "calib_pfav": 0.688,
     "calib_winrate": 0.692, "law_atp": -1.00, "law_wta": -0.98, "n_matches": 62865}},
    # ── 7th round (external validity: 3rd sport on the canonical layer) ──
    {"id": "T", "front": "External validity", "tag": "evidence/frente-T", "commit": "fa6ea6b",
     "title": "Basketball: the law holds in a 3rd sport (NBA moneyline, canonical layer)",
     "blocks": ["49_basketball"], "figures": ["f36"],
     "metrics": {"skew_fav": -0.570, "skew_dog": 2.609, "calib_pfav": 0.694,
     "calib_winrate": 0.685, "law_nba": -0.95, "n_matches": 19621}},
    # ── 8th round (inferential rigour: the temporal null as equivalence) ──
    {"id": "U", "front": "Equivalence", "tag": "evidence/frente-U", "commit": "0598390",
     "title": "Temporal equivalence: 'no drift' as TOST (evidence of absence)",
     "blocks": ["51_temporal_equivalence"], "figures": ["f37"],
     "metrics": {"beta_year": 0.00015, "drift20": 0.003, "sd_between": 0.0516,
     "delta20": 0.026, "p_tost": 0.006, "p_tost_boot": 0.005,
     "p_tost_balanced": 0.043, "n_obs": 638}},
]


def _commit_date(sha):
    try:
        return subprocess.check_output(
            ["git", "show", "-s", "--format=%cs", sha], cwd=ROOT,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def build():
    head = prov.git_info()
    data = prov.data_hash()
    rows = []
    for ph in PHASES:
        rows.append({**ph, "commit_date": _commit_date(ph["commit"])})
    ledger = {
        "schema": "skew-dynamic/lineage@1",
        "generated_at_head": head["short"],
        "head_dirty": head["dirty"],
        "data": data,
        "env": prov.env_versions(),
        "phases": rows,
    }
    LJSON.write_text(json.dumps(ledger, ensure_ascii=False, indent=2))

    # human table
    lines = [
        "# LINEAGE — evidence ledger (versioning)",
        "",
        "> Generated by `analysis/build_lineage.py` (do not edit by hand). Each phase pins",
        "> its headline number(s) to the exact VERSION of the code (commit + tag `evidence/*`)",
        f"> and to the DATASET (`sha256:{data['sha256']}`, {data.get('rows')} matches,",
        f"> {data.get('leagues')} leagues). Return to any state with",
        "> `git checkout <tag>`; audit a result change with `--check`.",
        "",
        f"**HEAD at generation:** `{head['short']}`"
        + ("  ⚠️ working tree DIRTY" if head["dirty"] else "  (clean)"),
        "",
        "| Phase | Front | Finding | Blocks | Figures | Headline numbers | Commit | Tag |",
        "|------|--------|--------|--------|---------|----------------|--------|-----|",
    ]
    for r in rows:
        met = " · ".join(f"{k}={v}" for k, v in r["metrics"].items())
        blk = ", ".join(r["blocks"])
        fig = ", ".join(r["figures"]) or "—"
        lines.append(
            f"| **{r['id']}** | {r["front"]} | {r['title']} | {blk} | {fig} | "
            f"{met} | `{r['commit']}` ({r['commit_date']}) | `{r['tag']}` |")
    lines += ["",
        "## Versioning tags (`evidence/*`)",
        "One annotated tag per evidence milestone points to the commit that established",
        "those numbers. `git tag -n` lists them; `git checkout evidence/frente-E`",
        "recovers the exact code of Front E.",
        ""]
    LMD.write_text("\n".join(lines) + "\n")
    print(f"-> {LJSON.relative_to(ROOT)} ({len(rows)} phases) | -> {LMD.relative_to(ROOT)}")
    print(f"   data sha256:{data['sha256']} · HEAD {head['short']}"
          + (" (DIRTY)" if head["dirty"] else ""))


def check():
    """Audit DRIFT: compares numbers recorded in the ledger with the most recent
    execution stamps (outputs/_provenance/<block>.json)."""
    if not LJSON.exists():
        print("lineage.json missing — run without --check first."); return
    ledger = json.loads(LJSON.read_text())
    pdir = C.OUTDIR / "_provenance"
    drift, checked = [], 0
    for ph in ledger["phases"]:
        for blk in ph["blocks"]:
            f = pdir / f"{blk}.json"
            if not f.exists():
                continue
            st = json.loads(f.read_text())
            for k, v in st.get("metrics", {}).items():
                if k in ph["metrics"]:
                    checked += 1
                    rec = ph["metrics"][k]
                    if isinstance(v, (int, float)) and isinstance(rec, (int, float)):
                        # the tolerance absorbs Monte Carlo noise (~0.3%) but catches
                        # a real script change (which moves numbers well beyond that)
                        tol = max(1e-3, 0.02 * abs(rec))
                        if abs(v - rec) > tol:
                            drift.append((ph["id"], blk, k, rec, v, st["git"]["short"]))
    print(f"[lineage --check] {checked} metrics compared against execution stamps.")
    if not drift:
        print("  ✓ no drift: the results match the versioned ledger.")
    else:
        print(f"  ⚠️ DRIFT in {len(drift)} metric(s) — the script changed the result:")
        for pid, blk, k, rec, v, sha in drift:
            print(f"    {pid}/{blk}: {k}  ledger={rec}  now={v}  (@{sha})")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    elif "--tags" in sys.argv:
        seen = set()
        for ph in PHASES:
            if ph["tag"] in seen:
                continue
            seen.add(ph["tag"])
            print(f"git tag -a {ph['tag']} {ph['commit']} -m \"{ph['id']}+ — {ph['title']}\"")
    else:
        build()
