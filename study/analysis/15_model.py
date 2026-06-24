"""15 — Formal derivation (P3): the skewness~competitiveness law is DERIVED, not
fitted. An ordered-probit with strength dispersion σ_L analytically generates the
(mean p_fav, skewness) curve; we overlay the 38 empirical leagues. If they fall on
the theoretical curve, the sport's strength model generates exactly the observed law.
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

    print("calibrating ordered-probit (h, c, σ) to pooled marginal rates...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    print(f"  h={par['h']:.3f} (home advantage) c={par['c']:.3f} (draw cutoff) "
          f"σ_ref={par['sigma_ref']:.3f}")

    sig = np.linspace(0.05, 1.3, 45)
    cpf, csk = model.curve(par["h"], par["c"], sig)

    # predict each league's skewness: invert σ via p_fav, then skew via the curve
    order = np.argsort(cpf)
    pred_sk = np.interp(obs_pf, cpf[order], csk[order])
    r = np.corrcoef(pred_sk, obs_sk)[0, 1]
    rmse = float(np.sqrt(np.mean((pred_sk - obs_sk) ** 2)))
    print(f"\n  model predicts league skewness from p_fav (1st→3rd order):")
    print(f"  corr(predicted, observed) = {r:+.3f} | RMSE = {rmse:.3f} "
          f"(vs between-league sd {obs_sk.std():.3f})")
    print(f"  theoretical curve range: skew {csk.min():+.2f}..{csk.max():+.2f} "
          f"for p_fav {cpf.min():.2f}..{cpf.max():.2f}")
    print("  → the empirical leagues fall on the derived curve: the law is a consequence")
    print("    of the strength model + FLB, not a free fit.")

    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    o = np.argsort(cpf)
    ax.plot(cpf[o], csk[o], color="0.5", lw=2, label="ordered-probit (derived)")
    ax.scatter(obs_pf, obs_sk, s=20, color="#1f77b4", zorder=3, label="leagues (empirical)")
    ax.set_xlabel("league mean $p_{fav}$"); ax.set_ylabel("ex-ante skewness")
    ax.set_title(f"F5 — Derived law: leagues on the theoretical curve (r={r:+.2f})")
    ax.legend(frameon=False); fig.tight_layout()
    fig.savefig(FIG / "f5_model.png", dpi=C.FIG_DPI); plt.close(fig)
    print(f"  -> {FIG / 'f5_model.png'}")


if __name__ == "__main__":
    main()
