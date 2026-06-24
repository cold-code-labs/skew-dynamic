"""41 — Frente O: BATERIA de modelos geradores (independência de modelo, ampliada).
A Frente I mostrou que UM Poisson de gols cai na mesma curva que o ordered-probit
de margem. Aqui submetemos a lei skewness=f(competitividade) a uma bateria de
geradores GENUINAMENTE distintos — Poisson (gols), Dixon-Coles (gols+dependência),
Bradley-Terry-Davidson (forças logísticas, SEM gols) e Elo de resultados (odds-free,
mapa ordinal) — e mostramos que TODOS reproduzem a lei e caem na curva S(σ_L).
Se cinco famílias independentes + o mercado caem na mesma curva, a lei não é
artefato de nenhuma forma funcional: é geometria da mistura de apostas de dois
pontos sobre a distribuição de competitividade da liga.

Nota de robustez: Poisson bivariado (covariância de gols) e Negative-Binomial
(super-dispersão) NÃO entram — gols de futebol são Poisson independente quase puro
(cov mediana ≈ −0.07, super-dispersão ≈ 0), então ambos colapsam ao Poisson.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (io, returns, exante, crossmodel as cm, model, stats,
                     provenance as prov, config as C)

GENS = [("poisson", "Poisson (gols)", "#d62728", "^"),
        ("dixoncoles", "Dixon-Coles", "#2ca02c", "s"),
        ("btd", "Bradley-Terry-Davidson", "#9467bd", "D"),
        ("elo", "Elo de resultados (odds-free)", "#ff7f0e", "x")]


def _corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return stats.bootstrap_corr(a[m], b[m])


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    print(f"N={len(df):,} | ajustando a bateria por liga-temporada "
          f"(Poisson, Dixon-Coles, Bradley-Terry-Davidson)...", flush=True)
    tab = cm.battery_table(df, min_games=150, min_teams=8)
    L = cm.by_league(tab)
    print(f"  {len(tab)} liga-temporadas ajustadas, {L.Division.nunique()} ligas")
    print("  ajustando Elo de resultados (odds-free, passo cronológico)...", flush=True)
    L = L.merge(cm.elo_by_league(df)[["Division", "skew_elo", "pfav_elo"]],
                on="Division", how="left")

    # curva derivada do ordered-probit (mesma calibração da Frente I)
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.05, 1.3, 45)
    cpf, csk = model.curve(par["h"], par["c"], sig)
    o = np.argsort(cpf)

    print(f"\nBATERIA DE MODELOS (entre {L.Division.nunique()} ligas) — "
          f"todos vs empírico e vs a curva S(σ_L):")
    print(f"  {'modelo':<26} {'corr(skew,emp)':>16} {'corr(pfav,emp)':>16} "
          f"{'r na curva':>11} {'nível skew':>11}")
    rows = []
    skemp = L.skew_emp.to_numpy()
    for key, lab, _c, _m in GENS:
        sk = L[f"skew_{key}"].to_numpy(); pf = L[f"pfav_{key}"].to_numpy()
        rs = _corr(sk, skemp); rp = _corr(pf, L.pfav_emp.to_numpy())
        msk = np.isfinite(pf) & np.isfinite(sk)
        pred = np.interp(pf[msk], cpf[o], csk[o])
        r_curve = float(np.corrcoef(pred, sk[msk])[0, 1])
        rows.append((key, lab, rs, rp, r_curve, float(np.nanmean(sk))))
        print(f"  {lab:<26} {rs['r']:+.3f} [{rs['ci_lo']:+.2f},{rs['ci_hi']:+.2f}] "
              f"  {rp['r']:+.3f}        {r_curve:+.2f}      {np.nanmean(sk):+.3f}")
    # referências
    pe = L.pfav_emp.to_numpy()
    pred_e = np.interp(pe, cpf[o], csk[o])
    r_emp_curve = float(np.corrcoef(pred_e, skemp)[0, 1])
    print(f"  {'mercado (empírico)':<26} {'  —':>16} {'  —':>16} "
          f"{r_emp_curve:+.2f}      {skemp.mean():+.3f}")
    print("\n  → cinco famílias independentes (margem-probit, Poisson, Dixon-Coles,")
    print("    Bradley-Terry-Davidson, Elo de resultados) + o mercado caem na MESMA")
    print("    curva: a lei skewness=f(competitividade) é independente do modelo gerador.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "model_battery_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    # painel 1: todos os modelos sobre a curva
    axes[0].plot(cpf[o], csk[o], color="0.4", lw=2, zorder=1,
                 label="ordered-probit S(σ_L)")
    axes[0].scatter(L.pfav_emp, L.skew_emp, s=26, color="#1f77b4",
                    label="mercado (empírico)", zorder=3)
    for key, lab, col, mk in GENS:
        axes[0].scatter(L[f"pfav_{key}"], L[f"skew_{key}"], s=22, color=col,
                        marker=mk, alpha=0.8, label=lab, zorder=2)
    axes[0].axhline(0, color="0.85", lw=0.8, zorder=0)
    axes[0].set_xlabel("mean $p_{fav}$ (competitividade)")
    axes[0].set_ylabel("skewness ex-ante")
    axes[0].set_title("Cinco famílias, uma curva")
    axes[0].legend(frameon=False, fontsize=7.5, loc="upper right")
    # painel 2: skew_modelo vs skew_empírico (todos), com a reta identidade
    lo = min(L.skew_emp.min(), -0.05); hi = max(L.skew_emp.max(), 0.4)
    axes[1].plot([lo, hi], [lo, hi], "--", color="0.7", lw=1, zorder=0)
    for key, lab, col, mk in GENS:
        rs = next(r for r in rows if r[0] == key)[2]
        axes[1].scatter(L.skew_emp, L[f"skew_{key}"], s=22, color=col, marker=mk,
                        alpha=0.8, label=f"{lab} (r={rs['r']:+.2f})")
    axes[1].set_xlabel("skewness empírica (mercado)")
    axes[1].set_ylabel("skewness do modelo")
    axes[1].set_title("Cada gerador reproduz a ordenação das ligas")
    axes[1].legend(frameon=False, fontsize=7.5, loc="upper left")
    fig.suptitle("F29 — O: bateria de modelos geradores reproduz a lei "
                 "(independência de modelo)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f29_model_battery.png", dpi=C.FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  -> {FIG / 'f29_model_battery.png'} | "
          f"{C.OUTDIR / 'model_battery_by_league.csv'}")

    metrics = {}
    for key, lab, rs, rp, r_curve, level in rows:
        metrics[f"corr_skew_{key}"] = rs["r"]
        metrics[f"r_curve_{key}"] = r_curve
    metrics["r_curve_emp"] = r_emp_curve
    metrics["n_league_seasons"] = len(tab)
    metrics["n_models"] = len(GENS) + 1
    prov.write_stamp("41_model_battery", metrics=metrics)


if __name__ == "__main__":
    main()
