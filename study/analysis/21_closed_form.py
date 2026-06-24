"""21 — Forma fechada de S(σ_L) (Frente E1): endurece a derivação. O P3/bloco 15
traça a lei skewness=f(competitividade) por SIMULAÇÃO (Monte Carlo sobre a força
d). Aqui mostramos que essa esperança é um INTEGRAL gaussiano 1-D em d e o
avaliamos por QUADRATURA — determinístico, sem ruído de MC: a forma fechada de
    S(σ_L) = E[m₃(p_fav(d))] / E[σ²(p_fav(d))]^{3/2},   d ~ N(0, 2σ_L²).
Três entregas:
  (1) a quadratura reproduz o MC a ~1e-3 (o resíduo é só o ruído do MC) → a curva
      teórica vira exata e suave;
  (2) limite balanceado em FORMA FECHADA: S(σ_L→0) = (1−2p₀)/√(p₀(1−p₀)), com
      p₀ = Φ(h−c) (a identidade por jogo no favorito de equilíbrio), + a curvatura
      líder S₂; honesto sobre o raio de validade (p_fav(d) tem quinas onde o
      favorito troca → S é C^∞ mas NÃO analítica global, daí a forma fechada ser
      o integral, não uma série elementar);
  (3) a curva exata prevê a skewness das 38 ligas a partir do p_fav, sem ruído.
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
    print("Calibrando ordered-probit (h, c, σ) p/ taxas marginais pooled...", flush=True)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    h, c, sref = par["h"], par["c"], par["sigma_ref"]
    print(f"  h={h:.3f} c={c:.3f} σ_ref={sref:.3f}")

    # (1) quadratura vs MC ao longo da grade de σ_L --------------------------
    sig = np.linspace(0.03, 1.30, 40)
    pf_ex, sk_ex = model.curve_exact(h, c, sig)
    sk_mc = np.array([model.league_skew(s, h, c, n=400000, seed=7) for s in sig])
    sk_sm = model.smallsigma_skew(sig, h, c)
    err = np.abs(sk_mc - sk_ex)
    print("\n(1) QUADRATURA EXATA vs MONTE CARLO (a forma fechada reproduz o MC):")
    print(f"  max|MC−exato| = {err.max():.4f} @ σ={sig[err.argmax()]:.3f} "
          f"(ordem do ruído de MC com n=4e5) | médio {err.mean():.4f}")
    print("  → a curva teórica passa a ser exata e suave (sem reamostragem).")

    # (2) limite balanceado em forma fechada ---------------------------------
    cf = model.smallsigma_coeffs(h, c)
    from scipy.stats import norm
    p0_analytic = float(norm.cdf(h - c))     # favorito = mandante no equilíbrio
    S0_identity = (1 - 2 * p0_analytic) / np.sqrt(p0_analytic * (1 - p0_analytic))
    print("\n(2) LIMITE BALANCEADO (forma fechada, σ_L→0):")
    print(f"  p₀ = Φ(h−c) = {p0_analytic:.4f}  (favorito de equilíbrio)")
    print(f"  S₀ = (1−2p₀)/√(p₀(1−p₀)) = {S0_identity:+.4f}  ≡ identidade por jogo")
    print(f"  conferência: S₀ do solver = {cf['S0']:+.4f} | curva exata @σ→0 = "
          f"{model.league_skew_exact(1e-4, h, c):+.4f}")
    print(f"  curvatura líder S₂ = {cf['S2']:+.3f} (>0: a skew SOBE ao sair do "
          f"equilíbrio); válida p/ σ≲0.1 (ligas muito parelhas).")
    # pico exato da curva (caracterização do máximo de assimetria)
    sg = np.linspace(0.02, 1.30, 600)
    sk_fine = np.array([model.league_skew_exact(s, h, c) for s in sg])
    i = int(sk_fine.argmax())
    pf_star = model.mean_pfav_exact(sg[i], h, c)
    print(f"  pico exato: σ*={sg[i]:.3f}  S_max={sk_fine[i]:+.4f}  (p_fav*={pf_star:.3f}); "
          f"zero da skew em σ≈{sg[np.argmin(np.abs(sk_fine))]:.2f} (favorito forte).")

    # (3) prever as ligas pela curva exata (sem ruído) -----------------------
    order = np.argsort(pf_ex)
    pred = np.interp(obs_pf, pf_ex[order], sk_ex[order])
    r = float(np.corrcoef(pred, obs_sk)[0, 1])
    rmse = float(np.sqrt(np.mean((pred - obs_sk) ** 2)))
    print(f"\n(3) PREVISÃO DAS {len(lg)} LIGAS pela curva EXATA (forma fechada):")
    print(f"  corr(previsto, observado) = {r:+.3f} | RMSE = {rmse:.3f} "
          f"(sd entre ligas {obs_sk.std():.3f})")
    print("  → mesma lei do bloco 15, agora derivada do integral fechado, não do MC.")

    C.OUTDIR.mkdir(exist_ok=True)
    import pandas as pd
    pd.DataFrame({"sigma_L": sig, "p_fav_exact": pf_ex, "skew_exact": sk_ex,
                  "skew_mc": sk_mc, "skew_smallsigma": sk_sm}).to_csv(
        C.OUTDIR / "closed_form_curve.csv", index=False)
    print(f"\n  -> {C.OUTDIR / 'closed_form_curve.csv'}")

    # figura -----------------------------------------------------------------
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
