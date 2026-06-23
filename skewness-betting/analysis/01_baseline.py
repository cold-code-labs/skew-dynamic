"""01 — Baseline: série de skewness + estatísticas globais."""
from skewlib import io, returns, series, stats, config as C

def main():
    df = returns.add_returns(io.load())
    print(f"N={len(df):,} | {df.date.min():%Y-%m}..{df.date.max():%Y-%m} | ligas={df.Division.nunique()}")

    from scipy.stats import skew
    se = series.bootstrap_se(df.ret_fav.values)
    print(f"skewness global (favorito): {skew(df.ret_fav):.4f} (boot SE={se:.4f})")
    print(f"retorno médio favorito:     {df.ret_fav.mean():.4f} (margem da casa)")

    ser = series.rolling_skew(df, "ret_fav")
    C.OUTDIR.mkdir(exist_ok=True)
    ser.to_csv(C.OUTDIR / "skew_series.csv")
    print(f"série: {len(ser)} pontos | média {ser.mean():.4f} | sd {ser.std():.4f}")
    print({**stats.stationarity(ser), **stats.persistence(ser)})

if __name__ == "__main__":
    main()
