"""05 — Cross-book (Block D): average odd vs best market odd."""
from skewlib import io, returns, series
from scipy.stats import skew

def main():
    df = returns.add_returns(io.load())
    sub = df.dropna(subset=["ret_fav_max"]).copy()
    print(f"games with Max*: {len(sub):,}")

    or_avg = (1/sub.OddHome + 1/sub.OddDraw + 1/sub.OddAway).mean()
    or_max = (1/sub.MaxHome + 1/sub.MaxDraw + 1/sub.MaxAway).mean()
    print(f"skewness   avg={skew(sub.ret_fav):.3f}  best={skew(sub.ret_fav_max):.3f}")
    print(f"mean ret   avg={sub.ret_fav.mean():.4f} best={sub.ret_fav_max.mean():.4f}")
    print(f"overround  avg={or_avg:.3f}     best={or_max:.3f}")
    print(f"gain from arbitraging odds: {(sub.ret_fav_max.mean()-sub.ret_fav.mean())*100:.2f} pp")

    sa = series.rolling_skew(sub, "ret_fav", overlap=False)
    sm = series.rolling_skew(sub, "ret_fav_max", overlap=False)
    n = min(len(sa), len(sm))
    print(f"temporal corr skew(avg)×skew(best) = {sa[:n].corr(sm[:n]):.3f}")

if __name__ == "__main__":
    main()
