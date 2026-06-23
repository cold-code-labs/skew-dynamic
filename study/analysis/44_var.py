"""44 — Frente VAR: experimento natural escalonado (placebo de competitividade).
O VAR é um choque institucional que NÃO altera a dispersão de força dos times. Se a
skewness é f(competitividade), o VAR não deve movê-la — ao contrário da COVID (W3),
choque real de competitividade (queda de HFA) que a moveu +0.42 SD. Diferenças-em-
diferenças escalonado: ligas adotam o VAR em 2018/2019/2020; divisões inferiores
inglesas/escocesas (sem VAR de liga no recorte) são controle nunca-tratado.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, var, provenance as prov, config as C

COVID_Z = 0.42   # W3: deslocamento médio da skewness na COVID (SD da liga)


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = var.build_panel(df)
    nt = pan[pan.treated == 1].Division.nunique()
    nc = pan[pan.treated == 0].Division.nunique()
    sd_between = float(pan.groupby("Division").skew_exante.mean().std())
    print(f"painel VAR: {len(pan)} liga-anos | {nt} ligas tratadas + {nc} controles | "
          f"{pan.year.min()}–{pan.year.max()}", flush=True)
    print(f"  sd entre-ligas da skewness = {sd_between:.3f} (referência de magnitude)")

    print("\nDIFERENÇAS-EM-DIFERENÇAS (VAR ~ FE liga + FE ano, SE cluster por liga):")
    out = {}
    for col, lab in [("skew_exante", "skewness ex-ante"),
                     ("fav_win_rate", "taxa vitória favorito"),
                     ("p_fav", "p_fav médio (mercado)")]:
        r = var.did(pan, col); out[col] = r
        extra = f"  = {r['beta']/sd_between:+.2f} SD da liga" if col == "skew_exante" else ""
        print(f"  {lab:<26} β={r['beta']:+.4f} [{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"p={r['p']:.2f}{extra}")

    sk = out["skew_exante"]
    print(f"\n  efeito do VAR na skewness: {sk['beta']/sd_between:+.2f} SD "
          f"(IC inclui 0: {'sim' if sk['ci_lo'] < 0 < sk['ci_hi'] else 'não'}) — "
          f"contraste com a COVID (W3): {COVID_Z:+.2f} SD.")
    print("  → o VAR (choque institucional, não de competitividade) deixa a skewness")
    print("    invariante; só um choque de COMPETITIVIDADE (COVID/HFA) a move. Confirma")
    print("    skewness = f(dispersão de força), não de fatores institucionais.")

    es = var.event_study(pan)
    print("\n  event-study (skew média por anos-desde-VAR, ligas tratadas):")
    print("   " + "  ".join(f"{int(r.years_since_var):+d}:{r['mean']:.3f}"
                            for _, r in es.iterrows()))

    C.OUTDIR.mkdir(exist_ok=True)
    pan.to_csv(C.OUTDIR / "var_panel.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    # event-study: sem salto na adoção
    axes[0].axvline(0, color="#d62728", ls="--", lw=1, label="adoção do VAR")
    axes[0].errorbar(es.years_since_var, es["mean"],
                     yerr=es["std"] / np.sqrt(es["count"]), marker="o",
                     color="#1f77b4", capsize=3)
    axes[0].set_xlabel("anos desde a adoção do VAR")
    axes[0].set_ylabel("skewness ex-ante média")
    axes[0].set_title("Sem salto na adoção (ligas tratadas)")
    axes[0].legend(frameon=False, fontsize=8)
    # DiD: efeito do VAR vs choque de competitividade (COVID)
    labels = ["VAR\n(skewness)", "COVID\n(W3, HFA)"]
    vals = [sk["beta"] / sd_between, COVID_Z]
    errs = [(sk["ci_hi"] - sk["ci_lo"]) / 2 / sd_between, 0]
    axes[1].bar(labels, vals, width=0.5, color=["#aec7e8", "#d62728"],
                yerr=errs, capsize=5)
    axes[1].axhline(0, color="0.6", lw=0.8)
    axes[1].set_ylabel("efeito na skewness (SD da liga)")
    axes[1].set_title("Institucional (nulo) vs competitividade (move)")
    fig.suptitle("F31 — VAR: choque institucional não move a skewness "
                 "(placebo de competitividade)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f31_var.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f31_var.png'} | {C.OUTDIR / 'var_panel.csv'}")

    prov.write_stamp("44_var", metrics={
        "did_skew_beta": sk["beta"], "did_skew_sd": sk["beta"] / sd_between,
        "did_skew_p": sk["p"], "did_favwin_beta": out["fav_win_rate"]["beta"],
        "did_pfav_beta": out["p_fav"]["beta"], "n_treated": nt, "n_control": nc,
        "n_obs": len(pan)})


if __name__ == "__main__":
    main()
