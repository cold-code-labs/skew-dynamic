# skew-meter — `/measure` service

Productisation of the **asymmetry-similarity** apparatus: it measures the skewness
signature of a new input (league, window, market) and situates it against the law
`skew = f(competitiveness)` — all on top of `skewlib`, without touching the raw dataset.

The service loads the **calibrated law** and the **per-league reference** from
`site/src/data/findings.json` (the same audited, drift-clean artefact that feeds
the site). Lightweight runtime → deployable.

## Run (local)

```bash
cd study
./.venv/bin/pip install -r api/requirements.txt      # fastapi, uvicorn, pydantic
./.venv/bin/uvicorn api.main:app --reload --port 8000
# Interactive OpenAPI: http://localhost:8000/docs
```

## Endpoints

| Method | Route | What |
|--------|------|-------|
| GET  | `/health`    | alive + artefact sha + law size |
| GET  | `/integrity` | monitor: is `findings.json` coherent? (count, completeness, law support, margin, residuals < spread) |
| POST | `/measure`   | asymmetry signature of an input + neighbours + equivalence verdict + anomalies |
| POST | `/reload`    | hot-reload of `findings.json` |

## `/measure` — modes (cost ladder)

**with-odds** — 1X2 odds per match (cheap de-vig by inverse-odds, corr≈1.0 with Shin):

```bash
curl -s localhost:8000/measure -H 'content-type: application/json' -d '{
  "mode": "with-odds",
  "odds_hda": [[1.5,4.0,7.0],[2.1,3.3,3.6],[1.2,6.5,13.0]]
}'
```

Alternative: `{"p_fav":[...], "o_fav":[...]}` (already de-vigged probabilities; `o_fav`
default = fair odds `1/p_fav`).

**odds-free** — only the Elo upset rate (no odds at all); predicts the skew from the law
(ceiling corr≈0.83):

```bash
curl -s localhost:8000/measure -H 'content-type: application/json' \
  -d '{"mode":"odds-free","upset_rate":0.46}'
```

### Response (with-odds), main fields

- `skew`, `var`, `exkurt`, `competitiveness` (mean of p_fav), `skew_se` (bootstrap floor)
- `predicted_skew` (the law at the competitiveness), `residual` (idiosyncratic asymmetry)
- `shape_label`, `nearest_raw` / `nearest_residual` (neighbours)
- `equivalence` — TOST verdict against the nearest league (`same_asymmetry`)
- `anomalies` — `extrapolation` | `insufficient_sample` | `outlier_residual` | `low_n`

## Tests

```bash
cd study && ./.venv/bin/python -m pytest api/test_api.py -q
```
