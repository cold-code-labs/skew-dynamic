# Estabilidade Temporal da Skewness em Mercados de Apostas de Futebol

**Status:** rascunho de trabalho · pipeline validado em amostra 2005–2025
**Autor:** Vitor Alves
**Última rodada:** dados 38 ligas, 205.450 jogos

---

## 1. Pergunta de pesquisa

A skewness da distribuição de retornos implícitos do mercado de apostas de
futebol é **estável ao longo do tempo**? Especificamente:

- É estacionária (sem deriva de longo prazo)?
- A variação de curto prazo tem estrutura (persistência) ou é ruído?
- Há quebras estruturais associadas a eventos (regulação, COVID, etc.)?

Estudo **autocontido sobre o mercado de apostas** — sem dado financeiro como
fonte nem como moldura conceitual.

## 2. Lacuna na literatura

A literatura trata skewness como fenômeno **cross-sectional** (entre apostas,
num corte): Golec & Tamarkin (1998) mostram que apostadores buscam skewness, não
variância; o favorite-longshot bias é o mecanismo. O ângulo **temporal** — a
skewness agregada do mercado como série, e sua estacionariedade/persistência —
é pouco explorado. Esta é a contribuição.

## 3. Dados

- **Fonte:** dataset multi-liga 2000–2025 (mirror do football-data.co.uk).
- **Recorte:** ≥2005 (cobertura de odds ~100% a partir daí).
- **N:** 205.450 jogos, 38 ligas (inclui BRA, ARG, ligas europeias).
- **Colunas-chave:** `OddHome/Draw/Away` (odd média de fechamento),
  `MaxHome/Draw/Away` (melhor odd do mercado → teste cross-casa),
  `FTResult` (resultado, p/ retorno ex-post), `Division` (controle de liga),
  `MatchDate` (ordenação da janela).

## 4. Método

### 4.1 Retorno ex-post
Para cada jogo, aposta unitária no **favorito** (menor odd):
`retorno = odd-1` se acerta, `-1` se erra. Estratégia fixa e replicável,
conectada à literatura clássica.

### 4.2 Série temporal — janela deslizante + pooling
- Todas as ligas empilhadas e ordenadas por data (fluxo único).
- Janela deslizante de **N=1000 jogos**, passo **250**.
- Resolve o problema do N-por-janela: skewness é momento de 3ª ordem e exige
  amostra grande; pooling garante N estável por ponto, série longa (818 pontos).

### 4.3 Cuidados metodológicos
- **Composição de liga:** empilhar cru pode mover a skewness só pela mudança da
  *mistura* de ligas na janela. Robustez: normalizar retorno por liga antes de
  empilhar, ou incluir composição como controle. *(pendente)*
- **Sobreposição de janelas:** step < window induz autocorrelação artificial.
  Reportar versão com janelas não-sobrepostas como robustez.
- **Erro-padrão da skewness:** via bootstrap (2000 reamostras).

### 4.4 Testes
| Dimensão | Teste |
|---|---|
| Estacionariedade | ADF + KPSS (confirmação dupla) |
| Persistência | ACF + Ljung-Box |
| Quebras estruturais | Bai-Perron / PELT (l2) |
| Robustez cross-casa | repetir com odd máxima (Max*) vs. média |

## 5. Resultados (amostra atual)

| Achado | Valor | Leitura |
|---|---|---|
| Skewness global (favorito) | **+0,230** (boot SE 0,004) | positiva, robusta |
| Skewness mercado (3 outcomes) | **+1,82** | favorite-longshot bias |
| Retorno médio favorito | **−4,8%** | margem da casa (valida pipeline) |
| ADF / KPSS | p<0,001 / p=0,10 | **estacionária** (ambos concordam) |
| Ljung-Box / ACF(1) | p<0,001 / **0,74** | **persistente** (não é ruído) |
| Quebras (2005–2025) | **2** (blip 2012/13) | regime essencialmente único |

### Síntese
A skewness do mercado de apostas é um traço **estrutural, estável-com-memória**:
estacionária no longo prazo (reverte sempre a ~0,23), porém altamente
persistente no curto prazo (ondas lentas, processo tipo AR(1) com reversão à
média), sem quebra permanente em 20 anos. Não é constante nem caótica.

## 6. Próximos passos
1. Controle de composição de liga (normalização por liga).
2. Robustez com janelas não-sobrepostas.
3. Teste cross-casa (odd média vs. máxima): a skewness diverge entre casas?
4. Investigar o blip de 2012/13 (artefato de composição? entrada de liga?).
5. Recorte por liga individual (Brasileirão isolado vs. pooling europeu).
6. Modelagem AR(1)/ARMA explícita da série + half-life da reversão.

## 7. Referências centrais
- Golec & Tamarkin (1998). *Bettors Love Skewness, Not Risk, at the Horse Track.* JPE.
- Andrikogiannopoulou & Papakonstantinou. *Estimating Risk Preferences from
  Betting Choices.*
- (Betfair time-series, UK horse racing) — contraponto de gain-loss asymmetry.
