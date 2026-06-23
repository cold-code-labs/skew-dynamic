"""Frente O — bateria de modelos geradores: a lei skewness=f(competitividade) é
independente do modelo? A Frente I mostrou que um Poisson de gols cai na mesma
curva que o ordered-probit de margem. Aqui ampliamos para uma BATERIA de
geradores genuinamente distintos, cada um produzindo (pH,pD,pA) por jogo, e
testamos se TODOS reproduzem a lei e caem na curva S(σ_L) do modelo de força:

  • Poisson (Maher)         — gols independentes; âncora na grade (= Frente I).
  • Dixon-Coles (1997)      — Poisson + correção de dependência em placares baixos
                              (ρ): ajuste fino de 0-0/0-1/1-0/1-1 vs independência.
  • Bradley-Terry-Davidson  — forças multiplicativas + empate (Davidson 1970), por
    (1970)                    COMPARAÇÃO PAREADA logística, SEM gols. Família
                              totalmente distinta (nem Poisson, nem probit).
  • Elo de resultados       — forças por rating de resultados (sem gols nem odds) →
                              mapa ordinal (MNLogit). 4ª família, liga à W2/P2.

Os geradores de gols (Poisson/DC) compartilham as taxas λ de `goals.fit_rates`
(mesmo ataque/defesa+mando), isolando o efeito da dependência (ρ) sobre as
probabilidades de resultado e a skewness. BTD e Elo ajustam forças próprias.
Todos usam `goals.degenerate_fit` p/ descartar ajustes degenerados (separação do
GLM, ex.: JAP 2017).

Nota (modelos que NÃO entram): gols de futebol são Poisson independente quase
puro — covariância casa×fora ≈ −0.07 (mediana) e super-dispersão ≈ 0. Logo um
Poisson BIVARIADO (λ₃≥0) e um Negative-Binomial (NB2, α) colapsam ao Poisson e
nada acrescentam à figura; reportamos esse colapso como robustez, não como série.
"""
import warnings
import numpy as np, pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize_scalar, minimize
from . import goals, exante
warnings.filterwarnings("ignore")

MAXG = 12                       # teto de gols na grade (cauda além disso desprezível)
_GG = np.arange(MAXG + 1)
MODELS = ["poisson", "dixoncoles", "btd", "elo"]


def _result_probs(joint):
    """(pH,pD,pA) a partir da conjunta joint[...,x,y]=P(casa=x, fora=y): casa
    vence x>y (triangular inferior), empate x=y (diagonal), fora x<y."""
    H = np.tril(joint, -1).sum(axis=(-2, -1))
    A = np.triu(joint, 1).sum(axis=(-2, -1))
    D = np.trace(joint, axis1=-2, axis2=-1)
    s = H + D + A
    return H / s, D / s, A / s


def _poisson_grid(lh, la):
    """Conjunta independente P(x,y)=Pois(x;lh)·Pois(y;la) por jogo → (M,G+1,G+1)."""
    px = poisson.pmf(_GG[None, :], lh[:, None])
    py = poisson.pmf(_GG[None, :], la[:, None])
    return px[:, :, None] * py[:, None, :]


# ── Dixon-Coles (1997): correção de dependência em placares baixos ───────────
def dc_rho(lh, la, x, y):
    """ρ do Dixon-Coles por verossimilhança de PERFIL (λ fixos do GLM): só os 4
    placares baixos {(0,0),(0,1),(1,0),(1,1)} dependem de ρ via τ; o resto
    contribui log 1. Limitado a um range seguro p/ manter τ>0."""
    x = np.asarray(x); y = np.asarray(y)
    m00 = (x == 0) & (y == 0); m01 = (x == 0) & (y == 1)
    m10 = (x == 1) & (y == 0); m11 = (x == 1) & (y == 1)

    def negll(rho):
        t = np.ones(len(x))
        t[m00] = 1.0 - lh[m00] * la[m00] * rho
        t[m01] = 1.0 + lh[m01] * rho
        t[m10] = 1.0 + la[m10] * rho
        t[m11] = 1.0 - rho
        return -np.log(np.clip(t, 1e-9, None)).sum()
    return float(minimize_scalar(negll, bounds=(-0.3, 0.3), method="bounded").x)


def dc_probs(lh, la, rho):
    """(pH,pD,pA) por jogo sob Dixon-Coles: Poisson + τ(ρ) nos 4 placares baixos.
    ρ=0 recupera exatamente o Poisson independente (âncora da bateria na grade)."""
    joint = _poisson_grid(lh, la)
    joint[:, 0, 0] *= np.clip(1.0 - lh * la * rho, 1e-9, None)
    joint[:, 0, 1] *= np.clip(1.0 + lh * rho, 1e-9, None)
    joint[:, 1, 0] *= np.clip(1.0 + la * rho, 1e-9, None)
    joint[:, 1, 1] *= np.clip(1.0 - rho, 1e-9, None)
    return _result_probs(joint)


# ── Bradley-Terry-Davidson (1970): forças + empate, comparação pareada ───────
def btd_probs(g, ridge=1e-3):
    """Ajusta o modelo de Davidson (Bradley-Terry com empates + mando) por MLE e
    devolve (pH,pD,pA) por jogo. Forças θ por time (soma-zero via time-referência),
    vantagem de casa log α e parâmetro de empate log ν:
        pH ∝ exp(α+θ_i), pA ∝ exp(θ_j), pD ∝ exp(ν+(α+θ_i+θ_j)/2).
    Família totalmente distinta dos modelos de gols/probit. None se falhar."""
    teams = sorted(set(g.HomeTeam) | set(g.AwayTeam))
    idx = {t: k for k, t in enumerate(teams)}
    n = len(teams)
    hi = g.HomeTeam.map(idx).to_numpy(); aj = g.AwayTeam.map(idx).to_numpy()
    res = g.FTResult.map({"H": 0, "D": 1, "A": 2}).to_numpy()

    def probs(w):
        th = np.concatenate([[0.0], w[:n - 1]])      # time 0 = referência (soma-zero)
        la, lv = w[n - 1], w[n]                       # logα (mando), logν (empate)
        ti = th[hi]; tj = th[aj]
        eh = np.exp(la + ti); ea = np.exp(tj)
        ed = np.exp(lv + 0.5 * (la + ti + tj))
        Z = eh + ea + ed
        return np.vstack([eh / Z, ed / Z, ea / Z]).T, th

    def negll(w):
        p, th = probs(w)
        ll = np.log(np.clip(p[np.arange(len(res)), res], 1e-12, None)).sum()
        return -ll + ridge * float(th @ th)           # ridge p/ identificabilidade
    w0 = np.zeros(n + 1); w0[n - 1] = 0.3             # logα inicial razoável
    try:
        sol = minimize(negll, w0, method="L-BFGS-B")
    except Exception:
        return None
    p, _ = probs(sol.x)
    return p[:, 0], p[:, 1], p[:, 2]


# ── bateria ──────────────────────────────────────────────────────────────────
def _pfav(pH, pD, pA):
    return np.clip(np.vstack([pH, pD, pA]).T.max(1), 1e-6, 1 - 1e-6)


def battery_table(df, min_games=150, min_teams=8):
    """Skewness do favorito por liga-temporada sob CADA modelo da bateria vs
    empírico. Requer add_exante (p_fav_dv, o_fav) e coluna `season`. Descarta
    ajustes degenerados (separação) via goals.degenerate_fit: nos geradores de
    gols a degeneração vem do λ compartilhado ⇒ a liga-temporada inteira sai."""
    rows = []
    for (lg, yr), g in df.groupby(["Division", "season"]):
        if len(g) < min_games or g.HomeTeam.nunique() < min_teams:
            continue
        rates = goals.fit_rates(g)
        if rates is None:
            continue
        lh, la = rates
        x = g.FTHome.astype(int).to_numpy(); y = g.FTAway.astype(int).to_numpy()
        pfe = g.p_fav_dv.values
        if goals.degenerate_fit(_pfav(*dc_probs(lh, la, 0.0)), pfe):
            continue                                  # λ degenerado (ex.: JAP 2017)
        gens = {
            "poisson": dc_probs(lh, la, 0.0),
            "dixoncoles": dc_probs(lh, la, dc_rho(lh, la, x, y)),
        }
        btd = btd_probs(g)
        if btd is not None and not goals.degenerate_fit(_pfav(*btd), pfe):
            gens["btd"] = btd
        row = {"Division": lg, "season": int(yr), "n": len(g),
               "skew_emp": exante.pooled_skew(pfe, g.o_fav.values)["skew"],
               "pfav_emp": float(pfe.mean())}
        for name, (pH, pD, pA) in gens.items():
            pf = _pfav(pH, pD, pA)
            row[f"skew_{name}"] = exante.pooled_skew(pf, 1.0 / pf)["skew"]
            row[f"pfav_{name}"] = float(pf.mean())
        rows.append(row)
    return pd.DataFrame(rows)


def by_league(tab, models=MODELS):
    """Agrega liga-temporada → liga (médias) p/ skew e pfav de cada modelo + emp."""
    agg = {"n": ("n", "sum"), "seasons": ("season", "nunique"),
           "skew_emp": ("skew_emp", "mean"), "pfav_emp": ("pfav_emp", "mean")}
    for m in models:
        if f"skew_{m}" in tab:
            agg[f"skew_{m}"] = (f"skew_{m}", "mean")
            agg[f"pfav_{m}"] = (f"pfav_{m}", "mean")
    return tab.groupby("Division").agg(**agg).reset_index()


def elo_by_league(df):
    """4ª família — gerador ODDS-FREE: forças por Elo de RESULTADOS (sem gols nem
    odds, passo cronológico multi-liga) → mapa ordinal rating-diff→(pH,pD,pA) por
    MNLogit calibrado nos resultados (W2/P2) → skewness do favorito por liga. Como
    o Elo é um único modelo global, agregamos as probabilidades por jogo dentro de
    cada liga (não há refit por liga-temporada)."""
    from . import elo
    d = elo.with_elo(df)
    rows = []
    for lg, g in d.groupby("Division"):
        pf = np.clip(g[["pH_elo", "pD_elo", "pA_elo"]].to_numpy(float).max(1),
                     1e-6, 1 - 1e-6)
        rows.append({"Division": lg, "n": len(g),
                     "skew_elo": exante.pooled_skew(pf, 1.0 / pf)["skew"],
                     "pfav_elo": float(pf.mean())})
    return pd.DataFrame(rows)
