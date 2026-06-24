"""03 — Decomposition (Block B): by strategy, odds bucket, mechanism."""
from skewlib import io, returns, decompose
from scipy.stats import skew

def main():
    df = returns.add_returns(io.load())

    print("B1 — by strategy:")
    print(decompose.by_strategy(df).to_string(index=False))

    print("\nB2 — favorite-longshot bias by p_fav bucket:")
    print(decompose.by_odds_bucket(df).to_string(index=False))

    print("\nB3 — mechanism of the stability (correlations over windows of 1000):")
    import pandas as pd
    rows = []
    s = df.sort_values("date").reset_index(drop=True)
    for i in range(0, len(s) - 1000, 1000):
        g = s.iloc[i:i + 1000]
        rows.append((g.p_fav.mean(), skew(g.ret_fav), g.ret_fav.std()))
    a = pd.DataFrame(rows, columns=["p_fav", "skew", "sd"])
    print(f"  corr(favourite strength, variance) = {a.p_fav.corr(a.sd):+.3f}")
    print(f"  corr(favourite strength, skewness) = {a.p_fav.corr(a['skew']):+.3f}")
    print(f"  corr(variance, skewness)           = {a.sd.corr(a['skew']):+.3f}")

if __name__ == "__main__":
    main()
