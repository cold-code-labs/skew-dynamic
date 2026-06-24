"""39 — Front M: realised tail risk of the strategies. The practical side: realised
moments, VaR/CVaR (left tail) and max drawdown of the cumulative P&L of
always-favourite vs always-underdog (unit stake, chronological order). Connects the
skewness structure to actual bankroll risk — the quant reading of the asymmetry.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, extras, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load())).sort_values("date")
    print(f"N={len(df):,} | unit stake, chronological order")

    strat = {"favorito": df.ret_fav.values, "azarão": df.ret_dog.values}
    print(f"\n{'strategy':10} {'mean':>8} {'std':>7} {'skew':>7} {'exkurt':>8} "
          f"{'CVaR5%':>8} {'maxDD':>9} {'final P&L':>10}")
    out = {}
    for name, r in strat.items():
        tm = extras.tail_metrics(r)
        dd = extras.max_drawdown(r)
        out[name] = {**tm, **dd}
        print(f"{name:10} {tm['mean']:>+8.4f} {tm['std']:>7.3f} {tm['skew']:>+7.3f} "
              f"{tm['exkurt']:>+8.2f} {tm['cvar5']:>+8.3f} {dd['max_drawdown']:>+9.1f} "
              f"{dd['final_pnl']:>+10.1f}")
    print("\n  → both bleed the vig (negative final P&L), but the underdog is the tail:")
    print("    much larger skew/kurtosis and a deeper drawdown (long runs of losses")
    print("    punctuated by rare big payouts) — the 'lottery' in real risk.")

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for name, col in [("favorito", "#1f77b4"), ("azarão", "#d62728")]:
        pnl = np.cumsum(strat[name])
        axes[0].plot(np.arange(len(pnl)), pnl, color=col, lw=1,
                     label={"favorito": "favourite", "azarão": "underdog"}[name])
    axes[0].axhline(0, color="0.7", lw=.8)
    axes[0].set_xlabel("bet no. (chronological)"); axes[0].set_ylabel("cumulative P&L (units)")
    axes[0].set_title("P&L curves (both bleed the vig)")
    axes[0].legend(frameon=False, fontsize=8)
    names = list(strat); skews = [out[n]["skew"] for n in names]
    dds = [out[n]["max_drawdown"] for n in names]
    x = np.arange(len(names))
    axes[1].bar(x - .2, skews, .4, color="#1f77b4", label="skew")
    axes[1].bar(x + .2, [d / 1000 for d in dds], .4, color="#d62728", label="maxDD (×10³)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([{"favorito": "favourite", "azarão": "underdog"}[n] for n in names])
    axes[1].axhline(0, color="0.7", lw=.8)
    axes[1].set_title("Underdog = more skew and deeper drawdown")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("F27 — M: realised tail risk of the strategies", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f27_tail_risk.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f27_tail_risk.png'}")

    prov.write_stamp("39_tail_risk", metrics={
        "skew_fav": out["favorito"]["skew"], "skew_dog": out["azarão"]["skew"],
        "maxdd_fav": out["favorito"]["max_drawdown"],
        "maxdd_dog": out["azarão"]["max_drawdown"]})


if __name__ == "__main__":
    main()
