# LINEAGE — ledger de evidências (versionamento)

> Gerado por `analysis/build_lineage.py` (não editar à mão). Cada fase pina
> seu(s) número(s)-título à VERSÃO exata do código (commit + tag `evidence/*`)
> e ao DATASET (`sha256:6905ca5324df9528`, 205435 jogos,
> 38 ligas). Volte a qualquer estado com
> `git checkout <tag>`; audite mudança de resultado com `--check`.

**HEAD na geração:** `f22f163b`  ⚠️ working tree DIRTY

| Fase | Frente | Achado | Blocos | Figuras | Números-título | Commit | Tag |
|------|--------|--------|--------|---------|----------------|--------|-----|
| **P0** | Foundation | Congelamento + reprodução | 00_fetch_data, 01_baseline | — | n_matches=205435 · leagues=38 · years=2005-2025 | `d58840c` (2026-06-23) | `evidence/phase-0` |
| **W1** | Finding | Núcleo mecânico (skew ex-ante) | 07_devig_exante, 03_decomposition | f1, f3 | skew_exante=0.236 · skew_expost=0.23 · within_frac_m3=1.026 | `699f14c` (2026-06-23) | `evidence/W1` |
| **W2** | Mechanism | Lei sem odds (Elo) | 08_mechanism_elo | f2 | corr_skew_upset=0.826 · corr_elo_odds=0.909 | `730fda7` (2026-06-23) | `evidence/W2` |
| **W3** | Invariance | Invariância temporal (painel) | 09_panel_temporal | f4 | trend_beta_year=0.00015 · trend_p=0.73 · icc=0.7 | `c68eb69` (2026-06-23) | `evidence/W3` |
| **W5** | Robustness | Mercado binário O/U 2.5 | 10_overunder | — | skew_ou=-0.21 · within_frac=0.996 | `95d1a07` (2026-06-23) | `evidence/W5` |
| **W4** | Separation | Margem ortogonal + de-vig | 11_margin_robustness | — | overround_avg=1.067 · overround_best=1.009 | `16b8c2e` (2026-06-23) | `evidence/W4` |
| **P1** | Reframe | Invariância intra-regime | 13_regimes | — | breaks_38_leagues=1 · epl_breaks=0 | `f2bc443` (2026-06-23) | `evidence/P1` |
| **P2** | Hardening | Balanço da classificação (odds-free) | 14_balance_indices | — | corr_skew_nollscully=-0.625 | `7f00792` (2026-06-23) | `evidence/P2` |
| **P3** | Theory | Lei derivada (ordered-probit) | 15_model | f5 | model_r=0.904 · model_rmse=0.024 | `624547a` (2026-06-23) | `evidence/P3` |
| **P4** | Confound | FLB estável (Angelini) | 16_flb_stability | — | mean_abs_ante_post=0.015 | `2bcef94` (2026-06-23) | `evidence/P4` |
| **B1** | Shape | Invariância de FORMA (multi-momento) | 17_moments | f6 | model_r_var=0.987 · model_r_skew=0.904 · model_r_exkurt=0.89 | `6946fc6` (2026-06-23) | `evidence/frente-B` |
| **B2** | Collapse | Colapso de distribuição | 18_collapse | f7 | uncond_ks=0.474 · cond_ks=0.059 · drop=0.87 | `6946fc6` (2026-06-23) | `evidence/frente-B` |
| **C1** | Pricing | Sem prêmio além do FLB mecânico | 19_premium | f8 | ret=-0.0482 · vig=-0.0497 · flb=0.0015 · resid_skew_r=0.11 | `2b2d423` (2026-06-23) | `evidence/frente-C` |
| **C2** | Preference | CPT invariante (γ) | 20_cpt | f9 | gamma=0.958 · gamma_sd_season=0.02 · gamma_sd_league=0.04 · trend_beta=0.0003 | `2b2d423` (2026-06-23) | `evidence/frente-C` |
| **E1** | Theory | Forma fechada de S(σ_L) | 21_closed_form | f10 | max_mc_err=0.0015 · p0=0.4392 · S0=0.2449 · sigma_peak=0.1226 · league_r=0.903 | `a70b790` (2026-06-23) | `evidence/frente-E` |
| **E2** | Robustness | Robustez da distribuição de força | 22_force_robustness | f11 | max_dS_overall=0.032 · sd_between_leagues=0.0518 | `a70b790` (2026-06-23) | `evidence/frente-E` |
| **G1** | Reliability | De-vig confiável + invariância de método | 23_devig_reliability | f12 | rel_global=0.0 · rel_sd_league=0.0003 · skew_devig_range=0.039 | `a326910` (2026-06-23) | `evidence/frente-G` |
| **G2** | Robustness | Painel balanceado estrito (composição morta) | 24_balanced_panel | f13 | n_balanced=15 · beta_balanced=-0.00013 · delta20_balanced=-0.003 | `a326910` (2026-06-23) | `evidence/frente-G` |
| **G3** | Confidence | IC por block-bootstrap sobre temporadas | 25_block_bootstrap | — | skew_ci_lo=0.232 · skew_ci_hi=0.239 · corr_ci_lo=-0.922 · corr_ci_hi=-0.876 | `a326910` (2026-06-23) | `evidence/frente-G` |
| **D2** | Microstructure | Sharp vs soft (margem ortogonal na melhor odd) | 26_sharp_soft | f14 | d_skew_mean=0.02 · corr_soft_sharp=0.993 · corr_sharp_pfav=-0.876 | `4ccbc01` (2026-06-23) | `evidence/frente-D` |
| **D3** | Microstructure | z de Shin (dinheiro informado) como série | 27_shin_z_series | f15 | z_global=0.0343 · z_sd_league=0.0043 · corr_z_overround=0.999 | `4ccbc01` (2026-06-23) | `evidence/frente-D` |
| **D4** | Third market | Handicap asiático: identidade num 3º mercado | 28_asian_handicap | f16 | p_fav_ah=0.533 · skew_ah_global=-0.104 · within_frac_ah=1.027 · league_identity_r=0.8 | `4ccbc01` (2026-06-23) | `evidence/frente-D` |
| **F1** | Within-season | Sazonalidade intra-temporada (drift leve) | 29_intraseason | f17 | global_span=0.0149 · shift_mean=-0.0078 · shift_ci_lo=-0.0131 · shift_ci_hi=-0.0015 | `e5b04e1` (2026-06-23) | `evidence/frente-F` |
| **F2** | Tail cancellation | Contribuição ao M₃ por competitividade do jogo | 30_game_contribution | f18 | share_weak_fav=1.26 · share_strong_fav=-0.26 | `e5b04e1` (2026-06-23) | `evidence/frente-F` |
| **F3** | Team structure | Decomposição por time (dispersão de força) | 31_team_decomposition | f19 | corr_elo_teamskew=-0.444 · corr_elosd_leagueskew=-0.601 | `e5b04e1` (2026-06-23) | `evidence/frente-F` |
| **H2** | Open vs closed | Liga aberta vs fechada (MLS na lei) | 32_open_vs_closed | f20 | mls_p_fav=0.503 · mls_skew=0.162 · mls_pfav_rank=22 · mls_residual=-0.059 | `e0bc9fd` (2026-06-23) | `evidence/H2` |
| **C3** | Staking | Kelly/staking sob a estrutura de skewness | 33_kelly_staking | f21 | frac_positive_ev=0.0 · skew_term_dog=0.598 · skew_term_fav=0.01 | `e0bc9fd` (2026-06-23) | `evidence/C3` |
| **E3** | Theory | Calibração por liga (cutoff de empate endógeno) | 34_per_league_calibration | f22 | corr_sigma_pfav=0.874 · corr_c_draw=0.906 · skew_model_r=0.905 | `e0bc9fd` (2026-06-23) | `evidence/E3` |
| **I** | Cross-model | Validação cruzada do mecanismo (Poisson de gols) | 35_poisson_crossmodel | f23 | corr_pfav=0.972 · corr_skew=0.925 · league_r_poisson=0.85 · n_league_seasons=617 | `7a45759` (2026-06-23) | `evidence/frente-I` |
| **J** | Dynamic | Chegada de informação HT→FT (identidade dinâmica) | 36_inplay_resolution | f24 | skew_pregame=0.239 · skew_behind=2.084 · skew_ahead2=-3.908 · martingale_err=0.0035 | `74f9c2e` (2026-06-23) | `evidence/frente-J` |
| **K** | Diversification | Diversificação (skewness = fenômeno de aposta única) | 37_diversification | f25 | skew_single_fav=0.23 · skew_single_dog=2.254 · n_to_gaussian_dog=509 | `b4b90eb` (2026-06-23) | `evidence/frente-K` |
| **L** | Confound | Vantagem de casa secular vs invariância | 38_home_advantage | f26 | hfa_beta=-0.00133 · skew_beta=-9e-05 · corr_hfa_skew=-0.244 | `f22f163` (2026-06-23) | `evidence/frente-LMN` |
| **M** | Tail risk | Risco de cauda realizado das estratégias | 39_tail_risk | f27 | skew_fav=0.23 · skew_dog=2.254 · maxdd_fav=-9922.9 · maxdd_dog=-20934.0 | `f22f163` (2026-06-23) | `evidence/frente-LMN` |
| **N** | Indices | Entropia + co-momento entre mercados | 40_entropy_comoment | f28 | corr_entropy_skew=0.827 · corr_1x2_ou_skew=0.146 | `f22f163` (2026-06-23) | `evidence/frente-LMN` |

## Tags de versionamento (`evidence/*`)
Uma tag anotada por marco de evidência aponta o commit que estabeleceu
aqueles números. `git tag -n` lista; `git checkout evidence/frente-E`
recupera o código exato da Frente E.

