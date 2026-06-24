#!/usr/bin/env bash
# run.sh — full skewness study pipeline, in one command.
#
# Does, in order: prepares the environment (venv + deps), fetches the dataset and
# runs analysis blocks 00→06. Each analysis/ script imports from skewlib/ and
# needs the project directory on PYTHONPATH (module names start with a digit,
# so we invoke by path, not with `python -m`).
#
# Usage:
#   ./run.sh                # everything: setup + fetch + analyses
#   ./run.sh --no-fetch     # skips the download (uses existing data/matches.csv)
#   ./run.sh --no-venv      # uses the current python, without creating .venv
#   SKEW_PY=python3.11 ./run.sh   # choose the base interpreter
set -euo pipefail

cd "$(dirname "$0")"

FETCH=1
USE_VENV=1
for arg in "$@"; do
  case "$arg" in
    --no-fetch) FETCH=0 ;;
    --no-venv)  USE_VENV=0 ;;
    -h|--help)  sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

PY="${SKEW_PY:-python3}"

# 1) environment: venv + dependencies (idempotent)
if [ "$USE_VENV" -eq 1 ]; then
  if [ ! -d .venv ]; then
    echo "==> creating .venv"
    "$PY" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  PY=python
fi

echo "==> installing dependencies (requirements.txt)"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r requirements.txt

# the project needs itself on the path for `from skewlib import ...`
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

# 2) data: fetch only if needed
if [ "$FETCH" -eq 1 ] && [ ! -f data/matches.csv ]; then
  echo "==> 00 fetch — downloading dataset"
  "$PY" analysis/00_fetch_data.py
else
  echo "==> 00 fetch — skipped (data/matches.csv present or --no-fetch)"
fi

if [ ! -f data/matches.csv ]; then
  echo "ERROR: data/matches.csv missing. Run without --no-fetch or point" >&2
  echo "       skewlib/config.py:DATA_PATH to your dump." >&2
  exit 1
fi

# 3) analyses 01→06 (their order does not matter, but we follow the numbering)
for script in \
  analysis/01_baseline.py \
  analysis/02_robustness.py \
  analysis/03_decomposition.py \
  analysis/04_dynamics.py \
  analysis/05_cross_book.py \
  analysis/06_league_hetero.py \
  analysis/07_devig_exante.py \
  analysis/08_mechanism_elo.py \
  analysis/09_panel_temporal.py \
  analysis/10_overunder.py \
  analysis/11_margin_robustness.py \
  analysis/13_regimes.py \
  analysis/14_balance_indices.py \
  analysis/15_model.py \
  analysis/16_flb_stability.py \
  analysis/17_moments.py \
  analysis/18_collapse.py \
  analysis/19_premium.py \
  analysis/20_cpt.py \
  analysis/21_closed_form.py \
  analysis/22_force_robustness.py \
  analysis/23_devig_reliability.py \
  analysis/24_balanced_panel.py \
  analysis/25_block_bootstrap.py \
  analysis/26_sharp_soft.py \
  analysis/27_shin_z_series.py \
  analysis/28_asian_handicap.py \
  analysis/29_intraseason.py \
  analysis/30_game_contribution.py \
  analysis/31_team_decomposition.py \
  analysis/32_open_vs_closed.py \
  analysis/33_kelly_staking.py \
  analysis/34_per_league_calibration.py \
  analysis/35_poisson_crossmodel.py \
  analysis/36_inplay_resolution.py \
  analysis/37_diversification.py \
  analysis/38_home_advantage.py \
  analysis/39_tail_risk.py \
  analysis/40_entropy_comoment.py \
  analysis/41_model_battery.py \
  analysis/44_var.py \
  analysis/45_skewmeter.py \
  analysis/46_bettype.py \
  analysis/47_canonical.py \
  analysis/51_temporal_equivalence.py \
  analysis/12_figures.py
do
  echo
  echo "================================================================"
  echo "==> ${script}"
  echo "================================================================"
  "$PY" "$script"
done

# 4) site/service data: (re)generates site/src/data/findings.json from the
#    same audited computations (feeds the widget and the /measure API).
echo
echo "================================================================"
echo "==> export — findings.json (site + API)"
echo "================================================================"
"$PY" analysis/export_site_data.py

# 5) evidence ledger: (re)generates lineage.json + docs/LINEAGE.md and audits drift
echo
echo "================================================================"
echo "==> lineage — evidence ledger + drift audit"
echo "================================================================"
"$PY" analysis/build_lineage.py
"$PY" analysis/build_lineage.py --check

# 6) EXTERNAL DATA fronts (canonical football-data.co.uk): opening→closing odds
#    (D1) and pre-2005 history (P6). They need the network to download
#    data/canonical/. They do not abort the pipeline if the network/source fails.
echo
echo "================================================================"
echo "==> external-data fronts (canonical): fetch + D1 + pre-2005"
echo "================================================================"
( "$PY" analysis/50_fetch_canonical.py \
  && "$PY" analysis/42_open_close.py \
  && "$PY" analysis/43_pre2005.py ) \
  || echo "   (skipped — no network/canonical source; the rest of the pipeline is complete)"

# 7) external validity (tennis, tennis-data.co.uk via HTTP): fetches only if absent
#    and runs block 48. Also does not abort the pipeline if the network/source fails.
echo
echo "================================================================"
echo "==> external validity (tennis): fetch + block 48"
echo "================================================================"
( { [ -f data/tennis.csv ] || "$PY" analysis/00b_fetch_tennis.py; } \
  && "$PY" analysis/48_tennis.py ) \
  || echo "   (skipped — no tennis.csv/network/openpyxl; the core is complete)"

# 8) external validity (basketball, sportsbookreviewsonline.com): fetches only if absent
#    and runs block 49 (moneyline market, NBA). Does not abort the pipeline if the network fails.
echo
echo "================================================================"
echo "==> external validity (basketball): fetch + block 49"
echo "================================================================"
( { [ -f data/basketball.csv ] || "$PY" analysis/00c_fetch_basketball.py; } \
  && "$PY" analysis/49_basketball.py ) \
  || echo "   (skipped — no basketball.csv/network; the core is complete)"

echo
echo "==> pipeline complete. Series/tables in outputs/; evidence in lineage.json"
