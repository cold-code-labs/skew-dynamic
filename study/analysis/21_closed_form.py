"""21 — Closed form of S(σ_L) (Front E1): hardens the derivation. P3/block 15
traces the law skewness=f(competitiveness) by SIMULATION (Monte Carlo over the
strength d). Here we show that this expectation is a 1-D Gaussian INTEGRAL in d and
evaluate it by QUADRATURE — deterministic, without MC noise: the closed form of
    S(σ_L) = E[m₃(p_fav(d))] / E[σ²(p_fav(d))]^{3/2},   d ~ N(0, 2σ_L²).
Three deliverables:
  (1) the quadrature reproduces the MC to ~1e-3 (the residual is only the MC noise)
      → the theoretical curve becomes exact and smooth;
  (2) balanced limit in CLOSED FORM: S(σ_L→0) = (1−2p₀)/√(p₀(1−p₀)), with
      p₀ = Φ(h−c) (the per-match identity at the equilibrium favourite), + the
      leading curvature S₂; honest about the radius of validity (p_fav(d) has kinks
      where the favourite switches → S is C^∞ but NOT globally analytic, hence the
      closed form is the integral, not an elementary series);
  (3) the exact curve predicts the skewness of the 38 leagues from p_fav, noise-free.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, model, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    lg = exante.pooled_by(df, "Division", min_n=2000)
    obs_pf, obs_sk = lg.p_fav_dv_mean.values, lg.skew_exante.values

    print(f"N={len(df):,} | de-vig={C.DEVIG_METHOD}")
    print("Calibrating ordered-probit (h, c, σ) for pooled marginal rates...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    h, c, sref = par["h"], par["c"], par["sigma_ref"]
    print(f"  h={h:.3f} c={c:.3f} σ_ref={sref:.3f}")

    # (1) quadrature vs MC along the σ_L grid ---------------------------------
    sig = np.linspace(0.03, 1.30, 40)
    pf_ex, sk_ex = model.curve_exact(h, c, sig)
    sk_mc = np.array([model.league_skew(s, h, c, n=400000, seed=7) for s in sig])
    sk_sm = model.smallsigma_skew(sig, h, c)
    err = np.abs(sk_mc - sk_ex)
    print("\n(1) EXACT QUADRATURE vs MONTE CARLO (the closed form reproduces the MC):")
    print(f"  max|MC−exact| = {err.max():.4f} @ σ={sig[err.argmax()]:.3f} "
          f"(order of MC noise with n=4e5) | mean {err.mean():.4f}")
    print("  → the theoretical curve becomes exact and smooth (no resampling).")

    # (2) balanced limit in closed form ---------------------------------------
    cf = model.smallsigma_coeffs(h, c)
    from scipy.stats import norm
    p0_analytic = float(norm.cdf(h - c))     # favourite = home side at equilibrium
    S0_identity = (1 - 2 * p0_analytic) / np.sqrt(p0_analytic * (1 - p0_analytic))
    print("\n(2) BALANCED LIMIT (closed form, σ_L→0):")
    print(f"  p₀ = Φ(h−c) = {p0_analytic:.4f}  (equilibrium favourite)")
    print(f"  S₀ = (1−2p₀)/√(p₀(1−p₀)) = {S0_identity:+.4f}  ≡ per-match identity")
    print(f"  check: S₀ from solver = {cf['S0']:+.4f} | exact curve @σ→0 = "
          f"{model.league_skew_exact(1e-4, h, c):+.4f}")
    print(f"  leading curvature S₂ = {cf['S2']:+.3f} (>0: skew RISES on leaving "
          f"equilibrium); valid for σ≲0.1 (very even leagues).")
    # exact peak of the curve (characterisation of the maximum asymmetry)
    sg = np.linspace(0.02, 1.30, 600)
    sk_fine = np.array([model.league_skew_exact(s, h, c) for s in sg])
    i = int(sk_fine.argmax())
    pf_star = model.mean_pfav_exact(sg[i], h, c)
    print(f"  exact peak: σ*={sg[i]:.3f}  S_max={sk_fine[i]:+.4f}  (p_fav*={pf_star:.3f}); "
          f"skew zero at σ≈{sg[np.argmin(np.abs(sk_fine))]:.2f} (strong favourite).")

    # (3) predict the leagues by the exact curve (noise-free) ------------------
    order = np.argsort(pf_ex)
    pred = np.interp(obs_pf, pf_ex[order], sk_ex[order])
    r = float(np.corrcoef(pred, obs_sk)[0, 1])
    rmse = float(np.sqrt(np.mean((pred - obs_sk) ** 2)))
    print(f"\n(3) PREDICTION OF THE {len(lg)} LEAGUES by the EXACT curve (closed form):")
    print(f"  corr(predicted, observed) = {r:+.3f} | RMSE = {rmse:.3f} "
          f"(sd across leagues {obs_sk.std():.3f})")
    print("  → same law as block 15, now derived from the closed integral, not the MC.")

    C.OUTDIR.mkdir(exist_ok=True)
    import pandas as pd
    pd.DataFrame({"sigma_L": sig, "p_fav_exact": pf_ex, "skew_exact": sk_ex,
                  "skew_mc": sk_mc, "skew_smallsigma": sk_sm}).to_csv(
        C.OUTDIR / "closed_form_curve.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'closed_form_curve.csv'}")

    # figure -----------------------------------------------------------------
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    o = np.argsort(sig)
    axes[0].scatter(sig, sk_mc, s=14, color="#1f77b4", alpha=.7, zorder=3,
                    label="Monte Carlo (n=4·10⁵)")
    axes[0].plot(sig[o], sk_ex[o], color="#d62728", lw=2,
                 label="exact quadrature (closed form)")
    m = sig <= 0.45
    axes[0].plot(sig[m], sk_sm[m], "--", color="0.4", lw=1.5,
                 label="analytic expansion S₀+S₂σ² (near-balance)")
    axes[0].axhline(0, color="0.8", lw=.8)
    axes[0].set_xlabel("strength dispersion $\\sigma_L$ (competitiveness)")
    axes[0].set_ylabel("pooled skewness $S(\\sigma_L)$")
    axes[0].set_title(f"Closed form vs MC (max|Δ|={err.max():.3f})")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].plot(pf_ex[order], sk_ex[order], color="#d62728", lw=2,
                 label="exact curve (closed form)")
    axes[1].scatter(obs_pf, obs_sk, s=20, color="#1f77b4", zorder=3,
                    label="leagues (empirical)")
    axes[1].set_xlabel("league mean $p_{fav}$")
    axes[1].set_ylabel("ex-ante skewness")
    axes[1].set_title(f"Leagues on the closed-form curve (r={r:+.2f})")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F10 — E1: closed-form S(σ_L) (Gaussian integral by quadrature)",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f10_closed_form.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"  -> {FIG / 'f10_closed_form.png'}")

    prov.write_stamp("21_closed_form", metrics={
        "max_mc_err": float(err.max()), "p0": p0_analytic, "S0": float(S0_identity),
        "sigma_peak": float(sg[i]), "league_r": r})


if __name__ == "__main__":
    main()
