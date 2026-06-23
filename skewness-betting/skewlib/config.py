"""Configuração central. Ajuste DATA_PATH para o dado completo na sua infra."""
from pathlib import Path

DATA_PATH = Path("data/matches.csv")   # trocar pelo dump completo no ymir
OUTDIR    = Path("outputs")
YEAR_MIN  = 2005      # cobertura de odds ~100% a partir daqui
WINDOW    = 1000      # jogos por janela deslizante
STEP      = 250       # passo (use STEP=WINDOW p/ janelas não-sobrepostas)
MIN_ODD   = 1.01      # filtro de odds inválidas (dado sujo)
BOOT_B    = 2000      # reamostras do bootstrap
SEED      = 42
