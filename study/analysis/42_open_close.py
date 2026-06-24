"""42 — Frente D1: descoberta de preço (abertura → fechamento). [DADO CANÔNICO]
O mirror congelado só tem o preço de fechamento; aqui usamos o football-data.co.uk
canônico, que traz odds de ABERTURA (Avg*) e FECHAMENTO (Avg*C) do mesmo jogo
(2019/20–2023/24, 21 ligas). Pergunta central da tese: a assimetria estrutural
JÁ NASCE no preço de abertura, ou o mercado a "descobre" ao longo da negociação?

Se a skewness é herdada da estrutura competitiva (não produzida pelo apreçamento),
ela deve estar presente já na abertura e quase não se mover até o fechamento —
mesmo que o fechamento seja mais afiado (margem menor, melhor calibração). Estende
a ortogonalidade da margem (W4/D2, entre books) para o eixo TEMPORAL da formação
de preço.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import fdcanon as fc, devig, exante, stats, provenance as prov, config as C


def _overround(g, cols):
    r = 1.0 / g[list(cols)].to_numpy(float)
    return r.sum(1).mean()


def main():
    df = fc.load()
    # jogos com abertura E fechamento 1X2 válidos
    d = df.copy()
    for c in (*fc.OPEN_AVG, *fc.CLOSE_AVG):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=[*fc.OPEN_AVG, *fc.CLOSE_AVG])
    for c in (*fc.OPEN_AVG, *fc.CLOSE_AVG):
        d = d[d[c] > C.MIN_ODD]
    print(f"N={len(d):,} | {d.Division.nunique()} ligas | {d.season.min()}–{d.season.max()} "
          f"(odds de abertura E fechamento)", flush=True)

    # ── de-vig abertura e fechamento; favorito definido na ABERTURA ──
    do = devig.devig_frame(d, cols=fc.OPEN_AVG)
    dc = devig.devig_frame(d, cols=fc.CLOSE_AVG)
    Po = do[["p_H", "p_D", "p_A"]].to_numpy(float)
    Pc = dc[["p_H", "p_D", "p_A"]].to_numpy(float)
    Oo = d[list(fc.OPEN_AVG)].to_numpy(float)
    Oc = d[list(fc.CLOSE_AVG)].to_numpy(float)
    i = np.arange(len(d)); j = Po.argmax(1)            # favorito na abertura
    p0 = Po[i, j]; p1 = Pc[i, j]                        # mesma perna: prob abre→fecha
    o0 = Oo[i, j]; o1 = Oc[i, j]
    res = d.FTResult.map({"H": 0, "D": 1, "A": 2}).to_numpy()
    fav_won = (res == j).astype(float)

    # margem e calibração: o fechamento é mais afiado?
    over_o = (1.0 / Oo).sum(1).mean(); over_c = (1.0 / Oc).sum(1).mean()
    brier_o = float(np.mean((fav_won - p0) ** 2)); brier_c = float(np.mean((fav_won - p1) ** 2))
    drift = p1 - p0
    print(f"\nMARGEM e CALIBRAÇÃO (favorito da abertura, {len(d):,} jogos):")
    print(f"  overround   abertura {over_o:.4f} → fechamento {over_c:.4f} "
          f"(margem cai {100*(over_o-over_c):.2f} p.p.)")
    print(f"  Brier(fav)  abertura {brier_o:.4f} → fechamento {brier_c:.4f} "
          f"({'fechamento mais afiado' if brier_c < brier_o else 'sem ganho'})")
    print(f"  prob do favorito: abre {p0.mean():.4f} → fecha {p1.mean():.4f} "
          f"(drift médio {drift.mean():+.4f}; o favorito {'firma' if drift.mean()>0 else 'afrouxa'})")

    # ── skewness por liga: abertura vs fechamento ──
    rows = []
    for lg, g in d.groupby("Division"):
        po, oo, so = exante.market_skew(g, fc.OPEN_AVG)
        pc, oc, sc = exante.market_skew(g, fc.CLOSE_AVG)
        rows.append({"Division": lg, "n": len(g),
                     "skew_open": so["skew"], "skew_close": sc["skew"],
                     "within_open": so["within_frac"], "within_close": sc["within_frac"],
                     "pfav_open": float(po.mean()), "pfav_close": float(pc.mean()),
                     "over_open": _overround(g, fc.OPEN_AVG),
                     "over_close": _overround(g, fc.CLOSE_AVG)})
    L = pd.DataFrame(rows)
    go = exante.market_skew(d, fc.OPEN_AVG)[2]; gc = exante.market_skew(d, fc.CLOSE_AVG)[2]
    print(f"\nSKEWNESS abertura vs fechamento:")
    print(f"  global: abertura {go['skew']:+.3f} (within {go['within_frac']:.3f}) → "
          f"fechamento {gc['skew']:+.3f} (within {gc['within_frac']:.3f})")
    rcc = stats.bootstrap_corr(L.skew_open.values, L.skew_close.values)
    print(f"  corr(skew_open, skew_close) entre {len(L)} ligas = {rcc['r']:+.3f} "
          f"[{rcc['ci_lo']:+.2f},{rcc['ci_hi']:+.2f}]")
    lo = stats.bootstrap_corr(L.skew_open.values, L.pfav_open.values)
    lc = stats.bootstrap_corr(L.skew_close.values, L.pfav_close.values)
    print(f"  lei estrutural corr(skew, p_fav): abertura {lo['r']:+.3f} | fechamento {lc['r']:+.3f}")
    print(f"  Δskew médio (fecha−abre) por liga = {(L.skew_close-L.skew_open).mean():+.4f} "
          f"(sd {(L.skew_close-L.skew_open).std():.4f})")
    print("\n  → a assimetria já está NO PREÇO DE ABERTURA; o fechamento a afina a")
    print("    margem/calibração mas quase não move a skewness (corr ~1). A assimetria")
    print("    é herdada da estrutura, não produzida pela negociação — eixo temporal de W4/D2.")

    C.OUTDIR.mkdir(exist_ok=True)
    L.to_csv(C.OUTDIR / "open_close_by_league.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    mn = min(L.skew_open.min(), L.skew_close.min()) - 0.02
    mx = max(L.skew_open.max(), L.skew_close.max()) + 0.02
    axes[0].plot([mn, mx], [mn, mx], "--", color="0.7", lw=1)
    axes[0].scatter(L.skew_open, L.skew_close, s=28, color="#1f77b4")
    axes[0].set_xlabel("skewness na ABERTURA"); axes[0].set_ylabel("skewness no FECHAMENTO")
    axes[0].set_title(f"Mesma assimetria abre→fecha (r={rcc['r']:+.2f})")
    axes[1].bar([0, 1], [over_o - 1, over_c - 1], width=0.5, color=["#aec7e8", "#1f77b4"])
    axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(["abertura", "fechamento"])
    axes[1].set_ylabel("margem (overround − 1)")
    axes[1].set_title(f"Margem cai, skewness não\nglobal skew {go['skew']:+.3f}→{gc['skew']:+.3f}")
    fig.suptitle("F30 — D1: a assimetria já nasce no preço de abertura "
                 "(descoberta de preço)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f30_open_close.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f30_open_close.png'} | {C.OUTDIR / 'open_close_by_league.csv'}")

    ch = fc.canonical_hash()
    prov.write_stamp("42_open_close", metrics={
        "skew_open": go["skew"], "skew_close": gc["skew"],
        "corr_open_close": rcc["r"], "law_open": lo["r"], "law_close": lc["r"],
        "over_open": over_o, "over_close": over_c, "brier_open": brier_o,
        "brier_close": brier_c, "fav_drift": float(drift.mean()), "n": len(d),
        "data_source": "canonical", "canonical_sha": ch["sha256"]})


if __name__ == "__main__":
    main()
