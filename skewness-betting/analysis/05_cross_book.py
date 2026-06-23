"""05 — Cross-casa (Bloco D): odd média vs melhor odd do mercado."""
from skewlib import io, returns, series
from scipy.stats import skew

def main():
    df = returns.add_returns(io.load())
    sub = df.dropna(subset=["ret_fav_max"]).copy()
    print(f"jogos com Max*: {len(sub):,}")

    or_avg = (1/sub.OddHome + 1/sub.OddDraw + 1/sub.OddAway).mean()
    or_max = (1/sub.MaxHome + 1/sub.MaxDraw + 1/sub.MaxAway).mean()
    print(f"skewness   média={skew(sub.ret_fav):.3f}  melhor={skew(sub.ret_fav_max):.3f}")
    print(f"ret médio  média={sub.ret_fav.mean():.4f} melhor={sub.ret_fav_max.mean():.4f}")
    print(f"overround  média={or_avg:.3f}     melhor={or_max:.3f}")
    print(f"ganho de arbitrar odds: {(sub.ret_fav_max.mean()-sub.ret_fav.mean())*100:.2f} p.p.")

    sa = series.rolling_skew(sub, "ret_fav", overlap=False)
    sm = series.rolling_skew(sub, "ret_fav_max", overlap=False)
    n = min(len(sa), len(sm))
    print(f"corr temporal skew(média)×skew(melhor) = {sa[:n].corr(sm[:n]):.3f}")

if __name__ == "__main__":
    main()
