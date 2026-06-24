"""39 — Frente M: risco de cauda realizado das estratégias. Lado prático: momentos
realizados, VaR/CVaR (cauda esquerda) e max drawdown do P&L acumulado de
sempre-favorito vs sempre-azarão (aposta unitária, ordem cronológica). Conecta a
estrutura de skewness ao risco de banca de fato — a leitura quant da assimetria.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, extras, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load())).sort_values("date")
    print(f"N={len(df):,} | aposta unitária, ordem cronológica")

    strat = {"favorito": df.ret_fav.values, "azarão": df.ret_dog.values}
    print(f"\n{'estratégia':10} {'média':>8} {'desv':>7} {'skew':>7} {'exkurt':>8} "
          f"{'CVaR5%':>8} {'maxDD':>9} {'P&L final':>10}")
    out = {}
    for name, r in strat.items():
        tm = extras.tail_metrics(r)
        dd = extras.max_drawdown(r)
        out[name] = {**tm, **dd}
        print(f"{name:10} {tm['mean']:>+8.4f} {tm['std']:>7.3f} {tm['skew']:>+7.3f} "
              f"{tm['exkurt']:>+8.2f} {tm['cvar5']:>+8.3f} {dd['max_drawdown']:>+9.1f} "
              f"{dd['final_pnl']:>+10.1f}")
    print("\n  → ambas sangram a margem (P&L final negativo), mas o azarão é a cauda:")
    print("    skew/kurtose muito maiores e drawdown mais fundo (sequências longas de")
    print("    perdas pontuadas por raros prêmios grandes) — a 'lotérica' em risco real.")

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for name, col in [("favorito", "#1f77b4"), ("azarão", "#d62728")]:
        pnl = np.cumsum(strat[name])
        axes[0].plot(np.arange(len(pnl)), pnl, color=col, lw=1, label=name)
    axes[0].axhline(0, color="0.7", lw=.8)
    axes[0].set_xlabel("aposta nº (cronológico)"); axes[0].set_ylabel("P&L acumulado (unidades)")
    axes[0].set_title("Curvas de P&L (ambas sangram a vig)")
    axes[0].legend(frameon=False, fontsize=8)
    names = list(strat); skews = [out[n]["skew"] for n in names]
    dds = [out[n]["max_drawdown"] for n in names]
    x = np.arange(len(names))
    axes[1].bar(x - .2, skews, .4, color="#1f77b4", label="skew")
    axes[1].bar(x + .2, [d / 1000 for d in dds], .4, color="#d62728", label="maxDD (×10³)")
    axes[1].set_xticks(x); axes[1].set_xticklabels(names)
    axes[1].axhline(0, color="0.7", lw=.8)
    axes[1].set_title("Azarão = mais skew e drawdown mais fundo")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F27 — M: risco de cauda realizado das estratégias", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f27_tail_risk.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f27_tail_risk.png'}")

    prov.write_stamp("39_tail_risk", metrics={
        "skew_fav": out["favorito"]["skew"], "skew_dog": out["azarão"]["skew"],
        "maxdd_fav": out["favorito"]["max_drawdown"],
        "maxdd_dog": out["azarão"]["max_drawdown"]})


if __name__ == "__main__":
    main()
