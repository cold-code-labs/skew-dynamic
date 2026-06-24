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

## ✅ Resolved (manual steps, now done)

| Requirement | What was done |
|---|---|
| **ORCID** | Registered: `0009-0008-3522-1694`, set in `CITATION.cff`, `.zenodo.json`, and the draft author line |
| **Zenodo DOI** | Release cut and archived; concept DOI `10.5281/zenodo.20822121` (resolves to latest, currently v1.0.2) in the draft's Data Accessibility and `CITATION.cff`; verified to resolve |
| **Cover letter** | `docs/paper/cover-letter.md` — scope fit, restricted-raw-data justification, equivalence + external-validity highlights, four real suggested reviewers |
| **Figures ≥300 DPI** | Centralized to `skewlib/config.py:FIG_DPI=300`; all `savefig` calls reference it; pranchas regenerated at 1800×1200 @ 300 DPI; drift audit clean |
| **Reference completeness** | Last unverified entry (Andrikogiannopoulou & Papakonstantinou) resolved to the published version: *Rev. Financial Studies* 33(8):3674–3718 (2020) |

## ✅ Substantive items (raised in review, now in the manuscript)

- **Temporal-null equivalence** — §4.3 / Figure 20: TOST against a pre-registered
  margin (½ between-league SD); every interval inside the band → *evidence of absence*.
- **External validity** — §4.9 / Figure 19: the same law reappears in tennis and
  basketball (independent odds sources) via the sport-agnostic canonical layer.

## 🟡 Remaining (revision-stage / portal; not initial-submission blockers)

- **Vancouver references + DOIs**: numbered-style conversion is a final-stage copy-edit
  (RSOS initial submission is format-free).
- **Portal mechanics (ScholarOne)**: subject category, separate high-res figure files,
  lay summary (`docs/paper/lay-summary.md`) and cover letter uploaded separately;
  confirm correspondence email.
