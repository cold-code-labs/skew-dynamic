"""17 — Multi-moment (Front B): from "skew invariance" to "SHAPE invariance".
Extends the moment decomposition of the mixture to var/skew/kurtosis/5th-6th
order and confronts EACH moment with the ordered-probit derived curve (as P3
did only for skew). If the strength model predicts var, skew AND kurtosis of the
38 leagues from p_fav, the entire shape of the implied distribution is a single
function of competitiveness — not just the 3rd moment.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, model, stats, config as C

MAXO = 6
MOMENTS = ["var", "skew", "exkurt"]   # orders 2,3,4 — predicted by the model


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    p, o = df.p_fav_dv.values, df.o_fav.values
    n = len(df)

    G = exante.pooled_moments(p, o, max_order=MAXO)
    print(f"N={n:,} | de-vig={C.DEVIG_METHOD}")
    print("\nGLOBAL — standardised moments of the implied mixture + MECHANICAL fraction:")
    print(f"  var      = {G['var']:.4f}")
    se = stats.bootstrap_stat(
        lambda i: exante.pooled_moments(p[i], o[i], 3)["skew"], n, B=400)
    print(f"  skew     = {G['skew']:+.4f}  (boot SE {se['se']:.4f}, "
          f"IC95 [{se['ci_lo']:+.3f},{se['ci_hi']:+.3f}])")
    sek = stats.bootstrap_stat(
        lambda i: exante.pooled_moments(p[i], o[i], 4)["exkurt"], n, B=400)
    print(f"  exkurt   = {G['exkurt']:+.4f}  (boot SE {sek['se']:.4f}, "
          f"IC95 [{sek['ci_lo']:+.3f},{sek['ci_hi']:+.3f}])")
    print(f"  std5     = {G['std5']:+.4f} | std6 = {G['std6']:+.4f}")
    print("  within fraction (mechanical / intra-match) by order — ≈1 ⇒ the ENTIRE shape")
    print("  is the algebraic image of the distribution of p, not of pooling across matches:")
    for k in range(2, MAXO + 1):
        print(f"    m{k}: within_frac = {G[f'within_frac_m{k}']:+.4f}")

    # --- by league: observed moments ---
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < 2000:
            continue
        pm = exante.pooled_moments(g.p_fav_dv.values, g.o_fav.values, max_order=MAXO)
        rows.append({"Division": lg, "n": len(g),
                     "p_fav_dv": float(g.p_fav_dv.mean()),
                     **{m: pm[m] for m in MOMENTS + ["std5", "std6"]},
                     **{f"wf_m{k}": pm[f"within_frac_m{k}"] for k in range(2, MAXO + 1)}})
    lg = pd.DataFrame(rows).sort_values("p_fav_dv").reset_index(drop=True)

    # --- predicted by the ordered-probit (1st order -> each moment) ---
    print("\nCalibrating ordered-probit for pooled marginal rates...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    print(f"  h={par['h']:.3f} c={par['c']:.3f} σ_ref={par['sigma_ref']:.3f}")
    sig = np.linspace(0.05, 1.3, 45)
    cpf, cmom = model.curve_moments(par["h"], par["c"], sig, max_order=4)
    order = np.argsort(cpf)
    print("\n  model predicts each league moment from ONLY the mean p_fav:")
    print(f"  {'moment':8s} {'corr(pred,obs)':>15s} {'RMSE':>8s} {'sd across leagues':>15s}")
    pred = {}
    for m in MOMENTS:
        pm = np.interp(lg.p_fav_dv.values, cpf[order], cmom[m][order])
        pred[m] = pm
        r = float(np.corrcoef(pm, lg[m].values)[0, 1])
        rmse = float(np.sqrt(np.mean((pm - lg[m].values) ** 2)))
        lg[f"{m}_pred"] = pm
        print(f"  {m:8s} {r:>+15.3f} {rmse:>8.4f} {lg[m].std():>15.4f}")

    C.OUTDIR.mkdir(exist_ok=True)
    lg.to_csv(C.OUTDIR / "moments_by_league.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'moments_by_league.csv'}")

    # --- figure: predicted×observed for skew and kurtosis ---
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, m, lab in [(axes[0], "skew", "skewness (m₃)"),
                       (axes[1], "exkurt", "excess kurtosis (m₄)")]:
        ax.plot(cpf[order], cmom[m][order], color="0.5", lw=2,
                label="ordered-probit (derived)")
        ax.scatter(lg.p_fav_dv, lg[m], s=20, color="#1f77b4", zorder=3,
                   label="leagues (empirical)")
        r = float(np.corrcoef(pred[m], lg[m].values)[0, 1])
        ax.set_xlabel("league mean $p_{fav}$"); ax.set_ylabel(lab)
        ax.set_title(f"{lab} — r={r:+.2f}"); ax.legend(frameon=False, fontsize=8)
    fig.suptitle("F6 — SHAPE invariance: every moment on the theoretical curve", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f6_moments.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f6_moments.png'}")


if __name__ == "__main__":
    main()
