"""10 — Mercado binário over/under 2.5 (W5): o teste mais limpo da identidade
mecânica. Sem empate → a skewness é função de um único p. Confirma que o achado
do W1 não depende da estrutura de 3 vias do 1X2.
"""
import numpy as np, pandas as pd
from scipy.stats import skew
from skewlib import io, overunder, exante, config as C


def main():
    df = io.load()
    d = overunder.prep(df)
    print(f"N={len(d):,} jogos com O/U 2.5 | overround médio={d.overround.mean():.4f} | "
          f"Shin z médio={d.shin_z.mean():.4f}")
    print(f"taxa over (gols≥3) = {d.over.mean():.3f} | "
          f"p_over de-vigada média = {d.p_over.mean():.3f} (calibração)")

    print("\nGLOBAL — aposta no favorito O/U: ex-ante vs ex-post:")
    g = exante.pooled_skew(d.p_fav_ou.values, d.o_fav_ou.values)
    print(f"  skew ex-ante = {g['skew']:+.4f}  | within(intra-jogo) = {g['within_frac']:+.1%}")
    print(f"  skew ex-post = {skew(d.ret_fav_ou):+.4f}  (realizada)")
    print(f"  ret médio favorito = {d.ret_fav_ou.mean():+.4f}")

    print("\nIdentidade pura: skew ex-ante = (1-2p)/√(p(1-p)) por jogo")
    p = d.p_fav_ou.values
    ident = (1 - 2 * p) / np.sqrt(p * (1 - p))
    print(f"  per-match skew (fórmula) vs exante.per_match_skew: "
          f"max|dif| = {np.abs(ident - exante.per_match_skew(p)).max():.2e}")

    print("\nPor faixa de p (lado favorito) — ex-ante×ex-post:")
    d["bucket"] = pd.cut(d.p_fav_ou, [0.5, .55, .6, .65, .7, .8, 1.0])
    rows = []
    for b, gb in d.groupby("bucket", observed=True):
        if len(gb) < 200:
            continue
        ex = exante.pooled_skew(gb.p_fav_ou.values, gb.o_fav_ou.values)
        rows.append({"bucket": str(b), "n": len(gb), "p_mean": gb.p_fav_ou.mean(),
                     "skew_exante": ex["skew"], "skew_expost": skew(gb.ret_fav_ou),
                     "win_rate": (gb.ret_fav_ou > 0).mean()})
    print(pd.DataFrame(rows).to_string(index=False,
          formatters={c: "{:.3f}".format for c in ["p_mean", "skew_exante", "skew_expost", "win_rate"]}))

    print("\n→ O/U é binário, p~0.5 (poucos gols extremos), skewness pequena mas "
          "rege-se pela MESMA identidade. within≈100% confirma o núcleo do W1\n"
          "  fora da estrutura 1X2.")

    C.OUTDIR.mkdir(exist_ok=True)
    d[["Division", "p_fav_ou", "o_fav_ou", "ret_fav_ou", "over"]].to_csv(
        C.OUTDIR / "overunder.csv", index=False)
    print(f"  -> {C.OUTDIR / 'overunder.csv'}")


if __name__ == "__main__":
    main()
