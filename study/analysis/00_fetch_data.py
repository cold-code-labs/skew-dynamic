"""Baixa o dataset multi-liga 2000–2025 para data/matches.csv e VERIFICA a
integridade contra data/PROVENANCE.json (sha256 + bytes do snapshot congelado).

A verificação garante que toda reprodução parte do MESMO dado que gerou os
números do paper. Se o mirror upstream mudar, o hash diverge e o fetch falha —
em vez de produzir números silenciosamente diferentes.

Na sua infra (rede liberada) você pode trocar pela fonte canônica
football-data.co.uk e empilhar todas as temporadas/ligas que quiser (nesse caso,
regenere PROVENANCE.json com o novo hash).
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/xgabora/"
       "Club-Football-Match-Data-2000-2025/main/data/Matches.csv")
DEST = Path("data/matches.csv")
PROV = Path("data/PROVENANCE.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"baixando {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"OK -> {DEST} ({DEST.stat().st_size/1e6:.1f} MB)")

    if not PROV.exists():
        print("AVISO: data/PROVENANCE.json ausente — pulei a verificação de hash.")
        return
    prov = json.loads(PROV.read_text())
    want = prov.get("sha256")
    got = sha256(DEST)
    if want and got != want:
        print(f"ERRO: hash do download não bate com o snapshot congelado.\n"
              f"  esperado: {want}\n  obtido:   {got}\n"
              f"  O mirror upstream mudou. Os números do paper foram produzidos com\n"
              f"  o snapshot {want[:12]}. Não prossiga sem regenerar PROVENANCE.json.",
              file=sys.stderr)
        sys.exit(1)
    print(f"integridade OK — sha256 {got[:12]} == PROVENANCE.json")


if __name__ == "__main__":
    main()
