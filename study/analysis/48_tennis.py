"""48 — Frente S: VALIDADE EXTERNA (tênis). A lei skew=f(competitividade) e o
formato lotérico do azarão são propriedades do ESPORTE, não do futebol?

Usa a camada canônica (skewlib/canonical + adapters/tennis) — zero ciência nova —
sobre o snapshot congelado de tênis (ATP+WTA, tennis-data.co.uk; hash em
data/PROVENANCE-tennis.json). Compara, na MESMA curva, o futebol (38 ligas, de
findings.json) e o tênis (tiers ATP/WTA).

Achado: a assinatura reaparece num 2º esporte, com mercado de 2 resultados (sem
empate) e fonte de odds independente — favorito mais negativo onde o torneio é mais
desbalanceado; azarão lotérico (~+2.3, como o futebol). A invariância estrutural não
é um artefato do 1X2 nem do futebol.
"""
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import canonical, config as C, provenance as prov
from skewlib.adapters import tennis

TENNIS = C.DATA_PATH.parent / "tennis.csv"
PROV = C.DATA_PATH.parent / "PROVENANCE-tennis.json"
FINDINGS = __import__("pathlib").Path(__file__).resolve().parents[2] / "site" / "src" / "data" / "findings.json"


def _verify_hash():
    want = json.loads(PROV.read_text())["sha256"]
    h = hashlib.sha256()
    with open(TENNIS, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    got = h.hexdigest()
    assert got == want, f"tennis.csv mudou: {got[:12]} != snapshot {want[:12]}"
    print(f"snapshot OK — sha256 {got[:12]} == PROVENANCE-tennis.json", flush=True)


def main():
    _verify_hash()
    raw = pd.read_csv(TENNIS, low_memory=False)

    # assinatura global + calibração (o de-vig é confiável em tênis?)
    can = tennis.to_canonical(raw)
    canonical.validate(can)
    n = can.event_id.nunique()
    fav = canonical.select(can, "fav"); dog = canonical.select(can, "dog")
    sf = canonical.signature(fav, "fav"); sd = canonical.signature(dog, "dog")
    calib_p, calib_w = float(fav.p.mean()), float(fav.won.mean())
    print(f"\nTÊNIS — {n:,} partidas (ATP+WTA), mercado match_odds (2 resultados):")
    print(f"  favorito skew = {sf['skew']:+.3f} | azarão skew = {sd['skew']:+.3f}")
    print(f"  calibração: p_fav médio {calib_p:.3f} ≈ vitória real do favorito {calib_w:.3f}")

    # a lei por tier, por tour
    tiers = []
    law = {}
    for tour in ["ATP", "WTA"]:
        bt = canonical.bettype_by(tennis.to_canonical(raw[raw.tour == tour]),
                                  by="competition", kinds=("fav", "dog"), min_n=800).dropna()
        bt.insert(0, "tour", tour)
        tiers.append(bt)
        law[tour] = float(np.corrcoef(bt.skew_fav, bt.p_fav_mean)[0, 1])
        print(f"  lei {tour}: corr(skew_fav, p_fav) por tier = {law[tour]:+.2f} ({len(bt)} tiers)")
    tiers = pd.concat(tiers, ignore_index=True)

    # futebol (findings.json) p/ a sobreposição
    fb = json.loads(FINDINGS.read_text())["bettype"]["leagues"]
    fb = pd.DataFrame(fb)

    C.OUTDIR.mkdir(exist_ok=True)
    tiers.to_csv(C.OUTDIR / "tennis_by_tier.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for a, fcol, tcol, ttl in [(ax[0], "fav", "skew_fav", "favourite bet"),
                               (ax[1], "dog", "skew_dog", "underdog bet")]:
        a.scatter(fb.p_fav, fb[fcol], s=26, c="#4a78b5", alpha=.7, label="football leagues (38)")
        a.scatter(tiers.p_fav_mean, tiers[tcol], s=60, marker="D", c="#d9822b",
                  edgecolor="#7a4a10", label="tennis tiers (ATP+WTA)")
        a.axhline(0, color="0.85", lw=.8)
        a.set_xlabel("competitiveness (mean favourite probability)")
        a.set_ylabel("ex-ante skewness")
        a.set_title(ttl, fontsize=11); a.legend(frameon=False, fontsize=8)
    fig.suptitle("F35 — external validity: football and tennis on one structural law\n"
                 "(favourite falls, underdog rises with imbalance — across sports & markets)", y=1.06)
    fig.tight_layout()
    fig.savefig(FIG / "f35_crosssport.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f35_crosssport.png'} | {C.OUTDIR / 'tennis_by_tier.csv'}")
    print("  → a lei é do ESPORTE, não do futebol: 2º esporte, mercado de 2 resultados, "
          "odds independentes.")

    prov.write_stamp("48_tennis", metrics={
        "n_matches": int(n), "skew_fav": sf["skew"], "skew_dog": sd["skew"],
        "calib_pfav": calib_p, "calib_winrate": calib_w,
        "law_atp": law["ATP"], "law_wta": law["WTA"]})


if __name__ == "__main__":
    main()
