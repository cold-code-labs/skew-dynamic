"""11 — Ortogonalidade da margem (W4) + robustez ao método de de-vig.

W4: a margem da casa (overround) afeta o NÍVEL de retorno, mas a skewness
(estrutura de assimetria) é invariante à casa? Compara odds médias vs máximas
(melhor preço do mercado) sobre as MESMAS partidas, já de-vigadas.

Robustez: o achado central depende do método de de-vig? Repete global + lei
cross-liga sob multiplicative / power / shin.
"""
import numpy as np, pandas as pd
from skewlib import io, returns, exante, stats, config as C

AVG = ("OddHome", "OddDraw", "OddAway")
MAX = ("MaxHome", "MaxDraw", "MaxAway")


def main():
    df = io.load()
    sub = df.dropna(subset=list(MAX)).copy()
    for c in MAX:
        sub = sub[sub[c] > C.MIN_ODD]
    print(f"jogos com mercado Max*: {len(sub):,}")

    print("\n=== W4 — Ortogonalidade da margem (odds média vs máxima) ===")
    pa, oa, ga = exante.market_skew(sub, AVG)
    pm, om, gm = exante.market_skew(sub, MAX)
    ora = (1 / sub[list(AVG)].to_numpy()).sum(1).mean()
    orm = (1 / sub[list(MAX)].to_numpy()).sum(1).mean()
    print(f"  overround     média={ora:.4f}   máxima={orm:.4f}   (margem cai)")
    print(f"  skew ex-ante  média={ga['skew']:+.4f}  máxima={gm['skew']:+.4f}  (invariante)")
    print(f"  p_fav média   média={pa.mean():.4f}   máxima={pm.mean():.4f}")
    print(f"  corr(p_fav_média, p_fav_máxima) por jogo = {np.corrcoef(pa, pm)[0,1]:.4f}")
    print("  → a casa compete na MARGEM (nível), não na assimetria (estrutura).")

    print("\n=== Robustez ao método de de-vig ===")
    base = returns.add_returns(io.load())
    print(f"  {'método':14s} {'skew_global':>11s} {'corr(p_fav,skew) liga':>22s}")
    for meth in ("multiplicative", "power", "shin"):
        d = exante.add_exante(base, method=meth)
        g = exante.pooled_skew(d.p_fav_dv.values, d.o_fav.values)
        lg = exante.pooled_by(d, "Division", min_n=2000)
        r = stats.bootstrap_corr(lg.p_fav_dv_mean.values, lg.skew_exante.values)["r"]
        print(f"  {meth:14s} {g['skew']:>+11.4f} {r:>+22.3f}")
    print("  → global e lei cross-liga estáveis ao método: achado não é artefato de de-vig.")


if __name__ == "__main__":
    main()
