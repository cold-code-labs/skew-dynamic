"""01 — Baseline: skewness series + global statistics."""
from skewlib import io, returns, series, stats, config as C

def main():
    df = returns.add_returns(io.load())
    print(f"N={len(df):,} | {df.date.min():%Y-%m}..{df.date.max():%Y-%m} | leagues={df.Division.nunique()}")

    from scipy.stats import skew
    se = series.bootstrap_se(df.ret_fav.values)
    print(f"global skewness (favourite): {skew(df.ret_fav):.4f} (boot SE={se:.4f})")
    print(f"mean favourite return:       {df.ret_fav.mean():.4f} (house margin)")

    ser = series.rolling_skew(df, "ret_fav")
    C.OUTDIR.mkdir(exist_ok=True)
    ser.to_csv(C.OUTDIR / "skew_series.csv")
    print(f"series: {len(ser)} points | mean {ser.mean():.4f} | sd {ser.std():.4f}")
    print({**stats.stationarity(ser), **stats.persistence(ser)})

if __name__ == "__main__":
    main()
