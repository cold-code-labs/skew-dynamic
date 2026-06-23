# Paper — outline (consolidado, pós W1–W5)

**Título de trabalho:** *Structural Invariance of Return Skewness in Football
Betting Markets*
**Alvo:** Royal Society Open Science (backup: Physica A / PLOS ONE)

1. **Introduction** — preferência por skewness (Golec-Tamarkin), FLB
   (Snowberg-Wolfers); a lacuna temporal/estrutural; nossa tese do invariante.
2. **Data** — football-data normalizado, congelado por hash; ≥2005; 1X2 + O/U.
3. **The object** — skewness ex-ante de-vigada; identidade de Bernoulli
   `(1−2p)/√(p(1−p))`; de-vig de Shin; decomposição por cumulantes totais.
4. **Results**
   4.1 *Mechanical core* (W1) — ex-ante≈ex-post; M₃ +102,6% intra-jogo.
   4.2 *Structural law* (W2) — skewness ~ competitividade **odds-free** (Elo);
       corr(elo, odds)=0,909 → odds leem a estrutura.
   4.3 *Temporal invariance* (W3) — painel sem tendência (β≈0), ICC 0,70;
       vinheta COVID como experimento natural.
   4.4 *Margin orthogonality* (W4) — overround colapsa, skewness não.
   4.5 *Binary market* (W5) — over/under 2.5 confirma a identidade fora do 1X2.
5. **Mechanism** — cancelamento de caudas; competitividade como propriedade
   lenta → invariância temporal.
6. **Robustness** — de-vig (mult/power/shin), janela/overlap, sampling-SE,
   estacionariedade (ADF/KPSS), i.i.d. (VR, AR(1)), forense do blip.
7. **Discussion** — assimetria de risco herdada do esporte; eficiência
   estrutural de 20 anos; contraste com gain-loss asymmetry financeira.
8. **Conclusion.**

**Figuras (script `analysis/12_figures.py`):**
- F1: FLB — skew (ex-ante & ex-post) vs p_fav (curva da identidade).
- F2: skewness por liga vs competitividade odds-free (Elo) — a lei.
- F3: decomposição de M₃ (within/cov/between) — barra.
- F4: painel liga×temporada — sem tendência (skewness vs ano, FE).
- F5: lei derivada — ligas na curva ordered-probit (P3).
