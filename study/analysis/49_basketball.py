"""49 — Frente T: VALIDADE EXTERNA (basquete). A lei skew=f(competitividade) e o
formato lotérico do azarão valem num 3º esporte?

Usa a camada canônica (skewlib/canonical + adapters/basketball) — zero ciência nova —
sobre o snapshot congelado da NBA (sportsbookreviewsonline.com; hash em
data/PROVENANCE-basketball.json). Mercado MONEYLINE (2 resultados, sem empate), fonte
de odds independente do futebol e do tênis. Compara, na MESMA curva, o futebol (38
ligas, de findings.json), o tênis (tiers ATP/WTA, de tennis_by_tier.csv se presente) e
o basquete (temporadas da NBA).

Achado: a assinatura reaparece num 3º esporte. O favorito é mais negativo nas
temporadas mais desbalanceadas (corr(skew_fav, p_fav) por temporada ≈ −0.95); o azarão
é lotérico (~+2.6, como futebol/tênis); calibração sã (p_fav ≈ vitória real). A
invariância estrutural é do ESPORTE como sistema competitivo — não do 1X2, do futebol
nem do tênis.
"""
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import canonical, config as C, provenance as prov
from skewlib.adapters import basketball

BBALL = C.DATA_PATH.parent / "basketball.csv"
PROV = C.DATA_PATH.parent / "PROVENANCE-basketball.json"
ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
FINDINGS = ROOT / "site" / "src" / "data" / "findings.json"
TENNIS_CSV = C.OUTDIR / "tennis_by_tier.csv"


def _verify_hash():
    want = json.loads(PROV.read_text())["sha256"]
    h = hashlib.sha256()
    with open(BBALL, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    got = h.hexdigest()
    assert got == want, f"basketball.csv mudou: {got[:12]} != snapshot {want[:12]}"
    print(f"snapshot OK — sha256 {got[:12]} == PROVENANCE-basketball.json", flush=True)


def main():
    _verify_hash()
    raw = pd.read_csv(BBALL, low_memory=False)

    # assinatura global + calibração (o de-vig é confiável em basquete?)
    can = basketball.to_canonical(raw)
    canonical.validate(can)
    n = can.event_id.nunique()
    fav = canonical.select(can, "fav"); dog = canonical.select(can, "dog")
    sf = canonical.signature(fav, "fav"); sd = canonical.signature(dog, "dog")
    calib_p, calib_w = float(fav.p.mean()), float(fav.won.mean())
    print(f"\nBASQUETE — {n:,} jogos (NBA), mercado moneyline (2 resultados):")
    print(f"  favorito skew = {sf['skew']:+.3f} | azarão skew = {sd['skew']:+.3f}")
    print(f"  calibração: p_fav médio {calib_p:.3f} ≈ vitória real do favorito {calib_w:.3f}")

    # a lei por temporada (a competitividade da NBA varia ano a ano)
    bk = canonical.bettype_by(can, by="competition", kinds=("fav", "dog"),
                              min_n=500).dropna().sort_values("p_fav_mean")
    law_nba = float(np.corrcoef(bk.skew_fav, bk.p_fav_mean)[0, 1])
    print(f"  lei NBA: corr(skew_fav, p_fav) por temporada = {law_nba:+.2f} ({len(bk)} temporadas)")

    # futebol (findings.json) + tênis (tennis_by_tier.csv, se a frente S já rodou)
    fb = pd.DataFrame(json.loads(FINDINGS.read_text())["bettype"]["leagues"])
    tn = pd.read_csv(TENNIS_CSV) if TENNIS_CSV.exists() else None

    C.OUTDIR.mkdir(exist_ok=True)
    bk.to_csv(C.OUTDIR / "basketball_by_season.csv", index=False)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for a, fcol, bcol, tcol, ttl in [(ax[0], "fav", "skew_fav", "skew_fav", "favourite bet"),
                                     (ax[1], "dog", "skew_dog", "skew_dog", "underdog bet")]:
        a.scatter(fb.p_fav, fb[fcol], s=26, c="#4a78b5", alpha=.7, label="football leagues (38)")
        if tn is not None:
            a.scatter(tn.p_fav_mean, tn[tcol], s=60, marker="D", c="#d9822b",
                      edgecolor="#7a4a10", label="tennis tiers (ATP+WTA)")
        a.scatter(bk.p_fav_mean, bk[bcol], s=64, marker="s", c="#3a9d5d",
                  edgecolor="#1f5e35", label="basketball seasons (NBA)")
        a.axhline(0, color="0.85", lw=.8)
        a.set_xlabel("competitiveness (mean favourite probability)")
        a.set_ylabel("ex-ante skewness")
        a.set_title(ttl, fontsize=11); a.legend(frameon=False, fontsize=8)
    fig.suptitle("F36 — external validity: football, tennis and basketball on one structural law\n"
                 "(favourite falls, underdog rises with imbalance — across three sports & markets)", y=1.06)
    fig.tight_layout()
    fig.savefig(FIG / "f36_crosssport.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f36_crosssport.png'} | {C.OUTDIR / 'basketball_by_season.csv'}")
    print("  → a lei é do ESPORTE: 3º esporte, mercado moneyline, odds independentes.")

    prov.write_stamp("49_basketball", metrics={
        "n_matches": int(n), "skew_fav": sf["skew"], "skew_dog": sd["skew"],
        "calib_pfav": calib_p, "calib_winrate": calib_w, "law_nba": law_nba})


if __name__ == "__main__":
    main()
