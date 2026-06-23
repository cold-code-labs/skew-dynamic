"""build_lineage — monta o LEDGER de evidências do estudo: liga cada FASE (achado)
ao(s) bloco(s) que a produzem, aos NÚMEROS-CHAVE, ao COMMIT git que a estabeleceu,
às TAGS de versionamento e ao HASH do dataset. Saída:
  • lineage.json   — máquina (fonte da verdade do versionamento de evidências)
  • docs/LINEAGE.md — humano (tabela navegável, casada com o timeline/FINDINGS)

Por que existe: o estudo evolui (podemos melhorar um script e isso mover um
resultado). O ledger pina cada número à versão exata do código + dados que o
geraram; o git (tags `evidence/*`) permite voltar a esse estado. `--check`
compara os números registrados com os carimbos de execução mais recentes
(outputs/_provenance/*.json) e acusa DRIFT.

Uso:
  python analysis/build_lineage.py           # (re)gera lineage.json + LINEAGE.md
  python analysis/build_lineage.py --check    # só audita drift vs últimas execuções
  python analysis/build_lineage.py --tags     # imprime os comandos git tag sugeridos
"""
import json, sys, subprocess
from pathlib import Path
from skewlib import provenance as prov, config as C

ROOT = Path(__file__).resolve().parents[1]
LJSON = ROOT / "lineage.json"
LMD = ROOT / "docs" / "LINEAGE.md"

# ── Registro curado: cada fase, seus blocos, números-título e o commit que a
# estabeleceu (a evidência vive aqui, pinada à versão). Frente: agrupador da agenda.
PHASES = [
    {"id": "P0", "frente": "Foundation", "tag": "evidence/phase-0", "commit": "d58840c",
     "title": "Congelamento + reprodução", "blocks": ["00_fetch_data", "01_baseline"],
     "figures": [], "metrics": {"n_matches": 205435, "leagues": 38, "years": "2005-2025"}},
    {"id": "W1", "frente": "Finding", "tag": "evidence/W1", "commit": "699f14c",
     "title": "Núcleo mecânico (skew ex-ante)", "blocks": ["07_devig_exante", "03_decomposition"],
     "figures": ["f1", "f3"], "metrics": {"skew_exante": 0.236, "skew_expost": 0.230,
     "within_frac_m3": 1.026}},
    {"id": "W2", "frente": "Mechanism", "tag": "evidence/W2", "commit": "730fda7",
     "title": "Lei sem odds (Elo)", "blocks": ["08_mechanism_elo"],
     "figures": ["f2"], "metrics": {"corr_skew_upset": 0.826, "corr_elo_odds": 0.909}},
    {"id": "W3", "frente": "Invariance", "tag": "evidence/W3", "commit": "c68eb69",
     "title": "Invariância temporal (painel)", "blocks": ["09_panel_temporal"],
     "figures": ["f4"], "metrics": {"trend_beta_year": 0.00015, "trend_p": 0.73, "icc": 0.70}},
    {"id": "W5", "frente": "Robustness", "tag": "evidence/W5", "commit": "95d1a07",
     "title": "Mercado binário O/U 2.5", "blocks": ["10_overunder"],
     "figures": [], "metrics": {"skew_ou": -0.210, "within_frac": 0.996}},
    {"id": "W4", "frente": "Separation", "tag": "evidence/W4", "commit": "16b8c2e",
     "title": "Margem ortogonal + de-vig", "blocks": ["11_margin_robustness"],
     "figures": [], "metrics": {"overround_avg": 1.067, "overround_best": 1.009}},
    {"id": "P1", "frente": "Reframe", "tag": "evidence/P1", "commit": "f2bc443",
     "title": "Invariância intra-regime", "blocks": ["13_regimes"],
     "figures": [], "metrics": {"breaks_38_leagues": 1, "epl_breaks": 0}},
    {"id": "P2", "frente": "Hardening", "tag": "evidence/P2", "commit": "7f00792",
     "title": "Balanço da classificação (odds-free)", "blocks": ["14_balance_indices"],
     "figures": [], "metrics": {"corr_skew_nollscully": -0.625}},
    {"id": "P3", "frente": "Theory", "tag": "evidence/P3", "commit": "624547a",
     "title": "Lei derivada (ordered-probit)", "blocks": ["15_model"],
     "figures": ["f5"], "metrics": {"model_r": 0.904, "model_rmse": 0.024}},
    {"id": "P4", "frente": "Confound", "tag": "evidence/P4", "commit": "2bcef94",
     "title": "FLB estável (Angelini)", "blocks": ["16_flb_stability"],
     "figures": [], "metrics": {"mean_abs_ante_post": 0.015}},
    {"id": "B1", "frente": "Shape", "tag": "evidence/frente-B", "commit": "6946fc6",
     "title": "Invariância de FORMA (multi-momento)", "blocks": ["17_moments"],
     "figures": ["f6"], "metrics": {"model_r_var": 0.987, "model_r_skew": 0.904,
     "model_r_exkurt": 0.890}},
    {"id": "B2", "frente": "Collapse", "tag": "evidence/frente-B", "commit": "6946fc6",
     "title": "Colapso de distribuição", "blocks": ["18_collapse"],
     "figures": ["f7"], "metrics": {"uncond_ks": 0.474, "cond_ks": 0.059, "drop": 0.87}},
    {"id": "C1", "frente": "Pricing", "tag": "evidence/frente-C", "commit": "2b2d423",
     "title": "Sem prêmio além do FLB mecânico", "blocks": ["19_premium"],
     "figures": ["f8"], "metrics": {"ret": -0.0482, "vig": -0.0497, "flb": 0.0015,
     "resid_skew_r": 0.11}},
    {"id": "C2", "frente": "Preference", "tag": "evidence/frente-C", "commit": "2b2d423",
     "title": "CPT invariante (γ)", "blocks": ["20_cpt"],
     "figures": ["f9"], "metrics": {"gamma": 0.958, "gamma_sd_season": 0.020,
     "gamma_sd_league": 0.040, "trend_beta": 0.0003}},
    {"id": "E1", "frente": "Theory", "tag": "evidence/frente-E", "commit": "a70b790",
     "title": "Forma fechada de S(σ_L)", "blocks": ["21_closed_form"],
     "figures": ["f10"], "metrics": {"max_mc_err": 0.0015, "p0": 0.4392, "S0": 0.2449,
     "sigma_peak": 0.1226, "league_r": 0.903}},
    {"id": "E2", "frente": "Robustness", "tag": "evidence/frente-E", "commit": "a70b790",
     "title": "Robustez da distribuição de força", "blocks": ["22_force_robustness"],
     "figures": ["f11"], "metrics": {"max_dS_overall": 0.0320, "sd_between_leagues": 0.0518}},
    {"id": "G1", "frente": "Reliability", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "De-vig confiável + invariância de método", "blocks": ["23_devig_reliability"],
     "figures": ["f12"], "metrics": {"rel_global": 0.0000, "rel_sd_league": 0.0003,
     "skew_devig_range": 0.039}},
    {"id": "G2", "frente": "Robustness", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "Painel balanceado estrito (composição morta)", "blocks": ["24_balanced_panel"],
     "figures": ["f13"], "metrics": {"n_balanced": 15, "beta_balanced": -0.00013,
     "delta20_balanced": -0.003}},
    {"id": "G3", "frente": "Confidence", "tag": "evidence/frente-G", "commit": "a326910",
     "title": "IC por block-bootstrap sobre temporadas", "blocks": ["25_block_bootstrap"],
     "figures": [], "metrics": {"skew_ci_lo": 0.232, "skew_ci_hi": 0.239,
     "corr_ci_lo": -0.922, "corr_ci_hi": -0.876}},
    {"id": "D2", "frente": "Microstructure", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "Sharp vs soft (margem ortogonal na melhor odd)", "blocks": ["26_sharp_soft"],
     "figures": ["f14"], "metrics": {"d_skew_mean": 0.020, "corr_soft_sharp": 0.993,
     "corr_sharp_pfav": -0.876}},
    {"id": "D3", "frente": "Microstructure", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "z de Shin (dinheiro informado) como série", "blocks": ["27_shin_z_series"],
     "figures": ["f15"], "metrics": {"z_global": 0.0343, "z_sd_league": 0.0043,
     "corr_z_overround": 0.999}},
    {"id": "D4", "frente": "Third market", "tag": "evidence/frente-D", "commit": "4ccbc01",
     "title": "Handicap asiático: identidade num 3º mercado", "blocks": ["28_asian_handicap"],
     "figures": ["f16"], "metrics": {"p_fav_ah": 0.533, "skew_ah_global": -0.104,
     "within_frac_ah": 1.027, "league_identity_r": 0.80}},
    {"id": "F1", "frente": "Within-season", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Sazonalidade intra-temporada (drift leve)", "blocks": ["29_intraseason"],
     "figures": ["f17"], "metrics": {"global_span": 0.0149, "shift_mean": -0.0078,
     "shift_ci_lo": -0.0131, "shift_ci_hi": -0.0015}},
    {"id": "F2", "frente": "Tail cancellation", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Contribuição ao M₃ por competitividade do jogo", "blocks": ["30_game_contribution"],
     "figures": ["f18"], "metrics": {"share_weak_fav": 1.26, "share_strong_fav": -0.26}},
    {"id": "F3", "frente": "Team structure", "tag": "evidence/frente-F", "commit": "e5b04e1",
     "title": "Decomposição por time (dispersão de força)", "blocks": ["31_team_decomposition"],
     "figures": ["f19"], "metrics": {"corr_elo_teamskew": -0.444, "corr_elosd_leagueskew": -0.601}},
    {"id": "H2", "frente": "Open vs closed", "tag": "evidence/H2", "commit": "e0bc9fd",
     "title": "Liga aberta vs fechada (MLS na lei)", "blocks": ["32_open_vs_closed"],
     "figures": ["f20"], "metrics": {"mls_p_fav": 0.503, "mls_skew": 0.162,
     "mls_pfav_rank": 22, "mls_residual": -0.059}},
    {"id": "C3", "frente": "Staking", "tag": "evidence/C3", "commit": "e0bc9fd",
     "title": "Kelly/staking sob a estrutura de skewness", "blocks": ["33_kelly_staking"],
     "figures": ["f21"], "metrics": {"frac_positive_ev": 0.0, "skew_term_dog": 0.598,
     "skew_term_fav": 0.010}},
    {"id": "E3", "frente": "Theory", "tag": "evidence/E3", "commit": "e0bc9fd",
     "title": "Calibração por liga (cutoff de empate endógeno)", "blocks": ["34_per_league_calibration"],
     "figures": ["f22"], "metrics": {"corr_sigma_pfav": 0.874, "corr_c_draw": 0.906,
     "skew_model_r": 0.905}},
    # ── 2ª rodada (dataset congelado) ──
    {"id": "I", "frente": "Cross-model", "tag": "evidence/frente-I", "commit": "7a45759",
     "title": "Validação cruzada do mecanismo (Poisson de gols)", "blocks": ["35_poisson_crossmodel"],
     "figures": ["f23"], "metrics": {"corr_pfav": 0.972, "corr_skew": 0.925,
     "league_r_poisson": 0.85, "n_league_seasons": 617}},
    {"id": "J", "frente": "Dynamic", "tag": "evidence/frente-J", "commit": "74f9c2e",
     "title": "Chegada de informação HT→FT (identidade dinâmica)", "blocks": ["36_inplay_resolution"],
     "figures": ["f24"], "metrics": {"skew_pregame": 0.239, "skew_behind": 2.084,
     "skew_ahead2": -3.908, "martingale_err": 0.0035}},
    {"id": "K", "frente": "Diversification", "tag": "evidence/frente-K", "commit": "b4b90eb",
     "title": "Diversificação (skewness = fenômeno de aposta única)", "blocks": ["37_diversification"],
     "figures": ["f25"], "metrics": {"skew_single_fav": 0.230, "skew_single_dog": 2.254,
     "n_to_gaussian_dog": 509}},
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

    # tabela humana
    lines = [
        "# LINEAGE — ledger de evidências (versionamento)",
        "",
        "> Gerado por `analysis/build_lineage.py` (não editar à mão). Cada fase pina",
        "> seu(s) número(s)-título à VERSÃO exata do código (commit + tag `evidence/*`)",
        f"> e ao DATASET (`sha256:{data['sha256']}`, {data.get('rows')} jogos,",
        f"> {data.get('leagues')} ligas). Volte a qualquer estado com",
        "> `git checkout <tag>`; audite mudança de resultado com `--check`.",
        "",
        f"**HEAD na geração:** `{head['short']}`"
        + ("  ⚠️ working tree DIRTY" if head["dirty"] else "  (clean)"),
        "",
        "| Fase | Frente | Achado | Blocos | Figuras | Números-título | Commit | Tag |",
        "|------|--------|--------|--------|---------|----------------|--------|-----|",
    ]
    for r in rows:
        met = " · ".join(f"{k}={v}" for k, v in r["metrics"].items())
        blk = ", ".join(r["blocks"])
        fig = ", ".join(r["figures"]) or "—"
        lines.append(
            f"| **{r['id']}** | {r['frente']} | {r['title']} | {blk} | {fig} | "
            f"{met} | `{r['commit']}` ({r['commit_date']}) | `{r['tag']}` |")
    lines += ["",
        "## Tags de versionamento (`evidence/*`)",
        "Uma tag anotada por marco de evidência aponta o commit que estabeleceu",
        "aqueles números. `git tag -n` lista; `git checkout evidence/frente-E`",
        "recupera o código exato da Frente E.",
        ""]
    LMD.write_text("\n".join(lines) + "\n")
    print(f"-> {LJSON.relative_to(ROOT)} ({len(rows)} fases) | -> {LMD.relative_to(ROOT)}")
    print(f"   data sha256:{data['sha256']} · HEAD {head['short']}"
          + (" (DIRTY)" if head["dirty"] else ""))


def check():
    """Audita DRIFT: compara números registrados no ledger com os carimbos de
    execução mais recentes (outputs/_provenance/<bloco>.json)."""
    if not LJSON.exists():
        print("lineage.json ausente — rode sem --check primeiro."); return
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
                        # tolerância absorve ruído de Monte Carlo (~0.3%) mas pega
                        # mudança real de script (que move números bem além disso)
                        tol = max(1e-3, 0.02 * abs(rec))
                        if abs(v - rec) > tol:
                            drift.append((ph["id"], blk, k, rec, v, st["git"]["short"]))
    print(f"[lineage --check] {checked} métricas confrontadas com carimbos de execução.")
    if not drift:
        print("  ✓ sem drift: os resultados batem com o ledger versionado.")
    else:
        print(f"  ⚠️ DRIFT em {len(drift)} métrica(s) — script mudou o resultado:")
        for pid, blk, k, rec, v, sha in drift:
            print(f"    {pid}/{blk}: {k}  ledger={rec}  agora={v}  (@{sha})")


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
