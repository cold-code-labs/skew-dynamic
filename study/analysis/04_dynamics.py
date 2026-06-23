"""04 — Dinâmica (Bloco C): a série é i.i.d.? Variance-ratio, AR(1), quebras."""
from skewlib import io, returns, series, stats

def main():
    df = returns.add_returns(io.load())
    ser = series.rolling_skew(df, "ret_fav", overlap=False)  # janelas disjuntas
    print(f"série não-overlap: n={len(ser)}, média={ser.mean():.3f}")

    vr = stats.variance_ratio(ser)
    for k, v in vr.items():
        print(f"  Variance Ratio({k}) = {v:.3f}  (=1 → i.i.d.)")

    a = stats.ar1(ser)
    print(f"  AR(1) phi = {a['phi']:+.3f} (p={a['phi_p']:.3f}) half-life={a['half_life']:.2f}")
    print(f"  → {'ruído branco confirmado' if a['phi_p'] > 0.05 else 'há estrutura AR'}")

    bks = stats.breakpoints(ser)
    print(f"  quebras estruturais: {len(bks)} {[str(b.date()) for b in bks]}")

if __name__ == "__main__":
    main()
