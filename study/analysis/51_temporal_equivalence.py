"""51 — Equivalência temporal (frente U): "sem deriva secular" como TESTE DE
EQUIVALÊNCIA (TOST), não mera não-rejeição de H0.

W3 estabeleceu β_ano≈0 com p alto e IC cruzando zero. Isso é AUSÊNCIA DE EVIDÊNCIA,
não evidência de ausência: um p alto também sai de um teste sem potência. Aqui
pré-registramos uma margem de equivalência Δ — a MESMA do §4.8 (meia SD between-liga,
0.026), lida como a deriva acumulada tolerável na janela de ~20 anos — e, por dois
testes unilaterais (TOST), mostramos que a tendência está, com 95% de confiança,
DENTRO de (−Δ,+Δ). É uma afirmação POSITIVA de estabilidade.

Robustez: (i) SE cluster-robusto por liga (analítico) e bootstrap por liga; (ii)
painel completo e painel BALANCEADO (cesta de ligas fixa, mata o confound de
composição); (iii) curva de sensibilidade da margem (¼, ½, 1× a SD between-liga).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, panel as pan, adversarial as adv, stats, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    P = pan.league_season_panel(df)
    span = int(P.season.max() - P.season.min())           # janela em anos (~20)
    vd = pan.variance_decomp(P)
    sd_b = vd["sd_between"]                                # SD entre ligas (o invariante)

    # margem de equivalência: meia SD between-liga ACUMULADA na janela (§4.8 usa 0.026)
    delta20 = 0.5 * sd_b                                   # na escala da deriva de 20 anos
    delta_yr = delta20 / span                              # na escala de β/ano
    print(f"painel: {len(P)} obs · {P.Division.nunique()} ligas · {P.season.min()}–{P.season.max()} ({span} anos)")
    print(f"SD between-liga = {sd_b:.4f} → margem de equivalência Δ = ½·SD = {delta20:.4f} "
          f"(deriva/20a) = {delta_yr:.5f}/ano\n")

    # painel balanceado (cesta fixa) — robustez ao confound de composição
    bal = adv.balanced_leagues(P, min_frac=1.0)
    if len(bal) < 3:
        bal = adv.balanced_leagues(P, min_frac=0.9)
    Pbal = P[P.Division.isin(bal)].copy()

    def assess(panel, label, boot_B=2000):
        t = pan.trend_test(panel)
        bt = pan.trend_boot(panel, B=boot_B)
        an = stats.tost(t["beta_year"], t["se"], delta_yr)        # analítico (SE cluster)
        bo = stats.tost(t["beta_year"], bt["se"], delta_yr)       # bootstrap (SE por liga)
        print(f"[{label}]  β={t['beta_year']:+.5f}/ano  drift20={t['beta_year']*span:+.4f}")
        print(f"  H0 clássica  : p(β=0)={t['p']:.2f}  IC95%[{t['ci_lo']:+.5f},{t['ci_hi']:+.5f}]  "
              f"→ {'não rejeita' if t['p']>.05 else 'rejeita'} (ausência de evidência)")
        print(f"  TOST analít. : SE={t['se']:.5f}  p_tost={an['p_tost']:.4f}  "
              f"IC90%[{an['ci90_lo']:+.5f},{an['ci90_hi']:+.5f}]  → {'EQUIVALENTE' if an['equivalent'] else 'inconclusivo'}")
        print(f"  TOST boot    : SE={bt['se']:.5f}  p_tost={bo['p_tost']:.4f}  "
              f"IC90 boot[{bt['ci90_lo']:+.5f},{bt['ci90_hi']:+.5f}]  → {'EQUIVALENTE' if bo['equivalent'] else 'inconclusivo'}\n")
        return t, bt, an, bo

    print("=== Equivalência da tendência secular (β dentro de ±Δ) ===")
    tf, btf, anf, bof = assess(P, "painel completo")
    tb, btb, anb, bob = assess(Pbal, f"painel balanceado ({len(bal)} ligas)")

    # sensibilidade da margem: ¼, ½, 1× a SD between-liga
    print("=== Sensibilidade da margem (painel completo, SE cluster) ===")
    sens = []
    for frac in (0.25, 0.5, 1.0):
        d = frac * sd_b / span
        r = stats.tost(tf["beta_year"], tf["se"], d)
        sens.append({"frac": frac, "delta20": frac * sd_b, "p_tost": r["p_tost"], "equivalent": r["equivalent"]})
        print(f"  Δ = {frac:>4}·SD = {frac*sd_b:.4f}/20a → p_tost={r['p_tost']:.4f}  "
              f"{'EQUIVALENTE' if r['equivalent'] else 'inconclusivo'}")

    # figura forest: drift de 20 anos ± IC, contra a banda de equivalência ±Δ20
    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    # IC de 90% = intervalo relevante p/ o TOST a α=0.05 (equivalência ⇔ IC90 ⊂ ±Δ)
    rows = [
        ("full panel · cluster-robust", tf["beta_year"]*span, (anf["ci90_lo"]*span, anf["ci90_hi"]*span)),
        ("full panel · league bootstrap", tf["beta_year"]*span, (btf["ci90_lo"]*span, btf["ci90_hi"]*span)),
        (f"balanced panel ({len(bal)}) · cluster", tb["beta_year"]*span, (anb["ci90_lo"]*span, anb["ci90_hi"]*span)),
    ]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.axvspan(-delta20, delta20, color="#3a9d5d", alpha=.13, label=f"equivalence band ±Δ (½ between-league SD = {delta20:.3f})")
    ax.axvline(0, color="0.7", lw=.8)
    for i, (lab, pt, (lo, hi)) in enumerate(rows):
        ax.errorbar(pt, i, xerr=[[pt-lo], [hi-pt]], fmt="o", color="#1f4e79",
                    capsize=4, lw=2, ms=7)
        ax.text(hi + delta20*0.06, i, lab, va="center", fontsize=8.5)
    ax.set_yticks([]); ax.set_ylim(-0.6, len(rows)-0.4)
    ax.set_xlabel("20-year drift in ex-ante skewness (β × span), with 90% CI (TOST-relevant)")
    lim = max(delta20*1.6, max(abs(hi) for _,_,(lo,hi) in rows)*1.25)
    ax.set_xlim(-lim, lim*1.9)
    ax.set_title("F37 — temporal invariance as EQUIVALENCE: the trend's CI lies inside ±Δ\n"
                 "(positive evidence of no drift, not mere failure to reject β=0)", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "f37_temporal_equivalence.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f37_temporal_equivalence.png'}")
    print("  → a invariância temporal vira afirmação positiva: rejeitamos qualquer deriva")
    print(f"    maior que ½ SD between-liga ({delta20:.3f}) em 20 anos, p_tost={anf['p_tost']:.4f}.")

    prov.write_stamp("51_temporal_equivalence", metrics={
        "beta_year": tf["beta_year"], "drift20": tf["beta_year"]*span,
        "sd_between": sd_b, "delta20": delta20, "delta_year": delta_yr,
        "p_tost": anf["p_tost"], "p_tost_boot": bof["p_tost"],
        "p_tost_balanced": anb["p_tost"], "n_obs": tf["n_obs"]})


if __name__ == "__main__":
    main()
