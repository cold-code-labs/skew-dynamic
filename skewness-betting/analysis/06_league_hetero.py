"""06 — Heterogeneidade entre ligas (E) + forense do blip 2012/13 (F)."""
from skewlib import io, returns, decompose

def main():
    df = returns.add_returns(io.load())

    print("E — skewness por liga:")
    tab = decompose.by_league(df)
    print(tab.to_string(index=False))
    sk = tab["skew"]  # tab.skew colidiria com o método DataFrame.skew()
    print(f"\ndispersão: média={sk.mean():.3f} sd={sk.std():.3f} "
          f"range=[{sk.min():.2f},{sk.max():.2f}]")
    print(f"corr(previsibilidade da liga, skewness) = {tab.p_fav_mean.corr(sk):+.3f}")

    print("\nF — ligas ativas por ano (origem do blip):")
    df = df.copy(); df["yr"] = df.date.dt.year
    for y in range(2010, 2015):
        n = (df[df.yr == y].Division.value_counts() > 20).sum()
        print(f"  {y}: {n} ligas")

if __name__ == "__main__":
    main()
