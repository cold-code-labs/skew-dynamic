"""06 — Heterogeneity across leagues (E) + forensics of the 2012/13 blip (F)."""
from skewlib import io, returns, decompose

def main():
    df = returns.add_returns(io.load())

    print("E — skewness by league:")
    tab = decompose.by_league(df)
    print(tab.to_string(index=False))
    sk = tab["skew"]  # tab.skew would clash with the DataFrame.skew() method
    print(f"\ndispersion: mean={sk.mean():.3f} sd={sk.std():.3f} "
          f"range=[{sk.min():.2f},{sk.max():.2f}]")
    print(f"corr(league predictability, skewness) = {tab.p_fav_mean.corr(sk):+.3f}")

    print("\nF — active leagues per year (origin of the blip):")
    df = df.copy(); df["yr"] = df.date.dt.year
    for y in range(2010, 2015):
        n = (df[df.yr == y].Division.value_counts() > 20).sum()
        print(f"  {y}: {n} leagues")

if __name__ == "__main__":
    main()
