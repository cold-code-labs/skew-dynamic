# Handoff — Módulo "Reuniões Gravadas"

Módulo novo do template light: grava reuniões no navegador, salva o áudio no
PocketBase e transcreve com OpenAI Whisper.

## Onde está
- **Template (fonte da verdade):** `cold-code-labs/template-web-coolify-light`
  (commit `feat: módulo Reuniões Gravadas…`). Já registrado em `features.json`,
  então aparece sozinho no **Ice Breaker / Features Library** de instâncias novas.
- **Instância de teste:** `cold-code-labs/arte-one` →
  **https://arte-one.coldcodelabs.com** (Coolify app `j3vpw4xbf8d1xvj69t7xadng`).
  - `APP_FEATURES` foi atualizado para `core,calendario,reunioes` (senão o
    módulo ficaria oculto nesta instância).

## Como testar (anytime)
1. Abra **https://arte-one.coldcodelabs.com**, faça login (o botão "Entrar como
   demo" está ligado — `DEMO_LOGIN=true`).
2. Sidebar → **Reuniões Gravadas** (grupo Operações).
3. **Nova gravação** → permita o microfone → Iniciar / Pausar / Parar →
   pré-visualize → dê um título → **Salvar reunião**.
4. A reunião aparece na lista com player de áudio e status.

## Ligar a transcrição (você escolhe o provedor)
A gravação/armazenamento funcionam **sem** key. A transcrição é à-la-carte com
**dois provedores** (env `TRANSCRIBE_PROVIDER`):

**Opção A — OpenAI Whisper** (transcrição corrida, sem locutores):
1. Coolify → `TRANSCRIBE_PROVIDER=openai` (ou deixe em branco, é o default) +
   `OPENAI_API_KEY=sk-…` (a key precisa do scope de áudio → preset **"All"** ou
   "Model capabilities" = Write).

**Opção B — Deepgram com diarização** ("quem falou o quê", Locutor 1/2/3…):
1. Coolify → `TRANSCRIBE_PROVIDER=deepgram` + `DEEPGRAM_API_KEY=…`
   (opcional `DEEPGRAM_MODEL`, default `nova-2`). A diarização já vem ligada.

Depois: **Redeploy** o app → em cada reunião → **"Iniciar transcrição"** → texto
em "Ver transcrição". Sem a key do provedor ativo, o botão avisa.

> **arte-one está hoje em `deepgram`** (com diarização). Para ver vários
> locutores, grave um trecho com 2+ pessoas falando — áudio real diariza bem
> melhor que samples sintéticos.
> A mesma config vale para qualquer instância nova (env no Coolify daquela app).

## O que já funciona
- Gravar (iniciar/pausar/parar), pré-visualizar e **salvar** áudio (PocketBase,
  arquivo **protegido** — só baixa com token do usuário logado).
- Listar reuniões com player, status (Gravada / Transcrevendo / Transcrita / Erro),
  **renomear** e **excluir** (gated por RBAC: `data.write` / `data.delete`).
- **Transcrição batch** via Whisper (quando `OPENAI_API_KEY` está setado).
- Gravações **compartilhadas no workspace** (escopo por tenant, como Arquivos).

## O que ficou para depois (próximo passo)
- **Transcrição ao vivo (realtime)**: o toggle existe na UI mas está
  **desabilitado** ("Em breve"). Streaming via OpenAI Realtime API (token
  efêmero + WebSocket) é um PR focado seguinte. Para já exibir o toggle numa
  instância, setar `MEETINGS_REALTIME=true` (continua sem streaming).
- Página de detalhe dedicada + transcrição editável.
- Chunking para reuniões longas (ver limite abaixo).

## Limites conhecidos
- **Whisper aceita até 25MB por arquivo.** O áudio é `webm/opus` (~1MB/min), então
  ~25min+ cabe. Acima disso a API recusa e o status vira "Erro" (sem quebrar).
  O campo PocketBase e o limite de Server Action estão em 32MB.
- `getUserMedia` exige HTTPS (ou localhost) — ok em produção.

## Fixes de plataforma incluídos (afetam todo o template)
- `next.config.mjs`: `Permissions-Policy` liberou **`microphone=(self)`** (antes
  `microphone=()` bloqueava o microfone em todo o app) e
  `experimental.serverActions.bodySizeLimit = "32mb"` (o default de 1MB barraria
  o upload de áudio).

## Arquivos principais
- `pocketbase/pb_migrations/1749520000_reunioes.js` — coleção `reunioes` + seed.
- `lib/reunioes/` — `types.ts` (client-safe), `meetings.ts` (reader), `actions.ts`
  (criar/transcrever/renomear/excluir), `transcribe.ts` (chamada Whisper).
- `app/(app)/reunioes/page.tsx` + `components/reunioes/reunioes-view.tsx` (UI + gravador).
- `config/env.ts`, `config/modules.ts`, `features.json`, `.env.example` — wiring.
