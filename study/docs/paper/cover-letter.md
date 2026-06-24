# Cover letter — Royal Society Open Science

*Draft. Replace ‹…› placeholders and verify reviewer affiliations before submission.*

Date: ‹submission date›

To the Editors, *Royal Society Open Science*

Dear Editors,

I am pleased to submit the research article **"Structural Invariance of Return
Skewness in Football Betting Markets"** for consideration as a research article in
*Royal Society Open Science*.

**What the paper shows.** The favourite–longshot bias is usually read as a pricing
anomaly explained by a taste for skewness. We show instead that, viewed as the
skewness of the betting market's return distribution, the phenomenon is a *structural
invariant of the sport that prices faithfully transcribe*. Using 205,435 matches
across 38 leagues (2005–2025), a law-of-total-cumulants decomposition shows market
skewness is ≈100% the within-match Bernoulli asymmetry of the win-probability
distribution; its cross-league level is fixed by competitiveness — a relation that
survives an odds-free, results-only measure — and it shows no secular drift within the
modern regime.

**Why it is a good fit for RSOS.** The contribution is as much methodological and
evidential as substantive, and the journal's open-science model fits the work
exactly:

- **Reproducibility.** The entire pipeline regenerates every number, figure and an
  evidence ledger from a single command, under a pinned environment, with an automatic
  result-drift audit. Each headline number is pinned to the exact code version that
  produced it via versioned git "evidence" tags.
- **Strength of inference.** Beyond null-hypothesis tests, the central "no temporal
  drift" claim is established as a formal *equivalence* result (two one-sided tests
  against a pre-registered margin), turning a high *p*-value into positive evidence of
  stability — addressing the absence-of-evidence pitfall directly.
- **External validity.** The analysis is ported, unchanged, through a sport-agnostic
  data layer to two further sports with independent odds sources — tennis and
  basketball — where the same law reappears, identifying it as a property of
  competition rather than of football or the 1X2 contract.

**Open data and code.** All derived data, figures and analysis code are openly
available under Apache-2.0 and archived at Zenodo with a citable DOI
(10.5281/zenodo.20822121; concept DOI, all versions), version-controlled at
https://github.com/cold-code-labs/skew-dynamic. The underlying raw match-and-odds
files are sourced from third parties whose terms restrict redistribution; they are not
deposited but are regenerated deterministically by the pipeline and verified against
frozen content hashes, and the provided derived data are sufficient to replicate every
reported result.

**Declarations.** This study uses only publicly available aggregate match results and
bookmaker odds; it involves no human participants, personal data or animal subjects.
The author declares no competing interests and received no external funding. The use
of an AI coding assistant is disclosed in the manuscript; all methodological choices,
results and conclusions are the author's.

**Originality.** This manuscript is original, has not been published previously, and is
not under consideration at any other journal.

**Suggested reviewers** (independent of the author; please verify current
affiliations and contact details, and that none has a conflict, before submission):
- **Karl Whelan** (University College Dublin) — author of "The favourite–longshot bias
  in fixed-odds football betting" (*Economica*, 2024); directly on topic.
- **Erik Štrumbelj** (University of Ljubljana) — work on extracting probabilities from
  betting odds (de-vigging), central to our measurement.
- **Rob Fort** (University of Washington) — competitive-balance measurement in sports
  economics (the structural variable our law depends on).
- **László Csató** (HUN-REN SZTAKI / Corvinus) — long-run competitive-balance trends,
  the nearest analog to our temporal analysis.

*(I am a single, independent author at Cold Code Labs with no institutional
co-authors; I am not aware of conflicts with the above, but the editor should confirm.)*

I confirm I have read and can comply with the journal's editorial and open-data
policies. Thank you for considering this submission.

Yours sincerely,

Vitor Alves
Cold Code Labs
ORCID: 0009-0008-3522-1694
‹email›
