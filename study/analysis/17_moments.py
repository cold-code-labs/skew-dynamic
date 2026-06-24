"""17 — Multi-momento (Frente B): de "invariância de skew" para "invariância de
FORMA". Estende a decomposição de momentos da mistura para var/skew/kurtose/5ª-6ª
ordem e confronta CADA momento com a curva derivada do ordered-probit (como o P3
fez só p/ a skew). Se o modelo de força prevê var, skew E kurtose das 38 ligas a
partir do p_fav, a forma inteira da distribuição implícita é função única da
competitividade — não só o 3º momento.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, model, stats, config as C

MAXO = 6
MOMENTS = ["var", "skew", "exkurt"]   # ordens 2,3,4 — previstas pelo modelo


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    p, o = df.p_fav_dv.values, df.o_fav.values
    n = len(df)

    G = exante.pooled_moments(p, o, max_order=MAXO)
    print(f"N={n:,} | de-vig={C.DEVIG_METHOD}")
    print("\nGLOBAL — momentos padronizados da mistura implícita + fração MECÂNICA:")
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
    print("  fração within (mecânica / intra-jogo) por ordem — ≈1 ⇒ a forma INTEIRA")
    print("  é a imagem algébrica da distribuição de p, não do pooling entre jogos:")
    for k in range(2, MAXO + 1):
        print(f"    m{k}: within_frac = {G[f'within_frac_m{k}']:+.4f}")

    # --- por liga: momentos observados ---
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

    # --- previsto pelo ordered-probit (1ª ordem -> cada momento) ---
    print("\nCalibrando ordered-probit p/ taxas marginais pooled...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    print(f"  h={par['h']:.3f} c={par['c']:.3f} σ_ref={par['sigma_ref']:.3f}")
    sig = np.linspace(0.05, 1.3, 45)
    cpf, cmom = model.curve_moments(par["h"], par["c"], sig, max_order=4)
    order = np.argsort(cpf)
    print("\n  modelo prevê cada momento da liga a partir SÓ do mean p_fav:")
    print(f"  {'momento':8s} {'corr(prev,obs)':>15s} {'RMSE':>8s} {'sd entre ligas':>15s}")
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

    # --- figura: previsto×observado p/ skew e kurtose ---
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, m, lab in [(axes[0], "skew", "skewness (m₃)"),
                       (axes[1], "exkurt", "excesso de kurtose (m₄)")]:
        ax.plot(cpf[order], cmom[m][order], color="0.5", lw=2,
                label="ordered-probit (derivado)")
        ax.scatter(lg.p_fav_dv, lg[m], s=20, color="#1f77b4", zorder=3,
                   label="ligas (empírico)")
        r = float(np.corrcoef(pred[m], lg[m].values)[0, 1])
        ax.set_xlabel("mean $p_{fav}$ da liga"); ax.set_ylabel(lab)
        ax.set_title(f"{lab} — r={r:+.2f}"); ax.legend(frameon=False, fontsize=8)
    fig.suptitle("F6 — Invariância de FORMA: cada momento na curva teórica", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f6_moments.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f6_moments.png'}")


if __name__ == "__main__":
    main()
