"""Tests for the /measure service — independent of the raw dataset (only findings.json).

    cd study && ./.venv/bin/python -m pytest api/test_api.py -q
"""
import numpy as np
from fastapi.testclient import TestClient
from api.main import app

c = TestClient(app)


def test_health():
    j = c.get("/health").json()
    assert j["status"] == "ok"
    assert j["n_leagues"] > 0 and j["law_points"] > 0


def test_integrity_green():
    j = c.get("/integrity").json()
    assert j["ok"] is True
    assert all(chk["ok"] for chk in j["checks"])


def test_measure_with_pfav_structure():
    # synthetic input (does not follow the real conditional shape → free residual);
    # here we check only the STRUCTURE of the response and the engine invariants.
    rng = np.random.default_rng(0)
    p = np.clip(rng.normal(0.52, 0.08, 4000), 0.05, 0.95)
    j = c.post("/measure", json={"mode": "with-odds", "p_fav": p.tolist(),
                                 "bootstrap": 120}).json()
    assert j["mode"] == "with-odds" and j["n"] == 4000
    assert np.isfinite(j["skew"]) and j["skew_se"] > 0
    assert abs(j["residual"] - (j["skew"] - j["predicted_skew"])) < 1e-3
    assert j["equivalence"]["margin"] > 0
    assert isinstance(j["nearest_residual"], list) and len(j["nearest_residual"]) == 3


def test_measure_odds_hda():
    j = c.post("/measure", json={"mode": "with-odds",
               "odds_hda": [[1.5, 4.0, 7.0], [2.1, 3.3, 3.6]]}).json()
    assert "skew" in j
    # 2 matches → noise dominates: should flag insufficient sample
    assert any(a["flag"] == "low_n" for a in j["anomalies"])


def test_measure_oddsfree():
    j = c.post("/measure", json={"mode": "odds-free", "upset_rate": 0.46}).json()
    assert j["mode"] == "odds-free"
    assert 0.4 < j["competitiveness"] < 0.7
    assert j["ceiling_corr"] > 0
    assert len(j["nearest_by_upset"]) == 3


def test_validation_errors():
    assert c.post("/measure", json={"mode": "odds-free"}).status_code == 422
    assert c.post("/measure", json={"mode": "with-odds"}).status_code == 422
    # p_fav outside (0,1)
    assert c.post("/measure", json={"mode": "with-odds",
                  "p_fav": [1.4, 0.5]}).status_code == 422
