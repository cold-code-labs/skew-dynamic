"""33 — C3: Kelly / staking ótimo sob a estrutura de skewness. O que a assimetria
implica para o crescimento de banca? (1) sob a margem real, Kelly manda NÃO apostar
em quase tudo — a estrutura não dá crescimento (eficiência, ecoa C1); (2) a
decomposição de momentos do log-crescimento isola o PAPEL da skewness e explica por
que o apostador de azarão tolera EV negativo: a skew positiva ADICIONA à utilidade
log, um "prêmio de skewness" que ele paga em EV.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skewlib import io, returns, exante, staking as st, provenance as prov, config as C


def main():
    df = exante.add_exante(returns.add_returns(io.load()))
    p = df.p_fav_dv.values; o = df.o_fav.values
    print(f"N={len(df):,}")

    # (1) Kelly sob a margem real: quase tudo f*=0
    f_real = st.kelly_fraction(p, o)
    pos = float((f_real > 0).mean())
    print(f"\n(1) KELLY sob a margem real (odds com vig):")
    print(f"  fração de apostas com f*>0 (EV>0) = {pos:.1%}; f* médio = {f_real.mean():.4f}")
    print(f"  → após a margem, não há crescimento a extrair (mercado eficiente, ~C1).")

    # (2) papel da skewness no crescimento — favorito (skew−) vs azarão (skew+)
    #     a uma fração fixa pequena f0, decompõe g ≈ μ·f − σ²f²/2 + m₃f³/3
    f0 = 0.05
    pud = 1 - p; oud = 1.0 / np.clip(pud, 1e-6, None)        # azarão a odd justa do dog
    # azarão real: a "outra ponta" — usa odd implícita do não-favorito
    P = df[["p_H", "p_D", "p_A"]].to_numpy(float)
    O = df[["OddHome", "OddDraw", "OddAway"]].to_numpy(float)
    j = P.argmax(1); i = np.arange(len(P))
    # azarão = menor prob (maior odd)
    k = P.argmin(1)
    p_dog, o_dog = P[i, k], O[i, k]

    tf = st.moment_growth_terms(p, o, np.full_like(p, f0))     # favorito
    td = st.moment_growth_terms(p_dog, o_dog, np.full_like(p_dog, f0))  # azarão
    print(f"\n(2) DECOMPOSIÇÃO do log-crescimento a f={f0} (×1e3):")
    print(f"  {'aposta':10} {'μ (mean)':>10} {'−σ²/2 (var)':>12} {'skew':>10} {'soma':>10}")
    for lab, t in [("favorito", tf), ("azarão", td)]:
        m, v, s = t["mean"].mean()*1e3, t["var"].mean()*1e3, t["skew"].mean()*1e3
        print(f"  {lab:10} {m:>10.3f} {v:>12.3f} {s:>+10.3f} {m+v+s:>10.3f}")
    print("  → no azarão o termo de SKEWNESS é positivo e grande: a assimetria")
    print("    compensa parte do EV negativo no crescimento/utilidade — o canal")
    print("    pelo qual o FLB (preferência por skew) sobrevive a ser EV-negativo.")

    # curva: termo de skewness ao longo de p_fav (a fração unitária)
    grid = np.linspace(0.05, 0.95, 60)
    skew_unit = np.array([st.moment_growth_terms(np.array([q]), np.array([1.0/q]),
                          np.array([f0]))["skew"][0] for q in grid]) * 1e3

    C.OUTDIR.mkdir(exist_ok=True)
    FIG = C.OUTDIR / "fig"; FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].hist(f_real, bins=40, color="#1f77b4")
    axes[0].set_xlabel("fração de Kelly f* (odds reais)"); axes[0].set_ylabel("jogos")
    axes[0].set_title(f"Kelly ≈ 0 após a margem ({pos:.0%} com EV>0)")
    axes[1].axhline(0, color="0.7", lw=.8); axes[1].axvline(0.5, color="0.85", lw=.8)
    axes[1].plot(grid, skew_unit, color="#d62728", lw=2)
    axes[1].set_xlabel("prob. p do lado apostado"); axes[1].set_ylabel("termo de skew no g (×1e3)")
    axes[1].set_title("Skewness impulsiona o crescimento no azarão (p<0.5)")
    fig.suptitle("F21 — C3: Kelly/crescimento sob a estrutura de skewness", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "f21_kelly.png", dpi=C.FIG_DPI, bbox_inches="tight"); plt.close(fig)
    print(f"\n  -> {FIG / 'f21_kelly.png'}")

    prov.write_stamp("33_kelly_staking", metrics={
        "frac_positive_ev": pos, "skew_term_dog": float(td["skew"].mean()*1e3),
        "skew_term_fav": float(tf["skew"].mean()*1e3)})


if __name__ == "__main__":
    main()
