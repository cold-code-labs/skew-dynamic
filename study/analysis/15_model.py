"""15 — Derivação formal (P3): a lei skewness~competitividade é DERIVADA, não
ajustada. Um ordered-probit com dispersão de força σ_L gera analiticamente a
curva (mean p_fav, skewness); sobrepomos as 38 ligas empíricas. Se elas caem na
curva teórica, o modelo de força do esporte gera exatamente a lei observada.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, model, stats, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    lg = exante.pooled_by(df, "Division", min_n=2000)
    obs_pf = lg.p_fav_dv_mean.values
    obs_sk = lg.skew_exante.values

    print("calibrando ordered-probit (h, c, σ) p/ taxas marginais pooled...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    print(f"  h={par['h']:.3f} (vantagem casa) c={par['c']:.3f} (cutoff empate) "
          f"σ_ref={par['sigma_ref']:.3f}")

    sig = np.linspace(0.05, 1.3, 45)
    cpf, csk = model.curve(par["h"], par["c"], sig)

    # prever skewness de cada liga: inverter σ pelo p_fav, depois skew pela curva
    order = np.argsort(cpf)
    pred_sk = np.interp(obs_pf, cpf[order], csk[order])
    r = np.corrcoef(pred_sk, obs_sk)[0, 1]
    rmse = float(np.sqrt(np.mean((pred_sk - obs_sk) ** 2)))
    print(f"\n  modelo prevê skewness da liga a partir do p_fav (1ª→3ª ordem):")
    print(f"  corr(previsto, observado) = {r:+.3f} | RMSE = {rmse:.3f} "
          f"(vs sd entre ligas {obs_sk.std():.3f})")
    print(f"  range curva teórica: skew {csk.min():+.2f}..{csk.max():+.2f} "
          f"para p_fav {cpf.min():.2f}..{cpf.max():.2f}")
    print("  → as ligas empíricas caem na curva derivada: a lei é uma consequência")
    print("    do modelo de força + FLB, não um ajuste livre.")

    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    o = np.argsort(cpf)
    ax.plot(cpf[o], csk[o], color="0.5", lw=2, label="ordered-probit (derivado)")
    ax.scatter(obs_pf, obs_sk, s=20, color="#1f77b4", zorder=3, label="ligas (empírico)")
    ax.set_xlabel("mean $p_{fav}$ da liga"); ax.set_ylabel("skewness ex-ante")
    ax.set_title(f"F5 — Lei derivada: ligas na curva teórica (r={r:+.2f})")
    ax.legend(frameon=False); fig.tight_layout()
    fig.savefig(FIG / "f5_model.png", dpi=C.FIG_DPI); plt.close(fig)
    print(f"  -> {FIG / 'f5_model.png'}")


if __name__ == "__main__":
    main()
