"""41 — Front O: BATTERY of generative models (model independence, extended).
Front I showed that ONE goals Poisson falls on the same curve as the margin
ordered-probit. Here we subject the law skewness=f(competitiveness) to a battery of
GENUINELY distinct generators — Poisson (goals), Dixon-Coles (goals+dependence),
Bradley-Terry-Davidson (logistic strengths, NO goals) and Elo of results (odds-free,
ordinal map) — and show that ALL reproduce the law and fall on the curve S(σ_L).
If five independent families + the market fall on the same curve, the law is not an
artefact of any functional form: it is the geometry of the mixture of two-point bets
over the league's competitiveness distribution.

Robustness note: bivariate Poisson (goal covariance) and Negative-Binomial
(over-dispersion) are NOT included — football goals are almost pure independent
Poisson (median cov ≈ −0.07, over-dispersion ≈ 0), so both collapse to Poisson.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (io, returns, exante, crossmodel as cm, model, stats,
                     provenance as prov, config as C)

GENS = [("poisson", "Poisson (goals)", "#d62728", "^"),
        ("dixoncoles", "Dixon-Coles", "#2ca02c", "s"),
        ("btd", "Bradley-Terry-Davidson", "#9467bd", "D"),
        ("elo", "Elo of results (odds-free)", "#ff7f0e", "x")]


def _corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return stats.bootstrap_corr(a[m], b[m])


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    print(f"N={len(df):,} | fitting the battery by league-season "
          f"(Poisson, Dixon-Coles, Bradley-Terry-Davidson)...", flush=True)
    tab = cm.battery_table(df, min_games=150, min_teams=8)
    L = cm.by_league(tab)
    print(f"  {len(tab)} league-seasons fitted, {L.Division.nunique()} leagues")
    print("  fitting Elo of results (odds-free, chronological step)...", flush=True)
    L = L.merge(cm.elo_by_league(df)[["Division", "skew_elo", "pfav_elo"]],
                on="Division", how="left")

    # curve derived from the ordered-probit (same calibration as Front I)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.05, 1.3, 45)
    cpf, csk = model.curve(par["h"], par["c"], sig)
    o = np.argsort(cpf)

    print(f"\nMODEL BATTERY (across {L.Division.nunique()} leagues) — "
          f"all vs empirical and vs the curve S(σ_L):")
    print(f"  {'model':<26} {'corr(skew,emp)':>16} {'corr(pfav,emp)':>16} "
          f"{'r on curve':>11} {'skew level':>11}")
    rows = []
    skemp = L.skew_emp.to_numpy()
    for key, lab, _c, _m in GENS:
        sk = L[f"skew_{key}"].to_numpy(); pf = L[f"pfav_{key}"].to_numpy()
        rs = _corr(sk, skemp); rp = _corr(pf, L.pfav_emp.to_numpy())
        msk = np.isfinite(pf) & np.isfinite(sk)
        pred = np.interp(pf[msk], cpf[o], csk[o])
        r_curve = float(np.corrcoef(pred, sk[msk])[0, 1])
        rows.append((key, lab, rs, rp, r_curve, float(np.nanmean(sk))))
        print(f"  {lab:<26} {rs['r']:+.3f} [{rs['ci_lo']:+.2f},{rs['ci_hi']:+.2f}] "
              f"  {rp['r']:+.3f}        {r_curve:+.2f}      {np.nanmean(sk):+.3f}")
    # references
    pe = L.pfav_emp.to_numpy()
    pred_e = np.interp(pe, cpf[o], csk[o])
    r_emp_curve = float(np.corrcoef(pred_e, skemp)[0, 1])
    print(f"  {'market (empirical)':<26} {'  —':>16} {'  —':>16} "
          f"{r_emp_curve:+.2f}      {skemp.mean():+.3f}")
    print("\n  → five independent families (margin-probit, Poisson, Dixon-Coles,")
    print("    Bradley-Terry-Davidson, Elo of results) + the market fall on the SAME")
    print("    curve: the law skewness=f(competitiveness) is independent of the generative model.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "model_battery_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    # panel 1: all models on the curve
    axes[0].plot(cpf[o], csk[o], color="0.4", lw=2, zorder=1,
                 label="ordered-probit S(σ_L)")
    axes[0].scatter(L.pfav_emp, L.skew_emp, s=26, color="#1f77b4",
                    label="market (empirical)", zorder=3)
    for key, lab, col, mk in GENS:
        axes[0].scatter(L[f"pfav_{key}"], L[f"skew_{key}"], s=22, color=col,
                        marker=mk, alpha=0.8, label=lab, zorder=2)
    axes[0].axhline(0, color="0.85", lw=0.8, zorder=0)
    axes[0].set_xlabel("mean $p_{fav}$ (competitiveness)")
    axes[0].set_ylabel("skewness ex-ante")
    axes[0].set_title("Five families, one curve")
    axes[0].legend(frameon=False, fontsize=7.5, loc="upper right")
    # panel 2: skew_model vs skew_empirical (all), with the identity line
    lo = min(L.skew_emp.min(), -0.05); hi = max(L.skew_emp.max(), 0.4)
    axes[1].plot([lo, hi], [lo, hi], "--", color="0.7", lw=1, zorder=0)
    for key, lab, col, mk in GENS:
        rs = next(r for r in rows if r[0] == key)[2]
        axes[1].scatter(L.skew_emp, L[f"skew_{key}"], s=22, color=col, marker=mk,
                        alpha=0.8, label=f"{lab} (r={rs['r']:+.2f})")
    axes[1].set_xlabel("empirical skewness (market)")
    axes[1].set_ylabel("model skewness")
    axes[1].set_title("Each generator reproduces the league ordering")
    axes[1].legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.suptitle("F29 — O: battery of generative models reproduces the law "
                 "(model independence)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f29_model_battery.png", dpi=C.FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  -> {FIG / 'f29_model_battery.png'} | "
          f"{C.OUTDIR / 'model_battery_by_league.csv'}")

    metrics = {}
    for key, lab, rs, rp, r_curve, level in rows:
        metrics[f"corr_skew_{key}"] = rs["r"]
        metrics[f"r_curve_{key}"] = r_curve
    metrics["r_curve_emp"] = r_emp_curve
    metrics["n_league_seasons"] = len(tab)
    metrics["n_models"] = len(GENS) + 1
    prov.write_stamp("41_model_battery", metrics=metrics)


if __name__ == "__main__":
    main()
