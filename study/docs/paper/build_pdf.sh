#!/usr/bin/env bash
# Gera o PDF de submissão (manuscrito + numeração de linhas + pranchas de figuras)
# a partir do draft.md. Requer pandoc + tectonic (`brew install pandoc tectonic`).
# Fontes: Times New Roman (corpo, com Grego/≈) + Menlo (código, com Grego).
# Saída: study/outputs/paper/submission.pdf
set -euo pipefail
cd "$(dirname "$0")/../.."                       # study/
OUT=outputs/paper; mkdir -p "$OUT"
BUILT="$OUT/_submission_built.md"

# 1) monta o markdown: draft + apêndice de PRANCHAS (figuras existentes, ao final)
python3 - "$BUILT" <<'PY'
import re, sys, pathlib
root = pathlib.Path(".")
draft = (root/"docs/paper/draft.md").read_text()
figs = (root/"docs/paper/FIGURES.md").read_text()
# mapa: nº da figura -> arquivo (das linhas da tabela do FIGURES.md)
rows = re.findall(r"\*\*Figure (\d+)\*\*[^|]*\|\s*`([^`]+\.png)`", figs)
plates = ["\n\n\\newpage\n\n# Figure plates\n",
          "*Figures are listed with full captions in the Figures section above; "
          "the plates follow here, one per page.*\n"]
have = []
for n, fn in sorted(rows, key=lambda r: int(r[0])):
    p = root/"outputs/fig"/fn
    if p.exists():
        plates.append(f"\n\\newpage\n\n![]({fn}){{width=92%}}\n\n**Figure {n}.**\n")
        have.append(n)
    # figuras ausentes (bloco de dado externo não rodado) são simplesmente omitidas
(root/sys.argv[1].split('/',2)[-1] if False else pathlib.Path(sys.argv[1])).write_text(
    draft + "".join(plates))
print(f"plates embedded: {len(have)} (figs {', '.join(have)})", file=sys.stderr)
PY

# 2) pandoc -> PDF (tectonic)
pandoc "$BUILT" \
  -o "$OUT/submission.pdf" \
  --pdf-engine=tectonic \
  --resource-path=.:outputs/fig \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  -V linestretch=1.3 \
  -V mainfont="Times New Roman" \
  -V monofont="Menlo" \
  -V colorlinks=true \
  -H docs/paper/_pandoc_header.tex \
  2>&1 | grep -iE "could not represent|error:" | sort | uniq -c || true

rm -f "$BUILT"
echo "-> $OUT/submission.pdf"
