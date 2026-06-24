"""skew-meter as a service — thin FastAPI over the engine (api/engine.py).

Run (from the study/ directory):
    uvicorn api.main:app --reload --port 8000

Endpoints:
    GET  /health      — alive + artefact sha + law size
    GET  /integrity    — monitor: is the reference (findings.json) coherent?
    POST /measure      — asymmetry signature of a new input
                         (with-odds | odds-free mode) + neighbours + verdict
    POST /reload       — reloads findings.json (artefact hot-reload)
    GET  /docs         — interactive OpenAPI (Swagger)
"""
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .engine import Engine, p_fav_from_odds_hda
from .schemas import MeasureRequest

app = FastAPI(
    title="skew-meter",
    version="0.1.0",
    summary="Asymmetry similarity as a service — measures the skewness "
            "signature of a league/window/market and situates it against the law.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

engine = Engine()


@app.get("/health")
def health():
    return {"status": "ok", "findings_sha": engine.sha,
            "n_leagues": len(engine.leagues), "law_points": len(engine.law["cpf"]),
            "dataset": {"sha256": engine.meta.get("sha256"),
                        "n_matches": engine.meta.get("n_matches"),
                        "devig": engine.meta.get("devig")}}


@app.get("/integrity")
def integrity():
    return engine.integrity()


@app.post("/reload")
def reload():
    engine.load()
    return {"reloaded": True, "findings_sha": engine.sha}


@app.post("/measure")
def measure(req: MeasureRequest):
    try:
        if req.mode == "odds-free":
            return engine.measure_oddsfree(req.upset_rate)

        if req.odds_hda is not None:
            p, o = p_fav_from_odds_hda(req.odds_hda)
        else:
            p = np.asarray(req.p_fav, float)
            o = np.asarray(req.o_fav, float) if req.o_fav is not None else 1.0 / p

        if np.any(~np.isfinite(p)) or np.any(p <= 0) or np.any(p >= 1):
            raise ValueError("p_fav must be finite and in (0, 1)")
        if np.any(~np.isfinite(o)) or np.any(o < 1.0):
            raise ValueError("o_fav must be finite decimal odds ≥ 1")

        return engine.measure_odds(p, o, B=req.bootstrap)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
