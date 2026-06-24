#!/usr/bin/env bash
# Generates the submission PDF (manuscript + line numbering + figure plates)
# from draft.md. Requires pandoc + tectonic (`brew install pandoc tectonic`).
# Fonts: Times New Roman (body, with Greek/≈) + Menlo (code, with Greek).
# Output: study/outputs/paper/submission.pdf
set -euo pipefail
cd "$(dirname "$0")/../.."                       # study/
OUT=outputs/paper; mkdir -p "$OUT"
BUILT="$OUT/_submission_built.md"

# 1) assemble the markdown: draft + PLATES appendix (existing figures, at the end)
python3 - "$BUILT" <<'PY'
import re, sys, pathlib
root = pathlib.Path(".")
draft = (root/"docs/paper/draft.md").read_text()
figs = (root/"docs/paper/FIGURES.md").read_text()
# map: figure no. -> file (from the table rows of FIGURES.md)
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
    # missing figures (external-data block not run) are simply omitted
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
