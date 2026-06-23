# Literatura & Ancoragem Conceitual

> Levantamento (deep-research, jun/2026) para ancorar a tese: **skewness da
> distribuição de retornos implícitos 1X2 é um invariante estrutural por liga,
> função da competitividade**. Foco: modelagem de balanço competitivo. Cada
> fonte tem venue + por que importa. Claims verificados adversarialmente
> (voto N-0/N-1 indica robustez).

## TL;DR estratégico

A literatura sustenta com força **metade** da tese — o mecanismo
`competitividade → distribuição de p por jogo → skewness`. Mas **contradiz a
forma forte** ("constante fixa no tempo + flutuação = ruído amostral"): os dois
melhores estudos de EPL (Lee & Fort 2012; Basini et al. 2023) acham **quebras
estruturais reais** ligadas a choques institucionais (Champions League 94/95,
Bosman 95, desigualdade de receita). 

**Recomendação:** reposicionar de *"constante fixa"* para **"baseline estrutural
específico da liga, estável DENTRO de regimes competitivos"**. Essa forma a
evidência carrega; a forma forte não. Nosso achado F (a única "quebra" em 20
anos = dataset crescendo de 21→37 ligas em 2012) já é compatível com isso — só
precisa ser enquadrado como *invariância intra-regime*, não atemporalidade
absoluta.

---

## Eixo 1 — Medidas de balanço competitivo (PRIMÁRIO)

A medição de CB é canonicamente um problema de **desigualdade/concentração**, e
cada índice tem falhas de comparabilidade entre ligas de tamanhos diferentes —
crítico pra nós, já que comparamos ligas com nº de times distinto.

| Fonte | Venue | Por que importa |
|---|---|---|
| **Utt & Fort (2002)** | J. Sports Economics 3(4):367-373 | ⚠️ **Gini é inválido para jogo de soma-zero de liga**; recomendam **SD de win-pct** para comparação temporal. → *não usar Gini cru* como índice de competitividade. [voto 3-0] |
| **Owen, Ryan & Weatherston (2007)** | Review of Industrial Organization 31:289-302 | Limites do HHI cru dependem do tamanho da liga; propõem **HHI normalizado (HHI\*/dHHI)** para comparabilidade cross-liga. → índice defensável pro nosso painel. [3-0] |
| **Borooah & Mangan (2012)** | Applied Economics 44(9):1093-1102 | Família de **Entropia Generalizada** (parâmetro de sensibilidade que repondera partes da distribuição de desempenho). → conecta CB a momentos/assimetria da distribuição, ponte natural pra skewness. [3-0] |

**Para a nossa W2:** benchmarkar skewness contra um índice **robusto a tamanho**
— HHI\*/dHHI ou SD-de-win-pct (Noll-Scully). **Gini cru sai** (apesar do nosso
corr −0,83 atual usá-lo informalmente — vale re-rodar com Noll-Scully/HHI\*).

## Eixo 1b — Da competitividade à distribuição de p por jogo (A PONTE)

Aqui está o ouro: já existe maquinário formal que escreve a distribuição
(casa/empate/fora) por jogo como função da força/competitividade — **não** só do
ranking final de temporada. É o template pra derivar `skewness = f(competitividade)`.

| Fonte | Venue | Por que importa |
|---|---|---|
| **Csató & Petróczy (2024)** | arXiv:2406.19222 | **Análogo mais próximo da nossa tese**: CB ex-ante = média (normalizada) da prob. de vitória do time mais forte, via Elo `W_ij = 1/(1+10^{-(R_i-R_j)/400})`. É competitividade expressa como função sobre P(forte vence). ⚠️ Mas é a **média**, não 3º momento, e o escopo é fase de grupos da UCL, não liga nacional. [3-0] |
| **Basini, Tsouli, Ntzoufras & Friel (2023)** | JRSS-A 186(3):530-556 | **Stochastic block model**: resultado 1X2 segue multinomial cujos parâmetros variam por bloco de força (array K×K×3 W/D/L). → liga competitividade-em-tiers diretamente às probs 1X2. Acha EPL equilibrada até ~2003, depois desequilibrada. [3-0] |
| **Goddard & Asimakopoulos (2004)** | J. Forecasting | **Ordered-probit** mapeia variável latente de força via 2 cut-offs em fora/empate/casa. Template direto pra distribuição de p a partir de covariáveis de força. [3-0] |
| **Koning (2000)** | The Statistician / JRSS-D 49:419-431 | Ordered-probit de resultados holandeses usado **explicitamente para estudar mudança de CB no tempo** — precedente de análise de CB a nível de jogo (não de classificação). [3-0] |

## Eixo 1c — Heterogeneidade entre ligas & estabilidade temporal (CONTRA-EVIDÊNCIA)

⚠️ **Confronto direto à forma forte da tese.** CB **não** é atemporal na EPL:

| Fonte | Venue | Achado |
|---|---|---|
| **Lee & Fort (2012)** | Scottish J. Political Economy 59(3):266-282 | **Quebras estruturais** dividem a história da EPL em 4 regimes; queda acentuada no "Modern Period" alinhada a Champions League 94/95, desigualdade de receita e Bosman 95. *Mudança de regime, não ruído.* [3-0; atribuição tri-causal 2-1] |
| **Basini et al. (2023)** | JRSS-A | EPL equilibrada até ~2003, "quite imbalanced since then". [3-0] |
| **Csató & Petróczy (2024)** | arXiv:2406.19222 | ✅ **Único aliado forte do "flutuação pode ser não-tendência"**: com medidas melhores, **nenhuma tendência de longo prazo** na CB da fase de grupos da UCL (2003/04–2023/24), derrubando estudos anteriores que viam declínio. Mas argumenta *artefato de medida* > *ruído amostral puro*, e é torneio, não liga nacional. [2-1] |

**Implicação:** nosso estudo precisa **distinguir um baseline de skewness
FIXO-por-liga de quebras de regime reais**. É exatamente o que os blocos A
(estacionariedade) e F (forense da quebra de 2012) atacam — mas o enquadramento
tem que reconhecer Lee & Fort e Basini de frente.

---

## Eixo 2 — FLB → skewness (APOIO; o elo mecânico)

O favorite-longshot bias é o canal que converte a distribuição de p por jogo em
skewness nos retornos de aposta.

| Fonte | Venue | Por que importa |
|---|---|---|
| **Whelan (2024)** | Economica 91(361):188-209 | FLB presente em **mercados fixed-odds de futebol** (não só pari-mutuel), gerado por discordância de apostadores + aversão a risco do bookmaker. → confirma FLB no nosso próprio mercado. [3-0] |
| **Golec & Tamarkin (1998)** | J. Political Economy 106:205-225 | FLB como **preferência por skewness** — liga skewness dos retornos à forma da utilidade do apostador, observacionalmente equiv. a risk-love. ⚠️ **Interpretação competidora**: skewness pode refletir preferência do apostador / estrutura de mercado, não (só) "competitividade verdadeira". [3-0] |
| **Snowberg & Wolfers (2010)** | J. Political Economy / NBER WP 15923 | Via compound bets, acham que **misperception de probabilidade** (Prospect Theory) dirige o FLB, não risk-love. ⚠️ Importa pra circularidade: odds de-vigadas embutem *cognição do apostador*, não só p verdadeiro. (Setting: turfe US, não futebol.) [3-0] |

> **Football-specific a fechar (citados na corroboração, não verificados aqui):**
> Cain, Law & Peel (2000); Direr (2013); **Angelini & De Angelis (2019)** — este
> achou FLB **mais fraco** em dados europeus recentes, i.e. *variação temporal no
> próprio viés* que pode mascarar/contaminar nosso teste de invariância. Vale
> buscar e citar.

## Eixo 3 — De-vigging & circularidade (APOIO; a vulnerabilidade)

A escolha do método de de-vig **move diretamente a skewness medida**, e o método
mais comum é enviesado contra justamente o sinal que estudamos.

| Fonte | Venue | Por que importa |
|---|---|---|
| **Shin (1993)** | Economic Journal 103(420):1141-1153 | Modelo estrutural canônico de de-vig: spread endógeno (proteção contra insiders), separa p verdadeiro da margem via parâmetro `z`. Nosso método primário. [3-0] |
| **Clarke, Kovalchik & Ingram (2017)** | Am. J. Sports Science 5(6):45-49 | ⚠️ **Multiplicativo ignora FLB** (remove overround proporcionalmente; longshots precisam perder fatia maior). **Power universalmente bate multiplicativo** e iguala/supera Shin em 3 datasets. → reportar **sensibilidade entre métodos**. (Venue de baixo tier, mas não-contraditado.) [3-0] |
| **Štrumbelj (2014)** | Int. J. Forecasting 30(4):934-943 | Probabilidades de Shin > normalização básica/regressão, fixed-odds **e** exchanges. ⚠️ Mas a alegação forte "Shin domina TODO par bookmaker/esporte" foi **REFUTADA [0-3]** — vantagem do Shin encolhe com tamanho de mercado e não remove FLB todo (ex. La Liga). *Não afirmar superioridade incondicional do Shin.* |
| **Nash (2018)** | arXiv:1811.12516 (preprint) | Formaliza: preço de consenso `P_C` ~ triangular em torno da freq. verdadeira `P_T`; **corolário: P_T é distribuído para cada P_C**. → defesa formal contra a tautologia "odds SÃO p por definição", mas também restrição: cada odd é consistente com uma *distribuição* de competitividades verdadeiras. [3-0] |

---

## A LACUNA (nossa contribuição original)

A verificação **não achou nenhum paper** que:
1. trate a **skewness (3º momento)** da distribuição 1X2 de-vigada como o
   invariante a nível de liga (a literatura para na *média* — Csató — ou na
   *variância*/Noll-Scully);
2. formalize **`skewness = f(competitividade)`** explicitamente;
3. teste **constância cross-liga** com inferência rigorosa de 3º momento /
   variance-ratio, enfrentando a **circularidade do de-vig de frente**.

→ É aí que o estudo entra. A ponte método (variance-ratio + bootstrap de 3º
momento aplicados a skewness-de-odds) é, ela própria, contribuição — ninguém
amarrou essas máquinas a momento de 3ª ordem de odds.

## Riscos a blindar no design (críticas a antecipar)

1. **Circularidade / tautologia (a mais séria).** Se "competitividade" sai das
   *mesmas* odds que dão a skewness, o corr −0,83 é parcialmente tautológico.
   **Design defensável:** medir competitividade de **fonte independente das odds**
   (HHI\*/Noll-Scully de classificação final, ou Elo de *resultados* não preços) e
   skewness das odds de-vigadas — e mostrar que o elo sobrevive. **Ação imediata:
   re-rodar W2 com competitividade odds-independente.**
2. **Sensibilidade ao de-vig.** Multiplicativo vs power vs Shin divergem
   exatamente na cauda do longshot que dirige a skewness → rodar os 3 e mostrar
   que o corr não é artefato do método (já temos `DEVIG_METHOD` parametrizado).
3. **Mudança de regime vs invariância.** Reconhecer Lee & Fort / Basini;
   reposicionar tese como invariância **intra-regime** (ver TL;DR).
4. **Viés de seleção de ligas + variação no próprio FLB** (Angelini & De Angelis):
   FLB enfraquecendo no tempo pode se confundir com (in)variância de skewness.

---

## Datasets a verificar (deliverable em aberto — checar cobertura/licença)

> O levantamento **não** validou disponibilidade pública além do
> football-data.co.uk. Candidatos a conferir antes de depender:

- **football-data.co.uk extended** — divisões secundárias (E1-E3, SP2, I2, D2,
  F2…) além das principais já usadas; mais cobertura de ligas pra cross-section.
- **`engsoccerdata` (R package)** — resultados históricos para computar
  HHI/Gini/Noll-Scully por liga-temporada (fonte odds-independente de
  competitividade → ataca a circularidade).
- **clubelo.com (API)** — Elo por clube para CB ex-ante estilo Csató, independente
  de preços.
- **Kaggle "European Soccer Database"** — resultados + odds multi-casa.
- **Odds de abertura vs fechamento** (oddsportal/arquivos) — habilita a frente
  "drift abertura→fechamento" do CLAUDE.md (precisa de odds de abertura).

## Índice de fontes (qualidade)

Primárias peer-reviewed: Utt & Fort, Owen et al., Borooah & Mangan, Basini et al.,
Goddard & Asimakopoulos, Koning, Lee & Fort, Whelan, Golec & Tamarkin (via
Snowberg & Wolfers), Snowberg & Wolfers, Shin, Štrumbelj. Preprints: Csató &
Petróczy (peer-review-track), Nash (single-author, não revisado). Baixo tier mas
útil: Clarke et al.
