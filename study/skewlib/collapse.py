"""Colapso de distribuição (data collapse, estilo física estatística).

A tese de "invariância de forma" (B): controlada a competitividade, a forma
INTEIRA da distribuição implícita é a mesma entre ligas — não só o 3º momento.
Dois testes complementares:

  1. `pairwise_test` sobre retornos z-scored por liga — a forma é universal SEM
     controlar competitividade? Esperado REJEITAR (a skew varia com a liga, que é
     justamente o achado): a forma não é globalmente universal, é função da
     competitividade.
  2. `conditional_invariance` — o teste FORTE: condicional à faixa de p_fav
     (competitividade), a distribuição do retorno é league-invariante? Se sim, a
     identidade da liga não acrescenta nada além da competitividade → colapso.

Caveat: o retorno do favorito é discreto (dois pontos por jogo), então o KS opera
sobre uma mistura discreta; `ks_2samp` lida com empates de forma aproximada. Os
p-valores são indicativos; a métrica de interesse é a FRAÇÃO de pares que rejeita.
"""
import numpy as np, pandas as pd, warnings
from scipy.stats import ks_2samp, anderson_ksamp


def zscore_returns(df, col="ret_fav", by="Division", min_n=2000):
    """Retornos padronizados (z-score: remove locação e escala) por grupo.
    Devolve dict grupo -> array. Padronizar isola a FORMA (skew/kurtose)."""
    out = {}
    for k, g in df.groupby(by):
        x = g[col].dropna().values
        if len(x) < min_n or x.std() == 0:
            continue
        out[k] = (x - x.mean()) / x.std()
    return out


def pairwise_test(samples, test="ks", alpha=0.05):
    """KS (ou Anderson-Darling) 2-amostras par-a-par entre grupos já padronizados.
    Com n grande o p-valor satura (rejeita tudo) → reportamos também a ESTATÍSTICA
    KS mediana (distância máxima de CDF = tamanho de efeito), que é o que importa.
    Devolve dict {pmatrix, reject_frac, median_p, median_stat}."""
    keys = list(samples)
    P = pd.DataFrame(np.eye(len(keys)), index=keys, columns=keys, dtype=float)
    pv, stat = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = samples[keys[i]], samples[keys[j]]
                if test == "ks":
                    r = ks_2samp(a, b); p, s = float(r.pvalue), float(r.statistic)
                else:  # anderson-darling k-sample (k=2)
                    ad = anderson_ksamp([a, b])
                    p, s = float(np.clip(ad.significance_level, 0, 1)), float(ad.statistic)
                P.iloc[i, j] = P.iloc[j, i] = p
                pv.append(p); stat.append(s)
    pv = np.array(pv)
    return {"pmatrix": P, "reject_frac": float((pv < alpha).mean()),
            "median_p": float(np.median(pv)), "median_stat": float(np.median(stat))}


def conditional_invariance(df, pcol="p_fav_dv", retcol="ret_fav", by="Division",
                           nbins=8, min_n=300, alpha=0.05):
    """Teste FORTE de colapso: condicional à faixa de p_fav, a distribuição do
    retorno é a mesma entre ligas? Em cada bin de quantil de p, compara cada liga
    (com ≥min_n jogos no bin) contra o RESTO do bin (one-vs-rest KS). Se a forma
    é função só da competitividade, a fração que rejeita dentro do bin é baixa.

    Devolve (tabela por (bin,liga), resumo por bin). O resumo traz a fração de
    ligas que rejeita o 'mesma forma que o resto' em cada faixa de competitividade.
    """
    d = df[[pcol, retcol, by]].dropna().copy()
    d["pbin"] = pd.qcut(d[pcol], nbins, duplicates="drop")
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for b, gb in d.groupby("pbin", observed=True):
            for lg, gl in gb.groupby(by, observed=True):
                if len(gl) < min_n:
                    continue
                rest = gb[gb[by] != lg][retcol].values
                if len(rest) < min_n:
                    continue
                ks = ks_2samp(gl[retcol].values, rest)
                rows.append({"pbin": str(b), "p_mid": float(gb[pcol].median()),
                             by: lg, "n": len(gl), "ks_stat": float(ks.statistic),
                             "ks_p": float(ks.pvalue), "reject": ks.pvalue < alpha})
    tab = pd.DataFrame(rows)
    if tab.empty:
        return tab, pd.DataFrame()
    summ = (tab.groupby("pbin", observed=True)
               .agg(p_mid=("p_mid", "first"), n_leagues=("reject", "size"),
                    reject_frac=("reject", "mean"), ks_stat_med=("ks_stat", "median"))
               .reset_index().sort_values("p_mid"))
    return tab, summ


def ecdf(x):
    """ECDF (xs ordenado, F) para sobrepor curvas no plot do colapso."""
    xs = np.sort(np.asarray(x, float))
    return xs, np.arange(1, len(xs) + 1) / len(xs)
