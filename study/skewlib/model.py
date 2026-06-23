"""Derivação formal: skewness = f(dispersão de força) via ordered-probit.

Template de Goddard-Asimakopoulos (2004) / Koning (2000): a força de cada time
r ~ N(0, σ_L²); num jogo a diferença d = r_i − r_j ~ N(0, 2σ_L²). A margem
latente y* = d + h + ε (ε~N(0,1), h = vantagem de casa) gera (A,D,H) por cutoffs
±c:
    P(A)=Φ(−c−μ),  P(H)=1−Φ(c−μ),  P(D)=Φ(c−μ)−Φ(−c−μ),   μ = d + h.
O favorito tem prob p = max(P_H,P_D,P_A). Sob odds JUSTAS (o=1/p) o favorito tem
média zero, então a skewness AGRUPADA da liga é
    S(σ_L) = E[m₃(p)] / E[σ²(p)]^{3/2},  com σ²=(1−p)/p, m₃=(1−p)(1−2p)/p²,
onde a esperança é sobre p = p_fav(d), d ~ N(0, 2σ_L²). σ_L é a competitividade:
pequeno = parelho.

Frente E (endurecimento da derivação) acrescenta duas peças:
  E1 — forma fechada: a esperança E[·] é um integral gaussiano 1-D em d, então
       `league_*_exact` o avalia por QUADRATURA (determinístico, sem ruído de MC),
       e `smallsigma_skew` dá a expansão analítica near-balance
       S(σ_L) = S₀ + S₂·σ_L² + O(σ_L⁴), com S₀ = (1−2p₀)/√(p₀(1−p₀)) a identidade
       no favorito balanceado p₀ = p_fav(0). (A curva NÃO é monótona: é côncava,
       com pico perto do equilíbrio e cruzando 0 quando o favorito fica forte.)
  E2 — robustez de força: `force_diff` troca N(0,σ²) por t-Student / skew-normal /
       uniforme. Como d = rᵢ − rⱼ é SIMÉTRICO p/ qualquer força iid, a assimetria
       da força não enviesa a lei; só a cauda (kurtose de d) pode mover — testável.
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import fsolve
from scipy.integrate import quad


def outcome_probs(d, h, c):
    mu = d + h
    cdf_hi = norm.cdf(c - mu); cdf_lo = norm.cdf(-c - mu)
    return 1 - cdf_hi, cdf_hi - cdf_lo, cdf_lo      # pH, pD, pA


def force_diff(sigma_L, n, seed, family="normal", nu=5.0, alpha=4.0):
    """Diferença de força d = rᵢ − rⱼ de um jogo, p/ várias famílias de força
    (Frente E2). Cada time tem força r de variância σ_L²; d tem variância 2σ_L².
    `normal` reproduz exatamente `np.random.default_rng(seed).normal(0,√2·σ,n)`
    (1 sorteio) — path congelado, bit-idêntico ao baseline. As demais sorteiam
    duas pernas (rᵢ, rⱼ) e diferenciam, então d é simétrico por construção:
      t        — força t-Student (cauda pesada), escalada p/ variância σ_L²;
      skewnormal[_neg] — força com assimetria ±α (skew-normal), variância σ_L²;
      uniform  — força uniforme, variância σ_L².
    """
    rng = np.random.default_rng(seed)
    s = float(sigma_L)
    if family == "normal":
        return rng.normal(0.0, np.sqrt(2.0) * s, n)
    if family == "t":
        scale = s * np.sqrt((nu - 2.0) / nu)          # Var(t_ν)=ν/(ν−2) → σ_L²
        return (rng.standard_t(nu, n) - rng.standard_t(nu, n)) * scale
    if family in ("skewnormal", "skewnormal_neg"):
        from scipy.stats import skewnorm
        a = alpha if family == "skewnormal" else -alpha
        delta = a / np.sqrt(1.0 + a * a)
        omega = s / np.sqrt(1.0 - 2.0 * delta * delta / np.pi)   # Var=σ_L²
        xi = -omega * delta * np.sqrt(2.0 / np.pi)               # média 0
        r1 = skewnorm.rvs(a, loc=xi, scale=omega, size=n, random_state=rng)
        r2 = skewnorm.rvs(a, loc=xi, scale=omega, size=n, random_state=rng)
        return r1 - r2
    if family == "uniform":
        hw = np.sqrt(3.0) * s                          # Var(U[-hw,hw])=hw²/3=σ_L²
        return rng.uniform(-hw, hw, n) - rng.uniform(-hw, hw, n)
    raise ValueError(f"família de força desconhecida: {family}")


def _d(sigma_L, n, seed, family="normal", **fkw):
    return force_diff(sigma_L, n, seed, family=family, **fkw)


def _pfav(d, h, c):
    pH, pD, pA = outcome_probs(d, h, c)
    return np.clip(np.maximum.reduce([pH, pD, pA]), 1e-6, 1 - 1e-6)


def marginals(sigma_L, h, c, n=200000, seed=1, family="normal", **fkw):
    d = _d(sigma_L, n, seed, family=family, **fkw)
    pH, pD, pA = outcome_probs(d, h, c)
    return {"home": float(pH.mean()), "draw": float(pD.mean()),
            "away": float(pA.mean()), "p_fav": float(_pfav(d, h, c).mean())}


def league_skew(sigma_L, h, c, n=200000, seed=1, family="normal", **fkw):
    """Skewness agrupada da liga sob odds justas — fechada em p (MC sobre d)."""
    p = _pfav(_d(sigma_L, n, seed, family=family, **fkw), h, c)
    s2 = (1 - p) / p
    m3 = (1 - p) * (1 - 2 * p) / p ** 2
    return float(m3.mean() / s2.mean() ** 1.5)


def _fair_central_moments(p, max_order=6):
    """Momentos centrais por jogo sob odds JUSTAS (o=1/p ⇒ média zero):
        m_k = (1-p)/p^(k-1) · [ (1-p)^(k-1) + (-1)^k · p^(k-1) ].
    Recupera s²=(1-p)/p e m₃=(1-p)(1-2p)/p² usados em `league_skew`."""
    p = np.asarray(p, float)
    return {k: (1 - p) / p ** (k - 1) * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1))
            for k in range(2, max_order + 1)}


# ── Frente E1 — forma fechada: o integral gaussiano, sem Monte Carlo ──────────
# E[g(p_fav(d))] = ∫ g(p_fav(d)) φ(d; 0, 2σ_L²) dd é um integral 1-D. p_fav(d) é
# contínua mas tem QUINAS onde o favorito troca (max de pH,pD,pA); avaliamos o
# integral por quadratura adaptativa, partindo nos pontos de troca → exato
# (determinístico) até a tolerância, recuperando `league_*` sem ruído de MC.

def _pfav_scalar(d, h, c):
    mu = d + h
    pH = 1.0 - norm.cdf(c - mu); pD = norm.cdf(c - mu) - norm.cdf(-c - mu)
    pA = norm.cdf(-c - mu)
    return min(max(max(pH, pD, pA), 1e-12), 1.0 - 1e-12)


def _fair_mk(p, k):
    """k-ésimo momento central por jogo sob odds justas (escalar)."""
    return (1 - p) / p ** (k - 1) * ((1 - p) ** (k - 1) + (-1) ** k * p ** (k - 1))


def fav_switch_points(h, c, span=14.0, ngrid=2801):
    """Valores de d onde o favorito (argmax de pH,pD,pA) troca de identidade —
    as quinas de p_fav(d). Usados como nós de partição na quadratura."""
    from scipy.optimize import brentq
    g = np.linspace(-span, span, ngrid)
    arg = np.vstack(outcome_probs(g, h, c)).argmax(0)
    pts = []
    for i in np.where(np.diff(arg) != 0)[0]:
        a, b = int(arg[i]), int(arg[i + 1])
        f = lambda d: outcome_probs(d, h, c)[a] - outcome_probs(d, h, c)[b]
        try:
            pts.append(float(brentq(f, g[i], g[i + 1])))
        except ValueError:
            pass
    return sorted(pts)


def mean_pfav_exact(sigma_L, h, c):
    """E[p_fav] exato (integral gaussiano), sem MC — competitividade observável."""
    tau = np.sqrt(2.0) * float(sigma_L)
    if tau < 1e-9:
        return _pfav_scalar(0.0, h, c)
    pts = [p for p in fav_switch_points(h, c) if abs(p) < 8 * tau]
    val, _ = quad(lambda d: _pfav_scalar(d, h, c) * norm.pdf(d, 0.0, tau),
                  -8 * tau, 8 * tau, points=pts, limit=200)
    return float(val)


def league_moments_exact(sigma_L, h, c, max_order=6):
    """Momentos PADRONIZADOS da liga por QUADRATURA do integral gaussiano em d —
    versão exata (sem ruído de MC) de `league_moments`. Forma fechada de S(σ_L)
    no sentido do integral avaliado à precisão da máquina."""
    tau = np.sqrt(2.0) * float(sigma_L)
    if tau < 1e-9:                                   # liga degenerada: p₀ único
        p0 = _pfav_scalar(0.0, h, c)
        M = {k: _fair_mk(p0, k) for k in range(2, max_order + 1)}
    else:
        pts = [p for p in fav_switch_points(h, c) if abs(p) < 8 * tau]
        def Ek(k):
            v, _ = quad(lambda d: _fair_mk(_pfav_scalar(d, h, c), k)
                        * norm.pdf(d, 0.0, tau), -8 * tau, 8 * tau,
                        points=pts, limit=200)
            return v
        M = {k: Ek(k) for k in range(2, max_order + 1)}
    M2 = M[2]
    res = {"var": M2}
    if max_order >= 3: res["skew"] = M[3] / M2 ** 1.5
    if max_order >= 4: res["exkurt"] = M[4] / M2 ** 2 - 3.0
    if max_order >= 5: res["std5"] = M[5] / M2 ** 2.5
    if max_order >= 6: res["std6"] = M[6] / M2 ** 3
    return res


def league_skew_exact(sigma_L, h, c):
    """Skewness exata da liga (quadratura). Substitui o MC de `league_skew`."""
    return float(league_moments_exact(sigma_L, h, c, max_order=3)["skew"])


def smallsigma_coeffs(h, c):
    """Coeficientes da expansão analítica near-balance de S(σ_L):
        S(σ_L) = S₀ + S₂·σ_L² + O(σ_L⁴).
    Em torno de σ_L→0, d→0 e p_fav é o ramo liso do favorito de equilíbrio, com
    p₀=p_fav(0), p₁=p_fav'(0), p₂=p_fav''(0). Pela expansão de Taylor + simetria
    de d (termo ímpar zera), para qualquer g(p):  E[g] = g(p₀) + σ_L²·[g''(p₀)p₁²
    + g'(p₀)p₂] + O(σ_L⁴) (pois Var(d)=2σ_L²). Aplicando a σ²(p)=(1−p)/p e
    m₃(p)=(1−p)(1−2p)/p²:
        S₀ = m₃(p₀)/σ²(p₀)^{3/2} = (1−2p₀)/√(p₀(1−p₀))      (identidade por jogo)
        S₂ = B₂/A₀^{3/2} − (3/2)·B₀·A₂/A₀^{5/2}.
    No ramo do mandante (favorito = casa), p₀=Φ(h−c), p₁=φ(h−c), p₂=−(h−c)φ(h−c)
    em forma fechada; usamos diferenças centrais p/ valer em qualquer ramo."""
    eps = 1e-3
    f = lambda d: _pfav_scalar(d, h, c)
    p0 = f(0.0)
    p1 = (f(eps) - f(-eps)) / (2 * eps)
    p2 = (f(eps) - 2 * p0 + f(-eps)) / eps ** 2
    A0 = (1 - p0) / p0                                   # σ²(p₀)
    A2 = (2 / p0 ** 3) * p1 ** 2 + (-1 / p0 ** 2) * p2   # g=σ²: g''=2/p³, g'=−1/p²
    B0 = (1 - p0) * (1 - 2 * p0) / p0 ** 2               # m₃(p₀)
    m3p = -2 / p0 ** 3 + 3 / p0 ** 2                     # m₃'(p)
    m3pp = 6 / p0 ** 4 - 6 / p0 ** 3                     # m₃''(p)
    B2 = m3pp * p1 ** 2 + m3p * p2
    S0 = B0 / A0 ** 1.5
    S2 = B2 / A0 ** 1.5 - 1.5 * B0 * A2 / A0 ** 2.5
    return {"S0": float(S0), "S2": float(S2), "p0": float(p0),
            "p1": float(p1), "p2": float(p2)}


def smallsigma_skew(sigma_L, h, c):
    """Expansão analítica S₀ + S₂·σ_L² (forma fechada near-balance)."""
    cf = smallsigma_coeffs(h, c)
    s = np.asarray(sigma_L, float)
    return cf["S0"] + cf["S2"] * s ** 2


def league_moments(sigma_L, h, c, n=200000, seed=1, max_order=6, family="normal", **fkw):
    """Momentos PADRONIZADOS da liga sob odds justas — var/skew/kurtose/etc.
    fechados na distribuição de p_fav. Como todas as apostas têm média zero, não
    há termo entre-jogos: M_k = E[m_k(p)]. Generaliza `league_skew` (ordem 3) e
    permite prever a FORMA inteira (não só o 3º momento) a partir de σ_L."""
    p = _pfav(_d(sigma_L, n, seed, family=family, **fkw), h, c)
    m = _fair_central_moments(p, max_order)
    M2 = float(m[2].mean())
    res = {"var": M2}
    if max_order >= 3: res["skew"] = float(m[3].mean() / M2 ** 1.5)
    if max_order >= 4: res["exkurt"] = float(m[4].mean() / M2 ** 2 - 3.0)
    if max_order >= 5: res["std5"] = float(m[5].mean() / M2 ** 2.5)
    if max_order >= 6: res["std6"] = float(m[6].mean() / M2 ** 3)
    return res


def calibrate(home=0.444, draw=0.264, pfav=0.499, n=200000):
    """Resolve (h, c, σ_ref) para casar as taxas marginais médias observadas."""
    def eqs(x):
        h, c, s = x
        m = marginals(abs(s), h, abs(c), n=n, seed=7)
        return [m["home"] - home, m["draw"] - draw, m["p_fav"] - pfav]
    h, c, s = fsolve(eqs, [0.2, 0.5, 0.4])
    return {"h": float(h), "c": float(abs(c)), "sigma_ref": float(abs(s))}


def calibrate_by_league(df, n=120000, min_n=3000):
    """Calibra (h, c, σ_L) POR liga a partir das taxas marginais da própria liga
    (Frente E3): vantagem de casa, cutoff de empate e dispersão de força endógenos.
    Requer add_exante (p_fav_dv). Devolve DataFrame por liga + skew prevista pelo
    modelo da própria liga vs observada."""
    import pandas as pd
    rows = []
    for lg, g in df.groupby("Division"):
        if len(g) < min_n:
            continue
        home = float((g.FTResult == "H").mean())
        draw = float((g.FTResult == "D").mean())
        pfav = float(g.p_fav_dv.mean())
        try:
            par = calibrate(home=home, draw=draw, pfav=pfav, n=n)
        except Exception:
            continue
        sk_model = league_skew(par["sigma_ref"], par["h"], par["c"], n=n, seed=5)
        rows.append({"Division": lg, "n": len(g), "home": home, "draw": draw,
                     "p_fav": pfav, "h": par["h"], "c": par["c"],
                     "sigma_L": par["sigma_ref"], "skew_model": sk_model})
    return pd.DataFrame(rows)


def curve(h, c, sigmas, n=200000, seed=3):
    """Traça (mean p_fav, skewness) ao longo de uma grade de σ_L."""
    pf, sk = [], []
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        sk.append(league_skew(s, h, c, n=n, seed=seed))
    return np.array(pf), np.array(sk)


def curve_exact(h, c, sigmas):
    """(mean p_fav, skewness) EXATOS por quadratura ao longo da grade de σ_L —
    a curva teórica sem ruído de MC (Frente E1). Substitui `curve` p/ a figura."""
    pf = np.array([mean_pfav_exact(s, h, c) for s in sigmas])
    sk = np.array([league_skew_exact(s, h, c) for s in sigmas])
    return pf, sk


def curve_family(h, c, sigmas, family="normal", n=200000, seed=3, **fkw):
    """(mean p_fav, skewness) por família de força (Frente E2) — MC, pois t/
    skew-normal/uniforme não têm o integral fechado do caso gaussiano. Permite
    reparametrizar a lei pela competitividade OBSERVÁVEL (p_fav) e ver se a curva
    skew×p_fav sobrevive à troca da distribuição de força."""
    pf, sk = [], []
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed, family=family, **fkw)["p_fav"])
        sk.append(league_skew(s, h, c, n=n, seed=seed, family=family, **fkw))
    return np.array(pf), np.array(sk)


def curve_moments(h, c, sigmas, n=200000, seed=3, max_order=6):
    """Traça (mean p_fav, {var, skew, exkurt, ...}) ao longo da grade de σ_L —
    a curva teórica de CADA momento, p/ prever a forma de cada liga pelo p_fav."""
    keys = ["var", "skew", "exkurt", "std5", "std6"][: max_order - 1]
    pf = []; mom = {k: [] for k in keys}
    for s in sigmas:
        pf.append(marginals(s, h, c, n=n, seed=seed)["p_fav"])
        lm = league_moments(s, h, c, n=n, seed=seed, max_order=max_order)
        for k in keys:
            mom[k].append(lm[k])
    return np.array(pf), {k: np.array(v) for k, v in mom.items()}
