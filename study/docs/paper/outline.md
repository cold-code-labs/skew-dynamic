# Paper — outline (consolidated, post W1–W5)

**Working title:** *Structural Invariance of Return Skewness in Football
Betting Markets*
**Target:** Royal Society Open Science (backup: Physica A / PLOS ONE)

1. **Introduction** — preference for skewness (Golec-Tamarkin), FLB
   (Snowberg-Wolfers); the temporal/structural gap; our invariance thesis.
2. **Data** — normalised football-data, frozen by hash; ≥2005; 1X2 + O/U.
3. **The object** — ex-ante de-vigged skewness; Bernoulli identity
   `(1−2p)/√(p(1−p))`; Shin de-vig; cumulant decomposition (law of total cumulants).
4. **Results**
   4.1 *Mechanical core* (W1) — ex-ante≈ex-post; M₃ +102.6% within-match.
   4.2 *Structural law* (W2) — skewness ~ **odds-free** competitiveness (Elo);
       corr(elo, odds)=0.909 → odds read off the structure.
   4.3 *Temporal invariance* (W3) — panel with no trend (β≈0), ICC 0.70;
       COVID vignette as natural experiment.
   4.4 *Margin orthogonality* (W4) — overround collapses, skewness does not.
   4.5 *Binary market* (W5) — over/under 2.5 confirms the identity beyond 1X2.
5. **Mechanism** — tail cancellation; competitiveness as a slow property
   → temporal invariance.
6. **Robustness** — de-vig (mult/power/shin), window/overlap, sampling-SE,
   stationarity (ADF/KPSS), i.i.d. (VR, AR(1)), forensics of the blip.
7. **Discussion** — risk asymmetry inherited from the sport; 20-year
   structural efficiency; contrast with financial gain-loss asymmetry.
8. **Conclusion.**

**Figures (script `analysis/12_figures.py`):**
- F1: FLB — skew (ex-ante & ex-post) vs p_fav (identity curve).
- F2: skewness by league vs odds-free competitiveness (Elo) — the law.
- F3: M₃ decomposition (within/cov/between) — bar.
- F4: league×season panel — no trend (skewness vs year, FE).
- F5: derived law — leagues on the ordered-probit curve (P3).
