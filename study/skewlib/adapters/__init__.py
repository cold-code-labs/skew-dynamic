"""Adaptadores de fonte → tabela CANÔNICA (ver docs/DATA-SCHEMA.md).

Cada adaptador mapeia um dataset bruto de um esporte/mercado para o contrato
canônico e declara sua taxonomia de resultados. O núcleo (`skewlib.canonical` +
`skewlib.skewmeter`) é sport-agnóstico e nunca muda. Adicionar um esporte =
escrever um módulo aqui e registrá-lo em REGISTRY.
"""
from . import football, tennis, basketball

REGISTRY = {
    "football:1x2": football,            # 3 resultados (H/D/A)
    "football:ou25": football.OU,        # 2 resultados (over/under 2.5)
    "tennis:match_odds": tennis,         # 2 resultados (winner/loser), sem empate
    "basketball:moneyline": basketball,  # 2 resultados (casa/visitante), sem empate
}


def get(name):
    """Adaptador por nome 'sport:market' (ex.: 'football:1x2')."""
    if name not in REGISTRY:
        raise KeyError(f"adaptador desconhecido: {name}. Disponíveis: {list(REGISTRY)}")
    return REGISTRY[name]
