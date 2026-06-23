# skew-meter — serviço `/measure`

Produtização do aparelho de **similaridade de assimetrias**: mede a assinatura de
skewness de uma entrada nova (liga, janela, mercado) e a situa contra a lei
`skew = f(competitividade)` — tudo sobre o `skewlib`, sem tocar o dataset bruto.

O serviço carrega a **lei calibrada** e a **referência por liga** do
`site/src/data/findings.json` (o mesmo artefato auditado, drift-clean, que alimenta
o site). Runtime leve → deployável.

## Rodar (local)

```bash
cd study
./.venv/bin/pip install -r api/requirements.txt      # fastapi, uvicorn, pydantic
./.venv/bin/uvicorn api.main:app --reload --port 8000
# OpenAPI interativo: http://localhost:8000/docs
```

## Endpoints

| Método | Rota | O quê |
|--------|------|-------|
| GET  | `/health`    | vivo + sha do artefato + tamanho da lei |
| GET  | `/integrity` | monitor: o `findings.json` é coerente? (contagem, completude, suporte da lei, margem, resíduos < espalhamento) |
| POST | `/measure`   | assinatura de assimetria de uma entrada + vizinhos + veredito de equivalência + anomalias |
| POST | `/reload`    | hot-reload do `findings.json` |

## `/measure` — modos (escada de custo)

**com-odds** — odds 1X2 por jogo (de-vig barato por inverse-odds, corr≈1.0 com Shin):

```bash
curl -s localhost:8000/measure -H 'content-type: application/json' -d '{
  "mode": "with-odds",
  "odds_hda": [[1.5,4.0,7.0],[2.1,3.3,3.6],[1.2,6.5,13.0]]
}'
```

Alternativa: `{"p_fav":[...], "o_fav":[...]}` (probabilidades já de-vigadas; `o_fav`
default = odds justas `1/p_fav`).

**odds-free** — só a taxa de zebra do Elo (nenhuma odd); prevê a skew pela lei
(teto corr≈0.83):

```bash
curl -s localhost:8000/measure -H 'content-type: application/json' \
  -d '{"mode":"odds-free","upset_rate":0.46}'
```

### Resposta (com-odds), campos principais

- `skew`, `var`, `exkurt`, `competitiveness` (média de p_fav), `skew_se` (piso bootstrap)
- `predicted_skew` (a lei na competitividade), `residual` (assimetria idiossincrática)
- `shape_label`, `nearest_raw` / `nearest_residual` (vizinhos)
- `equivalence` — veredito TOST contra a liga mais próxima (`same_asymmetry`)
- `anomalies` — `extrapolation` | `insufficient_sample` | `outlier_residual` | `low_n`

## Testes

```bash
cd study && ./.venv/bin/python -m pytest api/test_api.py -q
```
