# CLAUDE.md — project conventions

Context for Claude Code when continuing this study.

## What it is
Empirical study of skewness in football betting markets. Final goal: a paper.
Thesis: skewness is a structural invariant (not dynamic), a function of league
competitiveness. See `docs/FINDINGS.md` for the current state.

## Architecture
- All reusable logic lives in `skewlib/`. Scripts in `analysis/` are thin and
  import from `skewlib` — **do not duplicate logic** in the scripts.
- Adding a new capability = a function in `skewlib`, then a thin script that uses it.
- Parameters (window, step, cut-off) only in `skewlib/config.py`.
- **Multi-sport:** the core (`skewlib/canonical.py` + `skewmeter`) is sport-agnostic
  and consumes the canonical table (`docs/DATA-SCHEMA.md`). Adding a sport/market =
  one adapter in `skewlib/adapters/` (maps raw→canonical + taxonomy), registered in
  `adapters/__init__.py`. **Do not** branch the core per sport. Football delegates
  de-vig to the frozen path → bit-identical numbers (assertion in `47_canonical.py`).

## Data
- `data/` is never committed. Point `config.DATA_PATH` at the local dump.
- On our own infra, prefer football-data.co.uk as the canonical source and stack
  all seasons/leagues (more coverage than the bootstrap mirror).
- Always filter invalid odds (`MIN_ODD`) — the data has zeros/dirty values.

## Statistical rigour (do not regress)
- For inference, use **non-overlapping windows** (`overlap=False`). Overlap inflates
  autocorrelation — that is what masked "persistence" in v1.
- Skewness is a 3rd-order moment → standard error by bootstrap, never assume normal.
- Double confirmation of stationarity (ADF + KPSS).
- Report sensitivity to window size as robustness.

## State and next fronts
Central thesis **proven** (W1–W5 + P1–P5 + B + C + E, blocks 00–22; see
`docs/FINDINGS.md`). **Open fronts, prioritised and detailed in
`docs/RESEARCH-AGENDA.md`** — remaining in the dataset: G (adversarial robustness,
next), F (micro), D2–D4 (microstructure), H2 (open×close), C3 (Kelly), E3
(per-league calibration). `docs/LITERATURA.md` anchors everything.

## Lineage / provenance / versioning (DO NOT skip)
Every finding is pinned to the exact version that produced it. Discipline when
closing a front:
1. **Stamp** — every new block ends with
   `prov.write_stamp("NN_name", metrics={...})` (headline numbers), writing the git
   sha + dataset hash + libs to `outputs/_provenance/` (regenerable).
2. **Timeline** — add the phase to `docs/FINDINGS.md` (Phase X) **and** to
   `site/src/components/Timeline.astro` (one entry per sub-finding).
3. **Ledger** — register the phase in `analysis/build_lineage.py:PHASES` (blocks,
   figures, numbers, commit, tag), run `python analysis/build_lineage.py` to
   regenerate `lineage.json` + `docs/LINEAGE.md`.
4. **Version** — commit; then `git tag -a evidence/<front> <sha> -m "..."` on the
   commit that established the numbers (`--tags` suggests the commands).
5. **Audit** — `python analysis/build_lineage.py --check` compares the run stamps
   against the ledger and flags **DRIFT** (script changed ⇒ number changed).
   `run.sh` already runs this at the end of the pipeline. If there is legitimate
   drift, update the ledger + a new tag — git keeps the history of the old number.
`git checkout evidence/frente-E` recovers the exact code of any evidence (existing
tags keep their original `frente-` names).

## Style
- English in comments and docs. Clean code, small functions.
- Stack: Python, pandas/numpy/scipy/statsmodels/ruptures.
