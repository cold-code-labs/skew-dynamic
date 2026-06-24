"""Central configuration. Set DATA_PATH to your data dump."""
from pathlib import Path

DATA_PATH = Path("data/matches.csv")   # point to your full dump
OUTDIR    = Path("outputs")
YEAR_MIN  = 2005      # odds coverage ~100% from here on
WINDOW    = 1000      # games per sliding window
STEP      = 250       # step (use STEP=WINDOW for non-overlapping windows)
MIN_ODD   = 1.01      # filter for invalid odds (dirty data)
BOOT_B    = 2000      # bootstrap resamples
SEED      = 42
FIG_DPI   = 300       # figure resolution (RSOS min. for raster = 300 dpi)

DEVIG_METHOD = "shin"  # primary de-vigging: shin | multiplicative | power
