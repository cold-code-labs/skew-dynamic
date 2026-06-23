"""03 — Decomposição (Bloco B): por estratégia, faixa de odds, mecanismo."""
from skewlib import io, returns, decompose
from scipy.stats import skew

def main():
    df = returns.add_returns(io.load())

    print("B1 — por estratégia:")
    print(decompose.by_strategy(df).to_string(index=False))

    print("\nB2 — favorite-longshot bias por faixa de p_fav:")
    print(decompose.by_odds_bucket(df).to_string(index=False))

    print("\nB3 — mecanismo da estabilidade (correlações em janelas de 1000):")
    import pandas as pd
    rows = []
    s = df.sort_values("date").reset_index(drop=True)
    for i in range(0, len(s) - 1000, 1000):
        g = s.iloc[i:i + 1000]
        rows.append((g.p_fav.mean(), skew(g.ret_fav), g.ret_fav.std()))
    a = pd.DataFrame(rows, columns=["p_fav", "skew", "sd"])
    print(f"  corr(força favorito, variância) = {a.p_fav.corr(a.sd):+.3f}")
    print(f"  corr(força favorito, skewness)  = {a.p_fav.corr(a['skew']):+.3f}")
    print(f"  corr(variância, skewness)       = {a.sd.corr(a['skew']):+.3f}")

if __name__ == "__main__":
    main()
