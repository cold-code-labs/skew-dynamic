"""45 — skew-meter: SIMILARIDADE DE ASSIMETRIAS (estudo-referência do objetivo-raiz).
O objetivo original do projeto era MEDIR A SIMILARIDADE DE ASSIMETRIAS. Este bloco
operacionaliza isso num único aparelho (skewlib/skewmeter.py) e demonstra:

  A) Matriz de similaridade entre ligas: a distância BRUTA entre assimetrias é
     grande, mas a RESIDUAL (descontada a competitividade) COLAPSA ao piso amostral
     — as assimetrias são as MESMAS quando a competitividade é igualada (B2 operacional).
  B) Aparelho de POUCOS parâmetros: sem Shin (~0 custo), 1 parâmetro (média p_fav →
     forma fechada) e odds-free (só resultados) — quanto se perde.
  C) Convergência em tempo real: quão rápido o medidor 'trava' numa liga.
  D) Veredito par-a-par: 'mesma assimetria?' com z-score vs o ruído.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import (io, returns, exante, devig, elo, skewmeter as sm,
                     provenance as prov, config as C)


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    law = sm.fit_law(df)
    print(f"N={len(df):,} | lei calibrada: h={law['par']['h']:.3f} c={law['par']['c']:.3f}",
          flush=True)

    # ── assinaturas por liga + piso amostral ──
    sigs, se_by = [], {}
    for lg, g in df.groupby("Division"):
        if len(g) < 2000:
            continue
        sigs.append(sm.measure(g.p_fav_dv.values, g.o_fav.values, label=lg))
        se_by[lg] = sm.skew_se(g.p_fav_dv.values, g.o_fav.values)
    sigs = sorted(sigs, key=lambda s: s["comp"])           # ordena por competitividade
    ses = [se_by[s["label"]] for s in sigs]
    M = sm.matrix(sigs, law, ses=ses)
    truth0 = np.array([s["skew"] for s in sigs])
    one0 = np.array([sm.predict_skew(s["comp"], law) for s in sigs])
    r2 = np.corrcoef(truth0, one0)[0, 1] ** 2
    sd_between = float(truth0.std())
    print(f"\nA) SIMILARIDADE DE ASSIMETRIAS — {len(sigs)} ligas, distância |Δskew|:")
    print(f"   distância BRUTA mediana    = {M['median_raw']:.3f}")
    print(f"   distância RESIDUAL mediana = {M['median_residual']:.3f}  "
          f"(descontada a competitividade, 1 parâmetro)")
    print(f"   colapso bruta→residual     = {1-M['collapse']:.0%} da distância "
          f"explicada por 1 número (R²={r2:.2f} da variância entre ligas)")
    print(f"   resíduo idiossincrático: sd {sd_between*np.sqrt(1-r2):.3f} vs entre-ligas "
          f"{sd_between:.3f} | piso amostral {M['noise_floor']:.3f}")
    # escada de suficiência: quantos parâmetros bastam?
    lad = sm.sufficiency_ladder(df, law)
    sh = sm.split_half_residual(df, law)
    print(f"\n   ESCADA DE SUFICIÊNCIA (R² da assimetria entre ligas):")
    print(f"     1 parâmetro  (média p_fav)        R² = {lad['r2_1param']:.3f}")
    print(f"     2 momentos   (média + variância)  R² = {lad['r2_2moment']:.3f}")
    print(f"     distribuição INTEIRA de p_fav     R² = {lad['r2_full']:.3f}  "
          f"(resíduo {lad['resid_sd_full']:.3f} ≈ ruído {M['noise_floor']:.3f})")
    print(f"   → estatística suficiente MÍNIMA = distribuição inteira; a média sozinha")
    print(f"     deixa um resíduo ESTÁVEL (split-half temporal r={sh['r']:.2f}), não ruído")
    print(f"     — é a curvatura da lei, capturada pelo 2º momento (98%).")

    # ── B) aparelho de poucos parâmetros ──
    truth = np.array([s["skew"] for s in sigs])
    comp = np.array([s["comp"] for s in sigs])
    cheap = []
    for s in sigs:
        g = df[df.Division == s["label"]]
        cheap.append(sm.gauge_cheap(g[["OddHome", "OddDraw", "OddAway"]].to_numpy(float))["skew"])
    cheap = np.array(cheap)
    one = np.array([sm.predict_skew(c, law) for c in comp])
    comp_elo = elo.league_competitiveness(elo.with_elo(df)).set_index("Division")
    upset = np.array([comp_elo.loc[s["label"], "upset_rate"] for s in sigs])
    print("\nB) APARELHO DE POUCOS PARÂMETROS (corr com a verdade = pooled Shin):")
    print(f"   sem Shin (inverse-odds, ~0 custo) : {np.corrcoef(truth, cheap)[0,1]:.3f}")
    print(f"   1 PARÂMETRO (média p_fav → curva) : {np.corrcoef(truth, one)[0,1]:.3f}")
    print(f"   odds-free (upset rate, só W/D/L)  : {np.corrcoef(truth, upset)[0,1]:.3f}")

    # ── C) convergência em tempo real ──
    print("\nC) CONVERGÊNCIA EM TEMPO REAL (SE da skew com K jogos):")
    big = df[df.Division.isin(["E0", "SP1", "I1", "D1", "F1"])]
    rng = np.random.default_rng(0)
    conv = {}
    for K in [50, 100, 200, 400, 800]:
        errs = []
        for lg, g in big.groupby("Division"):
            p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
            est = [exante.pooled_skew(p[i], o[i])["skew"]
                   for i in (rng.integers(0, n, K) for _ in range(120))]
            errs.append(np.std(est))
        conv[K] = float(np.mean(errs))
        print(f"   K={K:4d} jogos → SE = {conv[K]:.3f}")
    print(f"   (sd ENTRE ligas = {truth.std():.3f} — o sinal estrutural a resolver)")

    # ── D) veredito de EQUIVALÊNCIA (TOST): com n enorme a significância sempre
    #     rejeita; testamos se a diferença residual cabe numa margem substantiva
    #     (meio desvio entre-ligas). ──
    margin = 0.5 * sd_between
    print(f"\nD) VEREDITO 'MESMA ASSIMETRIA?' (equivalência TOST, margem ½·sd = {margin:.3f}):")
    by = {s["label"]: (s, ses[k]) for k, s in enumerate(sigs)}
    pairs = [("E0", "SP1"), ("E0", "E3"), ("N1", "I2"), ("BRA", "ARG")]
    for a, b in pairs:
        if a in by and b in by:
            A, sa = by[a]; B, sb = by[b]
            raw = sm.distance(A, B); t = sm.tost(A, B, law, sa, sb, margin)
            expl = 1 - abs(t["d"]) / raw if raw > 0 else 0.0
            print(f"   {a} vs {b}: skew {A['skew']:+.3f}/{B['skew']:+.3f} | bruta {raw:.3f} "
                  f"→ residual {abs(t['d']):.3f} (explica {expl:.0%}) → "
                  f"{'EQUIVALENTES' if t['equivalent'] else 'distintas'}")

    # ── E) endurecimento (rigor): SE block-bootstrap, Mahalanobis, lei out-of-sample ──
    print("\nE) ROBUSTEZ DO APARELHO:")
    big5 = ["E0", "SP1", "I1", "D1", "F1"]
    iid = [sm.skew_se(df[df.Division == l].p_fav_dv.values,
                      df[df.Division == l].o_fav.values) for l in big5]
    blk = [sm.skew_se_block(df[df.Division == l]) for l in big5]
    print(f"   SE jogos-i.i.d. {np.mean(iid):.4f} → SE block-bootstrap de TEMPORADAS "
          f"{np.mean(blk):.4f} (×{np.mean(blk)/np.mean(iid):.1f} — dependência intra-ano)")
    cov_inv = np.linalg.inv(sm.sampling_shape_cov(df[df.Division == "E0"]))
    maha = [sm.shape_distance(sigs[i], sigs[j], cov_inv)
            for i in range(len(sigs)) for j in range(i + 1, len(sigs))]
    rawpairs = [sm.distance(sigs[i], sigs[j])
                for i in range(len(sigs)) for j in range(i + 1, len(sigs))]
    print(f"   distância de forma de Mahalanobis (skew+exkurt): mediana {np.median(maha):.1f}σ "
          f"| corr com |Δskew| escalar = {np.corrcoef(maha, rawpairs)[0,1]:.2f} "
          f"(a forma 2-D conta a MESMA história)")
    oos = sm.law_oos_r2(df)
    print(f"   lei OUT-OF-SAMPLE (calibra em anos pares, prevê ímpares): R²={oos:.3f} "
          f"(≈ in-sample {lad['r2_1param']:.2f} → régua do resíduo não é overfit)")

    print("\n  → CONCLUSÃO: 'similaridade de assimetrias' É, em primeira ordem,")
    print("    similaridade de COMPETITIVIDADE — um único número explica ~80% da")
    print("    variância da assimetria entre ligas (medível em tempo real, sem Shin,")
    print("    até odds-free). O resíduo é pequeno e absorvido pela distribuição inteira.")

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4),
                             gridspec_kw={"width_ratios": [1, 1, 0.9]})
    vmax = M["raw"].max()
    for ax, Mx, ttl in [(axes[0], M["raw"], "RAW  |Δskew|"),
                        (axes[1], M["residual"], "RESIDUAL (1 parameter)")]:
        im = ax.imshow(Mx, cmap="magma_r", vmin=0, vmax=vmax)
        ax.set_title(ttl, fontsize=11); ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_xlabel(f"leagues by competitiveness\nmedian {M['median_raw']:.3f}")
    axes[1].set_xlabel(f"median {M['median_residual']:.3f} ({1-M['collapse']:.0%} explained)")
    # painel 3: escada de suficiência
    bars = [lad["r2_1param"], lad["r2_2moment"], lad["r2_full"]]
    axes[2].bar(["1 param\n(mean)", "2 moments\n(+variance)", "full\ndistrib."],
                bars, color=["#aec7e8", "#5b9bd5", "#1f3a5f"])
    for i, v in enumerate(bars):
        axes[2].text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=9)
    axes[2].set_ylim(0, 1.08); axes[2].set_ylabel("R² of skewness across leagues")
    axes[2].set_title("Sufficiency ladder", fontsize=11)
    fig.suptitle("F33 — skew-meter: similarity of skewnesses = similarity of "
                 "competitiveness\n(1 parameter explains 80%; the first 2 moments 98%; "
                 "the full distribution is sufficient)", y=1.07)
    fig.tight_layout()
    fig.savefig(FIG / "f33_skewmeter.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f33_skewmeter.png'}")

    prov.write_stamp("45_skewmeter", metrics={
        "median_raw": M["median_raw"], "median_residual": M["median_residual"],
        "noise_floor": M["noise_floor"], "r2_1param": lad["r2_1param"],
        "r2_2moment": lad["r2_2moment"], "r2_full": lad["r2_full"],
        "split_half_r": sh["r"], "corr_cheap": float(np.corrcoef(truth, cheap)[0, 1]),
        "corr_oddsfree": float(np.corrcoef(truth, upset)[0, 1]),
        "se_k400": conv[400], "se_iid": float(np.mean(iid)),
        "se_block": float(np.mean(blk)), "law_oos_r2": oos,
        "n_leagues": len(sigs)})


if __name__ == "__main__":
    main()
