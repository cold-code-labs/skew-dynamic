# RSOS submission readiness

Tracking of Royal Society Open Science requirements (data/code availability is a
*condition of publication*) against this repository. Policy refs: RSOS "Information
for authors", Royal Society data-sharing & open-data policy, author guidelines.

## ✅ Resolved (this round)

| # | Requirement | What was done |
|---|---|---|
| 1 | One-command full reproduction | `run.sh` now runs **all** blocks incl. `46_bettype` and `export_site_data.py` (were orphaned), then the lineage drift audit |
| 2 | Pinned, deterministic environment | `requirements.txt` pinned to `==`; full transitive `requirements.lock`; `.python-version` (3.14); all RNG seeds fixed |
| 3 | Data integrity on fetch | `00_fetch_data.py` verifies the download SHA256 against `data/PROVENANCE.json` and aborts on drift |
| 4 | Public derived data + data dictionary | Derived tables (`outputs/*.csv`) and figures now **tracked** in git (raw file stays restricted); `outputs/README.md` documents every file and column with units |
| 5 | Mandatory declarations | Draft now has **Declarations**: ethics, data accessibility, code accessibility, competing interests, funding, CRediT author contributions, AI-use disclosure |
| 6 | Claim → figure → script traceability | `docs/paper/FIGURES.md` crosswalks each manuscript figure to its script, output file, and lineage phase |
| 7 | DOI deposit prepared | `.zenodo.json` metadata so a GitHub release auto-archives to Zenodo with a DOI; `CITATION.cff` carries DOI/ORCID slots |
| 8 | Abstract length | Trimmed to **197 words** (RSOS ≤ 200) with all headline numbers preserved |
| 9 | Continuous verification | `.github/workflows/ci.yml` runs engine import smoke + `/measure` API tests on push/PR |
| 10 | Reference completeness | Fixed the one entry missing a year; flagged author-date → Vancouver as a final copy-edit |

## 🔒 Manual steps (need the author; cannot be automated)

| Requirement | Action |
|---|---|
| **ORCID** | Register at orcid.org; replace `0000-0000-0000-0000` in `CITATION.cff`, `.zenodo.json`, and the draft author line |
| **Zenodo DOI** | Enable the Zenodo–GitHub integration for the repo, cut a release; replace `10.5281/zenodo.XXXXXXX` in the draft's Data Accessibility and `CITATION.cff` with the minted DOI |
| **Cover letter** | One-pager noting scope fit and the restricted-raw-data justification (derived data deposited; raw fetched + hash-verified) |

## 🟡 Recommended before submission (not blockers)

- **Figures**: currently PNG at 150 DPI. RSOS accepts PNG but prefers high-res/vector — emit PDF/EPS or bump to ≥300 DPI (one change in the matplotlib `savefig` calls).
- **Vancouver references + DOIs**: full numbered-style conversion is a final-stage copy-edit (initial submission is format-free).

## 🔬 Substantive item (separate from infra; raised in review)

- **Temporal-null equivalence**: the "no trend" claim is currently *absence of
  evidence*. Apply the existing TOST/equivalence machinery to the temporal null to
  state *evidence of absence* within a pre-set margin. New analysis + a number for §4.3.
- **External validity**: single sport / single source. The planned multi-sport
  modularization (canonical data schema) is the highest-leverage de-risking and
  doubles as the project's next expansion.
