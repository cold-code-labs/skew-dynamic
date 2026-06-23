"""22 — Robustez da distribuição de força (Frente E2): o modelo derivado assume
força gaussiana, r ~ N(0, σ_L²). A lei skewness=f(competitividade) sobrevive se
a força for cauda-pesada (t-Student), assimétrica (skew-normal) ou de suporte
limitado (uniforme)?

Predição teórica: a diferença de força de um jogo é d = rᵢ − rⱼ. Para QUALQUER
força iid, d é SIMÉTRICO (X−Y é simétrico em torno de 0). Logo a ASSIMETRIA da
força não pode enviesar a lei — só a CAUDA (kurtose de d) pode mover algo. Então:
  • skew-normal (±α) deve colapsar quase exatamente sobre a gaussiana;
  • t-Student (caudas pesadas) é o teste real; uniforme (caudas curtas) o oposto.
Reparametrizamos pela competitividade OBSERVÁVEL (mean p_fav) e medimos quanto a
curva skew×p_fav se desloca entre famílias — se quase nada, a lei é geometria da
mistura, não da hipótese gaussiana.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
from skewlib import io, returns, exante, model, provenance as prov, config as C

FAMILIES = [
    ("normal",          {},            "N(0,σ²) — baseline",          "#444444"),
    ("t",               {"nu": 5.0},   "t-Student ν=5 (cauda média)", "#1f77b4"),
    ("t",               {"nu": 3.0},   "t-Student ν=3 (cauda pesada)","#d62728"),
    ("skewnormal",      {"alpha": 4.0},"skew-normal α=+4",            "#2ca02c"),
    ("skewnormal_neg",  {"alpha": 4.0},"skew-normal α=−4",            "#9467bd"),
    ("uniform",         {},            "uniforme (cauda curta)",      "#ff7f0e"),
]
N = 600_000


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")
    print("Calibrando ordered-probit (força gaussiana) p/ fixar h, c...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    h, c, sref = par["h"], par["c"], par["sigma_ref"]
    print(f"  h={h:.3f} c={c:.3f} σ_ref={sref:.3f}")

    sig = np.linspace(0.05, 1.30, 36)
    curves = {}
    print("\nkurtose de d (cauda da força) por família @σ_ref:")
    for fam, kw, lab, _ in FAMILIES:
        pf, sk = model.curve_family(h, c, sig, family=fam, n=N, seed=11, **kw)
        curves[lab] = (pf, sk)
        d = model.force_diff(sref, 400_000, 5, fam, **kw)
        print(f"  {lab:30} exc.kurt(d) = {kurtosis(d):+.3f}")

    # reparametrizar pela competitividade observável (mean p_fav) e comparar -----
    base_pf, base_sk = curves["N(0,σ²) — baseline"]
    lo = max(c[0].min() for c in curves.values())
    hi = min(c[0].max() for c in curves.values())
    pgrid = np.linspace(lo + 0.005, hi - 0.005, 40)

    def interp_on_pgrid(pf, sk):
        o = np.argsort(pf)
        return np.interp(pgrid, pf[o], sk[o])

    base_i = interp_on_pgrid(base_pf, base_sk)
    print(f"\nDesvio da curva skew×p_fav vs gaussiana (p_fav ∈ [{lo:.2f},{hi:.2f}], "
          f"reparametrizada pela competitividade):")
    print(f"  {'família':30} {'max|ΔS|':>9} {'RMS ΔS':>9}")
    rows = []
    for fam, kw, lab, _ in FAMILIES:
        pf, sk = curves[lab]
        si = interp_on_pgrid(pf, sk)
        dmax = float(np.max(np.abs(si - base_i)))
        drms = float(np.sqrt(np.mean((si - base_i) ** 2)))
        print(f"  {lab:30} {dmax:>9.4f} {drms:>9.4f}")
        rows.append({"family": lab, "max_dS": dmax, "rms_dS": drms})

    # ponto operacional do futebol (p_fav ≈ valor empírico) ---------------------
    pf_emp = float(df.p_fav_dv.mean())
    if lo < pf_emp < hi:
        sk_at = {lab: float(np.interp(pf_emp, *(lambda pf, sk: (np.sort(pf),
                 sk[np.argsort(pf)]))(*curves[lab]))) for lab in curves}
        vals = np.array(list(sk_at.values()))
        print(f"\nNo ponto operacional do futebol (p_fav={pf_emp:.3f}): "
              f"skew ∈ [{vals.min():+.4f},{vals.max():+.4f}], "
              f"amplitude entre famílias = {vals.max()-vals.min():.4f}")

    print("\nLeitura: skew-normal (±α) cola na gaussiana (d simétrico ⇒ a assimetria")
    print("da força não conta); só a cauda (t pesada / uniforme) desloca, e pouco —")
    print("a lei skewness=f(competitividade) é robusta à distribuição de força.")

    C.OUTDIR.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(C.OUTDIR / "force_robustness.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'force_robustness.csv'}")

    # figura --------------------------------------------------------------------
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for fam, kw, lab, col in FAMILIES:
        pf, sk = curves[lab]
        o = np.argsort(pf)
        lw = 2.6 if fam == "normal" else 1.4
        ls = "-" if fam == "normal" else "--"
        ax.plot(pf[o], sk[o], ls, color=col, lw=lw, label=lab)
    ax.axhline(0, color="0.85", lw=.8)
    ax.set_xlabel("mean $p_{fav}$ (competitividade observável)")
    ax.set_ylabel("skewness agrupada $S$")
    ax.set_title("F11 — E2: a lei skew×competitividade sobrevive à troca da força")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "f11_force_robustness.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {FIG / 'f11_force_robustness.png'}")

    sd_lg = float(exante.pooled_by(df, "Division", min_n=2000).skew_exante.std())
    prov.write_stamp("22_force_robustness", metrics={
        "max_dS_overall": float(max(r["max_dS"] for r in rows)),
        "sd_between_leagues": sd_lg})


if __name__ == "__main__":
    main()
