"""Frente C3 — Kelly / staking ótimo sob a estrutura de skewness/CPT. O que a
assimetria implica para o crescimento ótimo de banca?

Para uma aposta unitária no resultado de prob VERDADEIRA p a odd decimal o:
  retorno X = (o−1) c/ prob p, −1 c/ prob (1−p);  EV = p·o − 1.
A fração de Kelly maximiza E[log(1+f·X)]:
  f* = (p·o − 1)/(o − 1)   (clipada em [0,1]; 0 se EV≤0).
A taxa de crescimento ótima g* = p·log(1+f*(o−1)) + (1−p)·log(1−f*) e a
APROXIMAÇÃO de momentos g ≈ μ − σ²/2 + skew·σ³/3 mostram o PAPEL da skewness:
sob preços justos (o=1/p) todos têm EV 0 e f*=0; sob a margem real (o<1/p) o EV é
negativo e Kelly manda NÃO apostar — a estrutura não oferece crescimento. O termo
de skewness explica por que o apostador de azarão (skew +) tolera EV negativo:
a assimetria positiva ADICIONA à utilidade log/crescimento.
"""
import numpy as np


def kelly_fraction(p, o):
    """f* de Kelly (clipada em [0,1]); 0 quando o EV ≤ 0."""
    p = np.asarray(p, float); o = np.asarray(o, float)
    b = o - 1.0
    f = (p * o - 1.0) / b
    return np.clip(f, 0.0, 1.0)


def growth_rate(p, o, f):
    """Taxa de crescimento log esperada de apostar a fração f."""
    p = np.asarray(p, float); o = np.asarray(o, float); f = np.asarray(f, float)
    win = np.log1p(f * (o - 1.0))
    lose = np.log1p(-f)
    return p * win + (1 - p) * lose


def moment_growth_terms(p, o, f):
    """Decomposição de momentos de g(f) ≈ f·μ − f²σ²/2 + f³·m₃/3 (Taylor de
    E[log(1+fX)]): isola a contribuição da SKEWNESS ao crescimento."""
    p = np.asarray(p, float); o = np.asarray(o, float); f = np.asarray(f, float)
    mu = p * o - 1.0
    s2 = p * (1 - p) * o ** 2
    m3 = p * (1 - p) * (1 - 2 * p) * o ** 3
    return {"mean": f * mu, "var": -0.5 * f ** 2 * s2, "skew": (f ** 3) * m3 / 3.0}


def fair_odds(p):
    return 1.0 / np.asarray(p, float)
