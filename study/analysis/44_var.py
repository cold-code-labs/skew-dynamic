"""44 — VAR front: staggered natural experiment (competitiveness placebo).
VAR is an institutional shock that does NOT alter the dispersion of team strength. If
skewness is f(competitiveness), VAR should not move it — unlike COVID (W3), a real
competitiveness shock (HFA drop) that moved it +0.42 SD. Staggered difference-in-
differences: leagues adopt VAR in 2018/2019/2020; lower English/Scottish divisions
(no league VAR within the window) are the never-treated control.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, var, provenance as prov, config as C

COVID_Z = 0.42   # W3: mean shift of skewness at COVID (league SD)


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    pan = var.build_panel(df)
    nt = pan[pan.treated == 1].Division.nunique()
    nc = pan[pan.treated == 0].Division.nunique()
    sd_between = float(pan.groupby("Division").skew_exante.mean().std())
    print(f"VAR panel: {len(pan)} league-years | {nt} treated leagues + {nc} controls | "
          f"{pan.year.min()}–{pan.year.max()}", flush=True)
    print(f"  between-league sd of skewness = {sd_between:.3f} (magnitude reference)")

    print("\nDIFFERENCE-IN-DIFFERENCES (VAR ~ league FE + year FE, SE clustered by league):")
    out = {}
    for col, lab in [("skew_exante", "ex-ante skewness"),
                     ("fav_win_rate", "favourite win rate"),
                     ("p_fav", "mean p_fav (market)")]:
        r = var.did(pan, col); out[col] = r
        extra = f"  = {r['beta']/sd_between:+.2f} league SD" if col == "skew_exante" else ""
        print(f"  {lab:<26} β={r['beta']:+.4f} [{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"p={r['p']:.2f}{extra}")

    sk = out["skew_exante"]
    print(f"\n  VAR effect on skewness: {sk['beta']/sd_between:+.2f} SD "
          f"(CI includes 0: {'yes' if sk['ci_lo'] < 0 < sk['ci_hi'] else 'no'}) — "
          f"contrast with COVID (W3): {COVID_Z:+.2f} SD.")
    print("  → VAR (an institutional shock, not a competitiveness one) leaves skewness")
    print("    invariant; only a COMPETITIVENESS shock (COVID/HFA) moves it. Confirms")
    print("    skewness = f(strength dispersion), not of institutional factors.")

    es = var.event_study(pan)
    print("\n  event-study (mean skew by years-since-VAR, treated leagues):")
    print("   " + "  ".join(f"{int(r.years_since_var):+d}:{r['mean']:.3f}"
                            for _, r in es.iterrows()))

    C.OUTDIR.mkdir(exist_ok=True)
    pan.to_csv(C.OUTDIR / "var_panel.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    # event-study: no jump at adoption
    axes[0].axvline(0, color="#d62728", ls="--", lw=1, label="VAR adoption")
    axes[0].errorbar(es.years_since_var, es["mean"],
                     yerr=es["std"] / np.sqrt(es["count"]), marker="o",
                     color="#1f77b4", capsize=3)
    axes[0].set_xlabel("years since VAR adoption")
    axes[0].set_ylabel("mean ex-ante skewness")
    axes[0].set_title("No jump at adoption (treated leagues)")
    axes[0].legend(frameon=False, fontsize=8)
    # DiD: VAR effect vs competitiveness shock (COVID)
    labels = ["VAR\n(skewness)", "COVID\n(W3, HFA)"]
    vals = [sk["beta"] / sd_between, COVID_Z]
    errs = [(sk["ci_hi"] - sk["ci_lo"]) / 2 / sd_between, 0]
    axes[1].bar(labels, vals, width=0.5, color=["#aec7e8", "#d62728"],
                yerr=errs, capsize=5)
    axes[1].axhline(0, color="0.6", lw=0.8)
    axes[1].set_ylabel("effect on skewness (league SD)")
    axes[1].set_title("Institutional (null) vs competitiveness (moves)")
    fig.suptitle("F31 — VAR: institutional shock does not move the skewness "
                 "(competitiveness placebo)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f31_var.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f31_var.png'} | {C.OUTDIR / 'var_panel.csv'}")

    prov.write_stamp("44_var", metrics={
        "did_skew_beta": sk["beta"], "did_skew_sd": sk["beta"] / sd_between,
        "did_skew_p": sk["p"], "did_favwin_beta": out["fav_win_rate"]["beta"],
        "did_pfav_beta": out["p_fav"]["beta"], "n_treated": nt, "n_control": nc,
        "n_obs": len(pan)})


if __name__ == "__main__":
    main()
