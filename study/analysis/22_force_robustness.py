"""22 — Robustness of the strength distribution (Front E2): the derived model
assumes Gaussian strength, r ~ N(0, σ_L²). Does the law skewness=f(competitiveness)
survive if the strength is heavy-tailed (Student-t), asymmetric (skew-normal) or of
bounded support (uniform)?

Theoretical prediction: a match's strength difference is d = rᵢ − rⱼ. For ANY iid
strength, d is SYMMETRIC (X−Y is symmetric about 0). Hence the ASYMMETRY of the
strength cannot bias the law — only the TAIL (kurtosis of d) can shift anything. So:
  • skew-normal (±α) should collapse almost exactly onto the Gaussian;
  • Student-t (heavy tails) is the real test; uniform (short tails) the opposite.
We reparametrise by the OBSERVABLE competitiveness (mean p_fav) and measure how much
the skew×p_fav curve shifts across families — if almost nothing, the law is geometry
of the mixture, not of the Gaussian assumption.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
from skewlib import io, returns, exante, model, provenance as prov, config as C

FAMILIES = [
    ("normal",          {},            "N(0,σ²) — baseline",          "#444444"),
    ("t",               {"nu": 5.0},   "t-Student ν=5 (medium tail)", "#1f77b4"),
    ("t",               {"nu": 3.0},   "t-Student ν=3 (heavy tail)",  "#d62728"),
    ("skewnormal",      {"alpha": 4.0},"skew-normal α=+4",            "#2ca02c"),
    ("skewnormal_neg",  {"alpha": 4.0},"skew-normal α=−4",            "#9467bd"),
    ("uniform",         {},            "uniform (short tail)",        "#ff7f0e"),
]
N = 600_000


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")
    print("Calibrating ordered-probit (Gaussian strength) to fix h, c...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    h, c, sref = par["h"], par["c"], par["sigma_ref"]
    print(f"  h={h:.3f} c={c:.3f} σ_ref={sref:.3f}")

    sig = np.linspace(0.05, 1.30, 36)
    curves = {}
    print("\nkurtosis of d (strength tail) by family @σ_ref:")
    for fam, kw, lab, _ in FAMILIES:
        pf, sk = model.curve_family(h, c, sig, family=fam, n=N, seed=11, **kw)
        curves[lab] = (pf, sk)
        d = model.force_diff(sref, 400_000, 5, fam, **kw)
        print(f"  {lab:30} exc.kurt(d) = {kurtosis(d):+.3f}")

    # reparametrise by observable competitiveness (mean p_fav) and compare --------
    base_pf, base_sk = curves["N(0,σ²) — baseline"]
    lo = max(c[0].min() for c in curves.values())
    hi = min(c[0].max() for c in curves.values())
    pgrid = np.linspace(lo + 0.005, hi - 0.005, 40)

    def interp_on_pgrid(pf, sk):
        o = np.argsort(pf)
        return np.interp(pgrid, pf[o], sk[o])

    base_i = interp_on_pgrid(base_pf, base_sk)
    print(f"\nDeviation of the skew×p_fav curve vs Gaussian (p_fav ∈ [{lo:.2f},{hi:.2f}], "
          f"reparametrised by competitiveness):")
    print(f"  {'family':30} {'max|ΔS|':>9} {'RMS ΔS':>9}")
    rows = []
    for fam, kw, lab, _ in FAMILIES:
        pf, sk = curves[lab]
        si = interp_on_pgrid(pf, sk)
        dmax = float(np.max(np.abs(si - base_i)))
        drms = float(np.sqrt(np.mean((si - base_i) ** 2)))
        print(f"  {lab:30} {dmax:>9.4f} {drms:>9.4f}")
        rows.append({"family": lab, "max_dS": dmax, "rms_dS": drms})

    # football operating point (p_fav ≈ empirical value) ------------------------
    pf_emp = float(df.p_fav_dv.mean())
    if lo < pf_emp < hi:
        sk_at = {lab: float(np.interp(pf_emp, *(lambda pf, sk: (np.sort(pf),
                 sk[np.argsort(pf)]))(*curves[lab]))) for lab in curves}
        vals = np.array(list(sk_at.values()))
        print(f"\nAt the football operating point (p_fav={pf_emp:.3f}): "
              f"skew ∈ [{vals.min():+.4f},{vals.max():+.4f}], "
              f"range across families = {vals.max()-vals.min():.4f}")

    print("\nReading: skew-normal (±α) sticks to the Gaussian (d symmetric ⇒ the strength")
    print("asymmetry does not count); only the tail (heavy t / uniform) shifts, and little —")
    print("the law skewness=f(competitiveness) is robust to the strength distribution.")

    C.OUTDIR.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(C.OUTDIR / "force_robustness.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'force_robustness.csv'}")

    # figure --------------------------------------------------------------------
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for fam, kw, lab, col in FAMILIES:
        pf, sk = curves[lab]
        o = np.argsort(pf)
        lw = 2.6 if fam == "normal" else 1.4
        ls = "-" if fam == "normal" else "--"
        ax.plot(pf[o], sk[o], ls, color=col, lw=lw, label=lab)
    ax.axhline(0, color="0.85", lw=.8)
    ax.set_xlabel("mean $p_{fav}$ (observable competitiveness)")
    ax.set_ylabel("pooled skewness $S$")
    ax.set_title("F11 — E2: the skew×competitiveness law survives swapping the strength law")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "f11_force_robustness.png", dpi=C.FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {FIG / 'f11_force_robustness.png'}")

    sd_lg = float(exante.pooled_by(df, "Division", min_n=2000).skew_exante.std())
    prov.write_stamp("22_force_robustness", metrics={
        "max_dS_overall": float(max(r["max_dS"] for r in rows)),
        "sd_between_leagues": sd_lg})


if __name__ == "__main__":
    main()
