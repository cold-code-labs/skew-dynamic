"""Proveniência e versionamento: carimba CADA resultado com a versão exata do
código (commit git) + o hash do dataset congelado + as versões das libs. É a
cola entre evidência e versionamento — se um script mudar e um número se mover, o
carimbo muda e o histórico (git) permite rastrear quando e por quê.

Uso típico num bloco de análise:
    from skewlib import provenance as prov
    prov.write_stamp("23_adversarial", metrics={"global_skew": 0.236})
gera `outputs/_provenance/23_adversarial.json` (registro de execução, regenerável)
com {git, data, env, metrics, generated_at}. O ledger versionado (lineage.json /
docs/LINEAGE.md) é montado por `analysis/build_lineage.py` a partir desses números.
"""
import json, subprocess, sys, hashlib
from datetime import datetime, timezone
from pathlib import Path
from . import config as C

ROOT = Path(__file__).resolve().parents[1]            # study/


def _git(*args, default=""):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return default


def git_info():
    """Estado do repositório no momento da execução."""
    commit = _git("rev-parse", "HEAD")
    dirty = bool(_git("status", "--porcelain"))
    return {
        "commit": commit,
        "short": commit[:8],
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": dirty,                                # True = há mudanças não commitadas
        "describe": _git("describe", "--tags", "--always", "--dirty", default=commit[:8]),
    }


def data_hash():
    """Identidade do dataset congelado (de PROVENANCE.json; fallback = hash do CSV)."""
    pf = C.DATA_PATH.parent / "PROVENANCE.json"
    if pf.exists():
        p = json.loads(pf.read_text())
        return {"sha256": p.get("sha256", "")[:16],
                "rows": p.get("analysis_rows_ge2005") or p.get("rows"),
                "leagues": p.get("leagues"),
                "date_min": p.get("date_min"), "date_max": p.get("date_max")}
    if C.DATA_PATH.exists():
        h = hashlib.sha256(C.DATA_PATH.read_bytes()).hexdigest()
        return {"sha256": h[:16], "rows": None}
    return {"sha256": "", "rows": None}


def env_versions():
    mods = {}
    for name in ("numpy", "pandas", "scipy", "statsmodels"):
        try:
            mods[name] = __import__(name).__version__
        except Exception:
            mods[name] = None
    mods["python"] = sys.version.split()[0]
    return mods


def stamp(metrics=None):
    """Carimbo completo: git + dados + libs + métricas-chave + timestamp."""
    return {
        "git": git_info(),
        "data": data_hash(),
        "env": env_versions(),
        "metrics": metrics or {},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_stamp(name, metrics=None):
    """Grava o carimbo de execução de um bloco em outputs/_provenance/<name>.json."""
    s = stamp(metrics)
    d = C.OUTDIR / "_provenance"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2))
    flag = " (DIRTY)" if s["git"]["dirty"] else ""
    print(f"  [prov] {name} @ {s['git']['short']}{flag} · data {s['data']['sha256']}")
    return s
