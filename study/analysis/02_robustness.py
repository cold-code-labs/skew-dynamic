"""02 — Robustness (Block A): demeaning, overlap vs non-overlap, window size."""
from skewlib import io, returns, series, stats

def run(df, col, overlap, win=1000, label=""):
    ser = series.rolling_skew(df, col, window=win, overlap=overlap)
    st, ps = stats.stationarity(ser), stats.persistence(ser)
    print(f"{label:34s} n={len(ser):4d} mean={ser.mean():.3f} sd={ser.std():.3f} "
          f"ADF={st['adf_p']:.3f} KPSS={st['kpss_p']:.3f} "
          f"LB={ps['ljungbox_p']:.3f} ACF1={ps['acf1']:.3f}")

def main():
    df = returns.add_returns(io.load())
    print("Robustness of the central finding:")
    run(df, "ret_fav", True,  label="baseline (overlap)")
    run(df, "ret_dm",  True,  label="league-demeaned (overlap)")
    run(df, "ret_fav", False, label="baseline (non-overlap)")
    run(df, "ret_dm",  False, label="league-demeaned (non-overlap)")
    print("\nSensitivity to window size (demeaned, non-overlap):")
    for w in (500, 750, 1000, 1500, 2000, 3000):
        run(df, "ret_dm", False, win=w, label=f"  window={w}")

if __name__ == "__main__":
    main()
