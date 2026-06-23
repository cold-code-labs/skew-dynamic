# Estabilidade Estrutural da Skewness em Mercados de Apostas de Futebol

**Status:** metodologia consolidada · pipeline reproduzido em amostra 2005–2025
**Autor:** Vitor Alves
**Dataset:** congelado (`data/PROVENANCE.json`, sha256 `6905ca53…`), 205.435
jogos, 38 ligas, 2005-01→2025-06. Alvo: *Royal Society Open Science* (regularidade
empírica + mecanismo + artefato reprodutível).

---

## 1. Pergunta de pesquisa

A assimetria (skewness) da distribuição de retornos implícitos do mercado de
apostas de futebol é um **processo temporal** ou um **invariante estrutural**?
Três frentes:

1. *Cross-sectional* — de onde vem a skewness? (mecanismo)
2. *Temporal* — ela tem dinâmica (deriva, persistência, quebras) ou é constante?
3. *Estrutural* — o que determina o nível de cada liga?

**Tese:** a skewness é, em 1ª ordem, a **imagem algébrica** da distribuição de
probabilidades implícitas; o nível de cada liga é determinado pela
competitividade esportiva (lenta), o que a torna um invariante temporal. A
margem das casas é ortogonal à assimetria.

## 2. Lacuna na literatura

Golec & Tamarkin (1998) tratam a preferência por skewness como fenômeno
*cross-sectional* (entre apostas, num corte); o favorite-longshot bias (FLB) é
o mecanismo (Snowberg & Wolfers 2010). Faltam (i) a **decomposição mecânica**
que quantifica quanto da skewness de mercado é a identidade de Bernoulli da
distribuição de p; (ii) a **lei estrutural** skewness=f(competitividade) medida
com um regressor *independente das odds*; (iii) a **invariância temporal** de
20 anos como afirmação de eficiência/microestrutura. Esta é a contribuição.

## 3. Dados

- **Fonte:** football-data.co.uk normalizado (espelho xgabora; main + ligas
  extra/sul-americanas), congelado por hash. Recorte ≥2005 (cobertura de odds
  ~100%).
- **N:** 205.435 jogos 1X2; 148.261 com mercado over/under 2.5.
- **Colunas:** `OddH/D/A` (média de fechamento) e `MaxH/D/A` (melhor preço →
  teste de margem); `FTResult`, `FTHome/FTAway` (gols → O/U e Elo);
  `HomeTeam/AwayTeam` (Elo); `Division`, `MatchDate`.

## 4. Objeto primário — skewness ex-ante (de-vigada)

Aposta unitária no favorito a odd decimal *o* com prob. verdadeira *p*:
retorno `(o−1)` com prob *p*, `−1` com prob `1−p` — uma **Bernoulli reescalada**
de momentos centrais fechados (`μ=po−1`, `σ²=p(1−p)o²`, `m₃=p(1−p)(1−2p)o³`).
A skewness por jogo **depende só de p**: `(1−2p)/√(p(1−p))`, cruzando zero em
p=0,5. A skewness agregada (liga/janela) é a da **mistura**, decomposta por
**lei dos cumulantes totais**:

```
M₃ = E[m₃ᵢ]                     (mecânico: assimetria intra-jogo / FLB)
   + 3·E[σ²ᵢ(μᵢ−μ)]             (covariância variância×média)
   + E[(μᵢ−μ)³]                 (dispersão entre jogos)
```

- **De-vig:** Shin (1993) primário (subproduto *z* = fração de dinheiro
  informado); multiplicativo e power como robustez.
- **Ex-post realizada** (skewness dos retornos efetivos) = robustez; deve
  convergir à ex-ante sob calibração.

**Extensão multi-momento (forma).** A Bernoulli reescalada tem momentos centrais
fechados de **toda ordem**, `m_k = oᵏ·p(1−p)·[(1−p)^{k−1} + (−1)ᵏ·p^{k−1}]`, e o
k-ésimo momento da mistura sai da **lei dos momentos totais**,
`M_k = E_i[Σ_j C(k,j)·m_{j,i}·dᵢ^{k−j}]`, `dᵢ=μᵢ−μ` (a decomposição de M₃ acima é o
caso k=3). Mede-se assim var/skew/**kurtose**/5ª–6ª ordem da distribuição implícita
e a **fração `within`** (mecânica) por ordem. Sob odds justas as médias são zero
(d≡0), logo `M_k=E[m_k]` e o ordered-probit prevê **cada** momento da liga a partir
da competitividade (não só o 3º) — *invariância de forma*. O **colapso de
distribuição** (KS condicional à faixa de p_fav; o tamanho de efeito é a estatística
KS, pois o p-valor satura com n grande) testa se, fixada a competitividade, a
distribuição é a mesma entre ligas.

## 5. Competitividade odds-free (quebra de circularidade)

Medir competitividade por p_fav (das odds) é circular. Constrói-se um **Elo só
de resultados**: passo cronológico multi-liga (W/D/L + saldo de gols, vantagem
de casa), e um mapa rating-diff→(P_H,P_D,P_A) por **MNLogit calibrado nos
resultados**. Medidas por liga: entropia média da previsão, prob. do favorito
Elo, dispersão de força, taxa de zebra. Nenhuma toca odds.

## 6. Painel temporal

Unidade = (liga, temporada) — dissolve o confound de composição por construção.
Testes: tendência secular (FE de liga + ano, SE cluster); decomposição
between/within com **benchmark de ruído amostral** (bootstrap dos jogos);
tendências/quebras por liga; **vinheta COVID** (estádios vazios 2020 como
experimento natural de choque na vantagem de casa).

## 7. Testes

| Dimensão | Teste |
|---|---|
| Calibração de-vig | over-rate vs p_over; ex-ante vs ex-post |
| Decomposição | lei dos cumulantes totais (within/cov/between) |
| Mecanismo odds-free | corr/OLS skew~Elo + bootstrap CI (n=38) |
| Estacionariedade/i.i.d. | ADF+KPSS, Ljung-Box, Variance-Ratio, AR(1) |
| Invariância temporal | painel FE+ano (SE cluster), ICC, quebras |
| Margem | overround e skew: odds média vs máxima |
| Robustez | de-vig (mult/power/shin), janela, overlap, O/U binário |

## 8. Resultados (amostra congelada)

| Achado | Valor | Leitura |
|---|---|---|
| Skew global ex-ante / ex-post | **+0,236 / +0,230** | objeto implícito reproduz o realizado |
| Decomposição M₃ | **+102,6% intra-jogo**, ~0% entre-jogos | skewness = imagem algébrica do FLB |
| corr(elo_pfav, p_fav_odds) | **+0,909** | odds *leem* a competitividade esportiva |
| skew ~ competitividade odds-free | **+0,83** (upset) / **−0,75** (elo_pfav) | lei não-circular sobrevive |
| Tendência secular (painel) | β=**+0,00015/ano** (p=0,73) | sem deriva em 20 anos |
| ICC (between/total) | **0,70** | invariante de liga domina o tempo |
| Margem: overround vs skew | 1,067→1,009 vs +0,236→+0,254 | margem ortogonal à assimetria |
| O/U 2.5 binário | ex-ante −0,210 (within 99,6%) | identidade vale fora do 1X2 |

### Síntese
A skewness do mercado de apostas é um **invariante estrutural**: ~100% a
assimetria intra-jogo da distribuição de probabilidades (mecânico), com nível
de liga determinado pela competitividade esportiva — relação que **sobrevive a
uma medida de competitividade independente das odds** — e **sem deriva temporal
em 20 anos**. A margem das casas afeta o nível de retorno, não a assimetria. A
assimetria de risco é **herdada do esporte**, não produzida pelo apreçamento.

## 9. Referências centrais
- Golec & Tamarkin (1998). *Bettors Love Skewness, Not Risk, at the Horse Track.* JPE.
- Snowberg & Wolfers (2010). *Explaining the Favorite-Longshot Bias.* JPE.
- Shin (1993). *Measuring the Incidence of Insider Trading in a Market for
  State-Contingent Claims.* Economic Journal. (de-vigging)
- Štrumbelj (2014). *On determining probability forecasts from betting odds.* IJF.
- Andrikogiannopoulou & Papakonstantinou. *Estimating Risk Preferences from Betting Choices.*
- Constantinou & Fenton (2012). *Solving the problem of inadequate scoring
  rules for assessing probabilistic football forecasts.* (Elo/probabilidades)
- Kraus & Litzenberger (1976); Harvey & Siddique (2000); Barberis & Huang (2008)
  — skewness em finanças (contraste).
