# template-web-coolify-light

Next.js (App Router) + PocketBase embutido, deploy 1-clique no Coolify. Este é o
template base; cada projeto derivado herda tudo abaixo.

## Rodar / preview no Claude Code

**Um passo, sem `.env`, sem segredos.** O Preview do Claude Code usa o config
`dev` em `.claude/launch.json`, que roda `scripts/dev-preview.sh`. O Preview é
DONO do processo (escolhe a porta e injeta via `$PORT`).

A partir de um `git clone` limpo, iniciar o config **dev** do Preview:
1. instala as deps se `node_modules` faltar (`corepack` + `pnpm install`);
2. sobe o PocketBase local em background (cache em `.pb/`, dados em `./pb_data`),
   espera o `/api/health` e o mata ao sair;
3. sobe o Next na **porta injetada** (`next dev -p $PORT`) em **modo demo
   zero-config** (`APP_ENV=dev`, `AUTH_MODE=stub`) e renderiza a tela de login
   demo (botão "Entrar com um clique").

Equivalente pela CLI (fora do Preview):

```bash
pnpm preview            # mesmo entrypoint do Preview (honra $PORT se setado)
# ou, pra dev humano:
pnpm dev:local          # PocketBase + app num comando (porta 3000)
pnpm dev                # só o app (auto-instala deps via predev)
```

## Readiness / health

- **`GET /api/health`** → `200 ok` sem auth. É o caminho canônico de saúde
  (Coolify e probes externos usam este).
- **`/`** responde **200** (splash que encaminha pro app no cliente) — de
  propósito, pra que probes que batem em `/` não vejam um 307 e travem em
  "Awaiting server…". O Preview também lê o `ready` do stdout do Next.

## Credenciais demo

- **App (login demo):** botão "Entrar com um clique" no `/login` (modo stub, sem
  senha). Em modo pocketbase, usuário semeado `demo@coldcodelabs.com` /
  `snowdemo123`.
- **PocketBase Admin (`/_/`) local:** `admin@local.dev` / `admin1234567`
  (criado pelo `pnpm pb:dev`; só dev local).

## Dev vs. prod (schema-as-code)

`APP_ENV` (default `dev`) decide o alvo do checkout local — produção é blindada
(o container fixa `POCKETBASE_URL` loopback, que sempre vence). Mude schema no
`/_/` local → vira arquivo em `pocketbase/pb_migrations/` → commit + push → o
backend ao vivo aplica no deploy (`pocketbase serve --migrationsDir`). Nunca
edite schema direto em produção. Veja o README pra o fluxo completo.

## Gotchas

- A porta interna do PocketBase é **`PB_PORT`** (default 8090), nunca `PORT` —
  `PORT` é reservada pro app (injetada por ferramentas externas).
- Regras das coleções exigem `@request.auth.id != ''`: leitura anônima é
  rejeitada. Por isso o preview demo usa `AUTH_MODE=stub`+`DATA_MODE=stub`
  (dados in-code). Pra dados reais, use `AUTH_MODE=pocketbase`+`DATA_MODE=pocketbase`.
