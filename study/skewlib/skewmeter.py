"""skew-meter — instrumento de SIMILARIDADE DE ASSIMETRIAS.

Objetivo-raiz do estudo: medir quão parecidas são as assimetrias (skewness/forma)
de duas entidades — ligas, eras, mercados (1X2/O/U/AH), modelos, janelas no tempo.
Reúne a maquinaria do estudo num único aparelho de POUCOS parâmetros:

  measure(p, o)            assinatura de assimetria (skew/var/exkurt + competitividade).
  gauge_cheap / _1param /  variantes de custo decrescente: sem Shin (inverse-odds),
  _oddsfree                1 parâmetro (média de p_fav → forma fechada), e só
                           resultados (upset rate).
  predict_skew(comp)       a lei skew=f(competitividade) avaliada (forma fechada).
  residual(sig)            assimetria IDIOSSINCRÁTICA: skew − o que a competitividade
                           explica. ≈0 ⇒ a competitividade é estatística suficiente.
  skew_se(p, o)            piso amostral (SE bootstrap) — calibra "parecido".
  similar(A, B)            veredito: a assimetria residual cabe no ruído? (z-score).
  matrix(sigs)             distâncias par-a-par: BRUTA vs RESIDUAL.

Achado-âncora (Frente B2, agora operacionalizado): a distância BRUTA entre ligas é
grande, mas a RESIDUAL (condicionando na competitividade) colapsa ao piso amostral —
as assimetrias são as MESMAS quando a competitividade é igualada. O aparelho mede
isso par a par, com distância calibrada e nulo.
"""
import numpy as np
from . import exante, model


# ── medição: assinatura de assimetria (com variantes de poucos parâmetros) ───
def measure(p, o, label=None, n=None):
    """Assinatura de assimetria de uma entidade a partir de (p_fav, o_fav)."""
    m = exante.pooled_moments(np.asarray(p, float), np.asarray(o, float), max_order=4)
    return {"label": label, "n": int(n if n is not None else len(p)),
            "skew": m["skew"], "var": m["var"], "exkurt": m["exkurt"],
            "within": m["within_frac_m3"], "comp": float(np.mean(p))}


def gauge_cheap(odds_HDA):
    """Assinatura SEM Shin: prob do favorito por inverse-odds normalizada (1 conta,
    ~0 custo). odds_HDA: array (n,3) das odds 1X2. corr≈1.0 com a verdade (Shin)."""
    r = 1.0 / np.asarray(odds_HDA, float)
    P = r / r.sum(1, keepdims=True)
    pf = P.max(1)
    return measure(pf, 1.0 / pf)


def gauge_oddsfree(upset_rate):
    """Proxy odds-free (só W/D/L): a competitividade pela taxa de zebra do Elo de
    resultados. Devolve o número de competitividade; vira skew via predict_skew∘mapa
    (corr≈0.83 — o limite de não usar nenhuma odd)."""
    return float(upset_rate)


# ── a lei skew=f(competitividade) como base de cálculo (1 parâmetro) ──────────
def fit_law(df):
    """Calibra a curva fechada S(competitividade) uma vez (ordered-probit) e devolve
    um avaliador comp→skew. `df` precisa de FTResult e p_fav_dv."""
    par = model.calibrate(home=(df.FTResult == "H").mean(),
                          draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.05, 1.30, 80)
    cpf, csk = model.curve_exact(par["h"], par["c"], sig)
    o = np.argsort(cpf)
    cpf, csk = cpf[o], csk[o]
    return {"par": par, "cpf": cpf, "csk": csk}


def predict_skew(comp, law):
    """Skew prevista pela competitividade (1 parâmetro), via forma fechada."""
    return float(np.interp(comp, law["cpf"], law["csk"]))


def residual(sig, law):
    """Assimetria idiossincrática: observada − explicada pela competitividade."""
    return sig["skew"] - predict_skew(sig["comp"], law)


# ── nulo amostral: piso de ruído (calibra 'parecido') ────────────────────────
def skew_se(p, o, B=300, seed=42):
    """SE bootstrap da skew agrupada — o piso abaixo do qual duas assimetrias são
    indistinguíveis. Reamostra jogos com reposição."""
    p = np.asarray(p, float); o = np.asarray(o, float); n = len(p)
    rng = np.random.default_rng(seed)
    vals = [exante.pooled_skew(p[i], o[i])["skew"]
            for i in (rng.integers(0, n, n) for _ in range(B))]
    return float(np.std(vals))


# ── similaridade de assimetrias ──────────────────────────────────────────────
def distance(A, B, kind="skew"):
    """Distância BRUTA entre assinaturas. kind='skew' (escalar) ou 'shape'
    (forma padronizada: skew + exkurt, scale-free)."""
    if kind == "skew":
        return abs(A["skew"] - B["skew"])
    da = np.array([A["skew"], A["exkurt"]]); db = np.array([B["skew"], B["exkurt"]])
    return float(np.linalg.norm(da - db))


def residual_distance(A, B, law):
    """Distância entre as assimetrias DEPOIS de descontar a competitividade — quão
    diferentes A e B são além do que a competitividade já explica."""
    return abs(residual(A, law) - residual(B, law))


def similar(A, B, law, seA=None, seB=None, z_thr=2.0):
    """Veredito de similaridade de assimetrias. Compara a distância RESIDUAL ao piso
    amostral combinado: z<z_thr ⇒ 'mesma assimetria' (a diferença é ruído)."""
    rd = residual_distance(A, B, law)
    se = np.hypot(seA or 0.0, seB or 0.0)
    z = rd / se if se > 0 else np.inf
    return {"raw": distance(A, B), "residual": rd, "noise": float(se),
            "z": float(z), "same_asymmetry": bool(z < z_thr)}


def sufficiency_ladder(df, law, min_n=2000):
    """Escada de suficiência: quanta da assimetria entre ligas cada conjunto de
    parâmetros da competitividade explica. 1 momento (média p_fav, forma fechada) →
    2 momentos (média+variância, OLS) → distribuição INTEIRA (skew sob odds justas,
    = imagem mecânica da distribuição de p). Devolve R² de cada degrau."""
    import numpy as np
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_n:
            continue
        p = g.p_fav_dv.values; o = g.o_fav.values
        rows.append({"truth": exante.pooled_skew(p, o)["skew"],
                     "mean_pf": float(p.mean()), "var_pf": float(p.var()),
                     "pred1": predict_skew(float(p.mean()), law),
                     "full": exante.pooled_skew(p, 1.0 / p)["skew"]})
    t = np.array([r["truth"] for r in rows])
    def r2(pred): return float(np.corrcoef(t, pred)[0, 1] ** 2)
    p1 = np.array([r["pred1"] for r in rows])
    full = np.array([r["full"] for r in rows])
    X = np.column_stack([np.ones(len(rows)), [r["mean_pf"] for r in rows],
                         [r["var_pf"] for r in rows]])
    beta = np.linalg.lstsq(X, t, rcond=None)[0]
    p2 = X @ beta
    return {"r2_1param": r2(p1), "r2_2moment": r2(p2), "r2_full": r2(full),
            "n_leagues": len(rows), "resid_sd_1param": float((t - p1).std()),
            "resid_sd_full": float((t - full * (np.std(t) / np.std(full))).std())}


def split_half_residual(df, law, min_n=4000):
    """Estabilidade do resíduo idiossincrático: corr entre o resíduo medido em
    temporadas PARES vs ÍMPARES. Alto ⇒ o resíduo é traço real da liga, não ruído."""
    import numpy as np, pandas as pd
    d = df.copy(); d["yr"] = d.date.dt.year
    rows = []
    for lg, g in d.groupby("Division"):
        ev = g[g.yr % 2 == 0]; od = g[g.yr % 2 == 1]
        if len(ev) < min_n or len(od) < min_n:
            continue
        se = measure(ev.p_fav_dv.values, ev.o_fav.values)
        so = measure(od.p_fav_dv.values, od.o_fav.values)
        rows.append((residual(se, law), residual(so, law)))
    a = np.array([r[0] for r in rows]); b = np.array([r[1] for r in rows])
    return {"r": float(np.corrcoef(a, b)[0, 1]), "n_leagues": len(rows)}


def skew_se_block(g, B=150, seed=42):
    """SE da skew por BLOCK-bootstrap de TEMPORADAS (reamostra anos inteiros) —
    respeita a dependência intra-temporada que `skew_se` (jogos i.i.d.) ignora.
    Piso amostral mais honesto. `g`: frame da liga com date/p_fav_dv/o_fav."""
    import numpy as np, pandas as pd
    g = g.copy(); g["yr"] = g.date.dt.year
    seasons = [sg for _, sg in g.groupby("yr")]
    if len(seasons) < 2:
        return skew_se(g.p_fav_dv.values, g.o_fav.values, B=B, seed=seed)
    rng = np.random.default_rng(seed); m = len(seasons)
    vals = []
    for _ in range(B):
        sub = pd.concat([seasons[i] for i in rng.integers(0, m, m)])
        vals.append(exante.pooled_skew(sub.p_fav_dv.values, sub.o_fav.values)["skew"])
    return float(np.std(vals))


def sampling_shape_cov(g, B=200, seed=1):
    """Covariância amostral de (skew, exkurt) de uma liga por bootstrap de jogos —
    a métrica para a distância de forma de Mahalanobis (ciente de escala e correlação)."""
    import numpy as np
    p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
    rng = np.random.default_rng(seed)
    S = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        m = exante.pooled_moments(p[i], o[i], max_order=4)
        S.append([m["skew"], m["exkurt"]])
    return np.cov(np.array(S).T)


def shape_distance(A, B, cov_inv):
    """Distância de forma de MAHALANOBIS em (skew, exkurt) — métrica scale/correlation
    -aware, supera o |Δskew| escalar e o Euclidiano cru de `distance(kind='shape')`."""
    import numpy as np
    d = np.array([A["skew"] - B["skew"], A["exkurt"] - B["exkurt"]])
    return float(np.sqrt(d @ cov_inv @ d))


def law_oos_r2(df, min_n=2000):
    """Calibração OUT-OF-SAMPLE: ajusta a lei nas taxas de temporadas PARES e prevê
    a skew das ligas em temporadas ÍMPARES (a lei nunca vê o alvo de teste). R² alto
    ⇒ a lei não é overfit; a régua do resíduo é honesta."""
    import numpy as np
    d = df.copy(); d["yr"] = d.date.dt.year
    ev, od = d[d.yr % 2 == 0], d[d.yr % 2 == 1]
    law_ev = fit_law(ev)
    t, pred = [], []
    for lg, g in od.groupby("Division"):
        if len(g) < min_n:
            continue
        t.append(exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"])
        pred.append(predict_skew(float(g.p_fav_dv.mean()), law_ev))
    return float(np.corrcoef(t, pred)[0, 1] ** 2)


def tost(A, B, law, seA, seB, margin):
    """Teste de equivalência (TOST) — o veredito certo com n enorme (significância
    sempre rejeita). 'Mesma assimetria' se o IC de 90% da diferença residual cabe
    em [−margin, +margin]. margin = meio desvio entre-ligas, pré-registrado."""
    import numpy as np
    d = residual(A, law) - residual(B, law)
    se = float(np.hypot(seA, seB))
    return {"d": float(d), "se": se, "margin": float(margin),
            "equivalent": bool(abs(d) + 1.645 * se < margin)}


def matrix(sigs, law, ses=None):
    """Matrizes de distância par-a-par (BRUTA e RESIDUAL) entre N entidades.
    Devolve dict com as matrizes e resumos. O colapso da BRUTA→RESIDUAL é a
    similaridade de assimetrias do estudo, operacionalizada."""
    n = len(sigs)
    raw = np.zeros((n, n)); res = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            raw[i, j] = distance(sigs[i], sigs[j])
            res[i, j] = residual_distance(sigs[i], sigs[j], law)
    iu = np.triu_indices(n, 1)
    noise = float(np.median(ses)) if ses is not None else None
    return {"raw": raw, "residual": res,
            "labels": [s["label"] for s in sigs],
            "median_raw": float(np.median(raw[iu])),
            "median_residual": float(np.median(res[iu])),
            "noise_floor": noise,
            "collapse": float(np.median(res[iu]) / np.median(raw[iu]))}
