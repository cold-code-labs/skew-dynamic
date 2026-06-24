"""Configuração central. Ajuste DATA_PATH para o seu dump de dados."""
from pathlib import Path

DATA_PATH = Path("data/matches.csv")   # aponte para o seu dump completo
OUTDIR    = Path("outputs")
YEAR_MIN  = 2005      # cobertura de odds ~100% a partir daqui
WINDOW    = 1000      # jogos por janela deslizante
STEP      = 250       # passo (use STEP=WINDOW p/ janelas não-sobrepostas)
MIN_ODD   = 1.01      # filtro de odds inválidas (dado sujo)
BOOT_B    = 2000      # reamostras do bootstrap
SEED      = 42
FIG_DPI   = 300       # resolução das figuras (mín. RSOS p/ raster = 300 dpi)

DEVIG_METHOD = "shin"  # de-vigging primário: shin | multiplicative | power
