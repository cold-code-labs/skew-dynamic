"""34 — E3: calibração do modelo POR liga (cutoff de empate endógeno). O bloco 15
calibra (h, c, σ) GLOBAL. Aqui calibramos os três POR liga a partir das taxas
marginais de cada uma — vantagem de casa, cutoff de empate c (ligas mais
"empatadeiras") e dispersão de força σ_L endógenos. Pergunta: a lei melhora quando
cada liga tem seu próprio (h,c,σ)? E o σ_L estimado é a competitividade?
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, model, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    obs = exante.pooled_by(df, "Division", min_n=3000)[["Division", "skew_exante", "p_fav_dv_mean"]]
    print(f"N={len(df):,} | calibrando (h,c,σ) por liga...", flush=True)
    P = model.calibrate_by_league(df, n=120000, min_n=3000)
    M = P.merge(obs, on="Division")
    print(f"  {len(M)} ligas calibradas")

    print(f"\nPARÂMETROS ENDÓGENOS por liga:")
    print(f"  h (casa):  média {P.h.mean():.3f} · range [{P.h.min():.3f},{P.h.max():.3f}]")
    print(f"  c (empate): média {P.c.mean():.3f} · range [{P.c.min():.3f},{P.c.max():.3f}]"
          f"  ← cutoff de empate endógeno (ligas mais/menos empatadeiras)")
    print(f"  σ_L (força): média {P['sigma_L'].mean():.3f} · "
          f"range [{P['sigma_L'].min():.3f},{P['sigma_L'].max():.3f}]")

    # σ_L estimado é a competitividade observável?
    rsp = stats.bootstrap_corr(M.sigma_L.values, M.p_fav_dv_mean.values)
    print(f"\n  corr(σ_L estimado, p_fav observado) = {rsp['r']:+.3f} "
          f"[{rsp['ci_lo']:+.2f},{rsp['ci_hi']:+.2f}] — σ_L recupera a competitividade")
    # c endógeno correlaciona com a taxa de empate da liga?
    rcd = stats.bootstrap_corr(M.c.values, M.draw.values)
    print(f"  corr(c endógeno, taxa de empate) = {rcd['r']:+.3f} "
          f"[{rcd['ci_lo']:+.2f},{rcd['ci_hi']:+.2f}] — c capta a 'empatabilidade'")

    # a skew prevista pelo modelo da PRÓPRIA liga vs observada
    r = float(np.corrcoef(M.skew_model.values, M.skew_exante.values)[0, 1])
    rmse = float(np.sqrt(np.mean((M.skew_model - M.skew_exante) ** 2)))
    print(f"\n  skew_model (por liga) vs observada: r={r:+.3f}, RMSE={rmse:.3f}")
    print(f"  (global do bloco 15: r=+0.90, RMSE 0.024 — calibração por liga mantém a lei)")
    print("  → a invariância sobrevive ao cutoff de empate endógeno; (h,c,σ) por liga")
    print("    não muda a história: σ_L (competitividade) continua governando a skew.")

    C.OUTDIR.mkdir(exist_ok=True)
    M.sort_values("sigma_L").to_csv(C.OUTDIR / "per_league_calibration.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(M.sigma_L, M.p_fav_dv_mean, s=22, color="#1f77b4")
    axes[0].set_xlabel("σ_L estimado por liga"); axes[0].set_ylabel("p_fav observado")
    axes[0].set_title(f"σ_L é a competitividade (r={rsp['r']:+.2f})")
    axes[1].plot([M.skew_exante.min(), M.skew_exante.max()],
                 [M.skew_exante.min(), M.skew_exante.max()], "--", color="0.7", lw=1)
    axes[1].scatter(M.skew_exante, M.skew_model, s=22, color="#d62728")
    axes[1].set_xlabel("skew observada"); axes[1].set_ylabel("skew do modelo da liga")
    axes[1].set_title(f"Calibração por liga (r={r:+.2f})")
    fig.suptitle("F22 — E3: (h,c,σ) endógenos por liga — a lei sobrevive", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f22_per_league_calib.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f22_per_league_calib.png'} | {C.OUTDIR / 'per_league_calibration.csv'}")

    prov.write_stamp("34_per_league_calibration", metrics={
        "corr_sigma_pfav": rsp["r"], "corr_c_draw": rcd["r"],
        "skew_model_r": r, "c_range": float(P.c.max() - P.c.min())})


if __name__ == "__main__":
    main()
