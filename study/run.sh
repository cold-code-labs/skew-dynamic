#!/usr/bin/env bash
# run.sh — pipeline completa do estudo de skewness, num comando.
#
# Faz, em ordem: prepara ambiente (venv + deps), baixa o dataset e roda os
# blocos de análise 00→06. Cada script de analysis/ importa de skewlib/ e
# precisa do diretório do projeto no PYTHONPATH (nomes de módulo começam com
# dígito, então invocamos por caminho, não com `python -m`).
#
# Uso:
#   ./run.sh                # tudo: setup + fetch + análises
#   ./run.sh --no-fetch     # pula o download (usa data/matches.csv existente)
#   ./run.sh --no-venv      # usa o python atual, sem criar .venv
#   SKEW_PY=python3.11 ./run.sh   # escolhe o interpretador base
set -euo pipefail

cd "$(dirname "$0")"

FETCH=1
USE_VENV=1
for arg in "$@"; do
  case "$arg" in
    --no-fetch) FETCH=0 ;;
    --no-venv)  USE_VENV=0 ;;
    -h|--help)  sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

PY="${SKEW_PY:-python3}"

# 1) ambiente: venv + dependências (idempotente)
if [ "$USE_VENV" -eq 1 ]; then
  if [ ! -d .venv ]; then
    echo "==> criando .venv"
    "$PY" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  PY=python
fi

echo "==> instalando dependências (requirements.txt)"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r requirements.txt

# o projeto precisa de si mesmo no path para `from skewlib import ...`
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

# 2) dados: baixa só se necessário
if [ "$FETCH" -eq 1 ] && [ ! -f data/matches.csv ]; then
  echo "==> 00 fetch — baixando dataset"
  "$PY" analysis/00_fetch_data.py
else
  echo "==> 00 fetch — pulado (data/matches.csv presente ou --no-fetch)"
fi

if [ ! -f data/matches.csv ]; then
  echo "ERRO: data/matches.csv ausente. Rode sem --no-fetch ou aponte" >&2
  echo "      skewlib/config.py:DATA_PATH para o seu dump." >&2
  exit 1
fi

# 3) análises 01→06 (a ordem não importa entre si, mas seguimos a numeração)
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
  analysis/12_figures.py
do
  echo
  echo "================================================================"
  echo "==> ${script}"
  echo "================================================================"
  "$PY" "$script"
done

# 4) ledger de evidências: (re)gera lineage.json + docs/LINEAGE.md e audita drift
echo
echo "================================================================"
echo "==> lineage — ledger de evidências + auditoria de drift"
echo "================================================================"
"$PY" analysis/build_lineage.py
"$PY" analysis/build_lineage.py --check

echo
echo "==> pipeline concluída. Séries/tabelas em outputs/; evidências em lineage.json"
