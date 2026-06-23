"""06 — Heterogeneidade entre ligas (E) + forense do blip 2012/13 (F)."""
from skewlib import io, returns, decompose

def main():
    df = returns.add_returns(io.load())

    print("E — skewness por liga:")
    tab = decompose.by_league(df)
    print(tab.to_string(index=False))
    print(f"\ndispersão: média={tab.skew.mean():.3f} sd={tab.skew.std():.3f} "
          f"range=[{tab.skew.min():.2f},{tab.skew.max():.2f}]")
    print(f"corr(previsibilidade da liga, skewness) = {tab.p_fav_mean.corr(tab.skew):+.3f}")

    print("\nF — ligas ativas por ano (origem do blip):")
    df = df.copy(); df["yr"] = df.date.dt.year
    for y in range(2010, 2015):
        n = (df[df.yr == y].Division.value_counts() > 20).sum()
        print(f"  {y}: {n} ligas")

if __name__ == "__main__":
    main()
