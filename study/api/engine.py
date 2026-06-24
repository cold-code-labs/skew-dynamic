"""Engine for the /measure service — wraps skewlib and the already-calibrated law.

Instead of touching the raw dataset (43 MB) at runtime, the service loads the LAW
(skew=f(competitiveness)) and the per-league reference from the versioned
`findings.json` — the same artefact that feeds the site. This keeps the service
light and deployable, and uses exactly the audited numbers (drift-clean). The
signature of a new input (skew/var/exkurt + bootstrap SE) reuses skewlib without
duplicating logic.

Two modes, along the study's cost ladder:
  • with-odds  — takes 1X2 odds (or already de-vigged p_fav); de-vigs by inverse-odds
                 (gauge_cheap, corr≈1.0 with Shin) and measures the full signature.
  • odds-free  — takes only the upset rate (Elo, no odds at all); predicts the skew
                 from the law via the competitiveness→p_fav map (ceiling corr≈0.83).
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]          # study/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from skewlib import exante, skewmeter as sm          # noqa: E402

FINDINGS = ROOT.parent / "site" / "src" / "data" / "findings.json"


class Engine:
    """Immutable state loaded from findings.json. Reloadable (hot-reload)."""

    def __init__(self, path: Path = FINDINGS):
        self.path = Path(path)
        self.load()

    # ── load / integrity ───────────────────────────────────────────────────
    def load(self):
        raw = self.path.read_bytes()
        self.sha = hashlib.sha256(raw).hexdigest()[:12]
        d = json.loads(raw)
        self.meta = d["meta"]
        SM = d["skewmeter"]
        curve = SM["curve"]
        cpf = np.array([c["p_fav"] for c in curve], float)
        csk = np.array([c["skew"] for c in curve], float)
        o = np.argsort(cpf)
        self.law = {"cpf": cpf[o], "csk": csk[o]}
        self.comp_lo, self.comp_hi = float(cpf.min()), float(cpf.max())
        self.margin = float(SM["margin"])
        self.sd_between = float(SM["sd_between"])
        self.noise_floor = float(SM["noise_floor"])
        self.corr_oddsfree = float(SM["corr_oddsfree"])
        self.r2_1param = float(SM["r2_1param"])
        self.leagues = d["leagues"]
        self.max_abs_residual = max(abs(L["residual"]) for L in self.leagues
                                    if L.get("residual") is not None)
        # odds-free map: competitiveness (Elo upset) → p_fav, OLS over the leagues
        u = np.array([L["upset"] for L in self.leagues if L.get("upset") is not None])
        pf = np.array([L["p_fav"] for L in self.leagues if L.get("upset") is not None])
        A = np.column_stack([np.ones_like(u), u])
        self._upset_beta = np.linalg.lstsq(A, pf, rcond=None)[0]   # [a, b]: p_fav ≈ a + b·upset

    def predict(self, comp: float) -> float:
        return sm.predict_skew(float(comp), self.law)

    # ── location against the cloud of leagues ──────────────────────────────
    def _nearest(self, key: str, val: float, n: int = 3):
        pool = [L for L in self.leagues if L.get(key) is not None]
        pool.sort(key=lambda L: abs(L[key] - val))
        return [{"code": L["code"], "name": L["name"],
                 "delta": round(abs(L[key] - val), 4), key: round(L[key], 4)}
                for L in pool[:n]]

    def _equivalence(self, residual: float, se_in: float):
        """TOST verdict against the nearest league in residual: does the
        conditioned asymmetry gap fit within the ½·sd margin (= noise)?"""
        pool = [L for L in self.leagues if L.get("residual") is not None]
        pool.sort(key=lambda L: abs(L["residual"] - residual))
        nb = pool[0]
        d = abs(residual - nb["residual"])
        se = float(np.hypot(se_in, nb.get("se") or 0.0))
        equivalent = bool(d + 1.645 * se < self.margin)   # 90% CI ⊂ [−margin, margin]
        return {"code": nb["code"], "name": nb["name"],
                "residual_gap": round(d, 4), "se_combined": round(se, 4),
                "margin": round(self.margin, 4), "same_asymmetry": equivalent}

    def _anomalies(self, comp, se_in, residual, n):
        flags = []
        if comp < self.comp_lo or comp > self.comp_hi:
            flags.append({"flag": "extrapolation", "detail":
                          f"competitiveness {comp:.3f} outside law support "
                          f"[{self.comp_lo:.3f}, {self.comp_hi:.3f}]"})
        if se_in > self.margin:
            flags.append({"flag": "insufficient_sample", "detail":
                          f"SE {se_in:.4f} exceeds equivalence margin "
                          f"{self.margin:.4f} — cannot resolve the league"})
        if abs(residual) > self.max_abs_residual:
            flags.append({"flag": "outlier_residual", "detail":
                          f"|residual| {abs(residual):.4f} beyond the observed "
                          f"league range ({self.max_abs_residual:.4f})"})
        if n < 50:
            flags.append({"flag": "low_n", "detail":
                          f"{n} matches — signature is noise-dominated"})
        return flags

    # ── with-odds mode ─────────────────────────────────────────────────────
    def measure_odds(self, p, o, B=300, seed=42):
        """Full signature from per-match p_fav (and odds)."""
        p = np.asarray(p, float); o = np.asarray(o, float)
        sig = sm.measure(p, o)
        comp = sig["comp"]
        residual = sig["skew"] - self.predict(comp)
        se = sm.skew_se(p, o, B=B, seed=seed)
        return self._assemble("with-odds", sig, comp, residual, se, len(p))

    # ── odds-free mode ─────────────────────────────────────────────────────
    def measure_oddsfree(self, upset_rate: float):
        """Prediction from the law using ONLY the upset rate (Elo). No measured
        signature — the ceiling with no odds at all (corr≈0.83)."""
        a, b = self._upset_beta
        comp = float(a + b * float(upset_rate))
        skew_hat = self.predict(comp)
        flags = []
        if comp < self.comp_lo or comp > self.comp_hi:
            flags.append({"flag": "extrapolation", "detail":
                          f"implied competitiveness {comp:.3f} outside law support"})
        return {
            "mode": "odds-free",
            "input": {"upset_rate": round(float(upset_rate), 4)},
            "competitiveness": round(comp, 4),
            "skew_predicted": round(skew_hat, 4),
            "ceiling_corr": self.corr_oddsfree,
            "nearest_by_upset": self._nearest("upset", float(upset_rate)),
            "anomalies": flags,
            "note": ("odds-free estimate: skewness predicted from results-only "
                     "competitiveness via the law; no measured asymmetry. Ceiling "
                     f"corr≈{self.corr_oddsfree} vs {self.r2_1param:.2f} R² with odds."),
        }

    def _assemble(self, mode, sig, comp, residual, se, n):
        return {
            "mode": mode,
            "n": int(n),
            "skew": round(sig["skew"], 4),
            "var": round(sig["var"], 4),
            "exkurt": round(sig["exkurt"], 4),
            "competitiveness": round(comp, 4),
            "skew_se": round(se, 4),
            "predicted_skew": round(self.predict(comp), 4),
            "residual": round(residual, 4),
            "shape_label": _shape_label(sig["skew"]),
            "nearest_raw": self._nearest("skew", sig["skew"]),
            "nearest_residual": self._nearest("residual", residual),
            "equivalence": self._equivalence(residual, se),
            "anomalies": self._anomalies(comp, se, residual, n),
        }

    # ── integrity monitor ──────────────────────────────────────────────────
    def integrity(self):
        checks = []

        def chk(name, ok, detail=""):
            checks.append({"check": name, "ok": bool(ok), "detail": detail})

        n = len(self.leagues)
        chk("leagues_count", n == self.meta.get("leagues"),
            f"{n} leagues vs meta {self.meta.get('leagues')}")
        chk("leagues_complete",
            all(L.get(k) is not None for L in self.leagues
                for k in ("skew", "p_fav", "residual")),
            "all leagues have skew/p_fav/residual")
        chk("law_monotone_support", self.comp_hi > self.comp_lo,
            f"law support [{self.comp_lo:.3f}, {self.comp_hi:.3f}]")
        chk("margin_positive", self.margin > 0, f"margin={self.margin:.4f}")
        chk("residuals_below_spread", self.max_abs_residual < self.sd_between * 2,
            f"max|residual|={self.max_abs_residual:.4f} vs sd_between={self.sd_between:.4f}")
        ok = all(c["ok"] for c in checks)
        return {"ok": ok, "findings_sha": self.sha, "dataset_sha": self.meta.get("sha256"),
                "checks": checks}


def _shape_label(skew: float) -> str:
    a = abs(skew)
    if a >= 0.27: return "strongly lottery-like"
    if a >= 0.18: return "tilted"
    if a >= 0.10: return "mildly tilted"
    return "near-balanced"


def p_fav_from_odds_hda(odds_hda):
    """Cheap de-vig (normalised inverse-odds) → (p_fav, o_fav) per match.
    corr≈1.0 with Shin's de-vig (skewlib.skewmeter.gauge_cheap)."""
    r = 1.0 / np.asarray(odds_hda, float)
    P = r / r.sum(axis=1, keepdims=True)
    pf = P.max(axis=1)
    return pf, 1.0 / pf
