// Centralised, à-la-carte runtime configuration — read SERVER-SIDE only.
//
// Every backend piece is optional. With the default "stub" modes the app boots
// and runs end-to-end with ZERO backend (demo login + demo data), so the
// template is usable the moment it's cloned. Flip a mode + set the matching
// URLs to wire a real Postgres + Logto + PostgREST + edge-runtime stack.

export type AuthMode = "stub" | "logto" | "pocketbase" | "hauldr"
export type DataMode = "stub" | "postgrest" | "pocketbase"
export type LogLevel = "debug" | "info" | "warn" | "error" | "silent"

/**
 * Server log verbosity (see lib/log.ts). Default "info": the boot config summary
 * plus every caught failure land in the container logs — so a fresh deployment
 * is debuggable out of the box. Set "warn"/"error" to quiet a noisy instance,
 * "debug" while diagnosing, or "silent" to mute server logging entirely.
 */
export const LOG_LEVEL: LogLevel = ((): LogLevel => {
  const raw = (process.env.LOG_LEVEL ?? "").toLowerCase()
  return raw === "debug" || raw === "warn" || raw === "error" || raw === "silent"
    ? (raw as LogLevel)
    : "info"
})()

/**
 * stub = one-click demo login · logto = real OIDC via self-hosted Logto ·
 * pocketbase = email/password against a bundled PocketBase (the "light" tier) ·
 * hauldr = email/password against a Hauldr project's GoTrue (the "BaaS" tier).
 */
export const AUTH_MODE: AuthMode =
  process.env.AUTH_MODE === "logto"
    ? "logto"
    : process.env.AUTH_MODE === "pocketbase"
      ? "pocketbase"
      : process.env.AUTH_MODE === "hauldr"
        ? "hauldr"
        : "stub"

/**
 * stub = in-code demo data · postgrest = vanilla Postgres via PostgREST ·
 * pocketbase = collections on the bundled PocketBase.
 */
export const DATA_MODE: DataMode =
  process.env.DATA_MODE === "postgrest"
    ? "postgrest"
    : process.env.DATA_MODE === "pocketbase"
      ? "pocketbase"
      : "stub"

/**
 * Deployment target for THIS running process — a LOCAL-DEV convenience.
 *   dev (default) → talk to a PocketBase you run locally (`pnpm pb:dev`).
 *   prd           → talk to this instance's LIVE remote backend (data-<sub>,
 *                   behind Cloudflare Access — needs the service token below).
 * Production is unaffected: the container sets POCKETBASE_URL to its bundled
 * localhost PocketBase, and a loopback URL ALWAYS wins over APP_ENV (below).
 */
export type AppEnv = "dev" | "prd"
export const APP_ENV: AppEnv =
  (process.env.APP_ENV ?? "").trim().toLowerCase() === "prd" ? "prd" : "dev"

const PB_EXPLICIT = process.env.POCKETBASE_URL ?? ""
const PB_IS_LOOPBACK = /\/\/(127\.0\.0\.1|localhost|\[::1\])(:|\/|$)/.test(PB_EXPLICIT)
const PB_LOCAL = process.env.POCKETBASE_URL_LOCAL || "http://127.0.0.1:8090"
// Remote backend: POCKETBASE_URL_REMOTE, or a legacy non-loopback POCKETBASE_URL
// (so the .env Fleet generates today — POCKETBASE_URL=https://data-<sub>… — keeps
// working as the "prd" target without regenerating it).
const PB_REMOTE =
  process.env.POCKETBASE_URL_REMOTE || (PB_EXPLICIT && !PB_IS_LOOPBACK ? PB_EXPLICIT : "")

/**
 * Base URL of the PocketBase the app talks to. Resolution order:
 *   1) explicit loopback POCKETBASE_URL → always wins (the production container).
 *   2) APP_ENV=prd → the remote backend (data-<sub>).
 *   3) APP_ENV=dev (default) → the local PocketBase.
 * The browser never talks to it directly — all access is server-side via the seams.
 */
export const POCKETBASE_URL = PB_IS_LOOPBACK
  ? PB_EXPLICIT
  : APP_ENV === "prd"
    ? PB_REMOTE || PB_LOCAL
    : PB_LOCAL

/**
 * Cloudflare Access service token — attached to every PocketBase request ONLY
 * when actually hitting the remote backend (APP_ENV=prd against data-<sub>, which
 * sits behind Cloudflare Access locked to service-token-only). In dev (local PB)
 * or production (localhost) Access isn't involved, so no headers are added.
 */
const PB_USING_REMOTE = !PB_IS_LOOPBACK && APP_ENV === "prd"
export const PB_CF_ACCESS_CLIENT_ID = PB_USING_REMOTE
  ? (process.env.PB_CF_ACCESS_CLIENT_ID ?? "")
  : ""
export const PB_CF_ACCESS_CLIENT_SECRET = PB_USING_REMOTE
  ? (process.env.PB_CF_ACCESS_CLIENT_SECRET ?? "")
  : ""

/**
 * One-click demo login (only with AUTH_MODE=pocketbase). When true, the login
 * page shows an "Entrar como demo" button that signs in as the demo user below.
 * DEV/DEMO ONLY — anyone who can reach the page can click in. Leave false (the
 * default) in production; the real email/password form is always available.
 */
export const DEMO_LOGIN = process.env.DEMO_LOGIN === "true"

/** Demo user used by the one-click button (matches the seeded migration user). */
export const DEMO_LOGIN_EMAIL =
  process.env.DEMO_LOGIN_EMAIL ?? "demo@coldcodelabs.com"
export const DEMO_LOGIN_PASSWORD =
  process.env.DEMO_LOGIN_PASSWORD ?? "snowdemo123"

/**
 * Resolve a backend URL by environment, mirroring the PocketBase loopback-wins
 * rule but for separate services: production is native (the internal URL on the
 * Coolify network — the DB/services are never public), and a LOCAL-DEV checkout
 * opts into a public dev endpoint with APP_ENV=dev + a `*_REMOTE` var.
 *   • APP_ENV=dev (default) AND a `<name>_REMOTE` is set → the remote (public).
 *   • otherwise → the internal `<name>` (the production default).
 */
function resolveByEnv(internal: string, remote: string): string {
  if (APP_ENV === "dev" && remote) return remote
  return internal
}

/**
 * PostgREST data-API base URL. In the Hauldr tier this is the project's `rest`
 * service: internal on the Coolify network in prod, the public `rest-<proj>`
 * URL in dev (set DATA_API_URL_REMOTE). The browser never talks to it — all
 * access is server-side via lib/data/client.ts, which forwards the user's GoTrue
 * access token so PostgREST enforces per-user RLS from the JWT claims.
 */
export const DATA_API_URL = resolveByEnv(
  process.env.DATA_API_URL ?? "",
  process.env.DATA_API_URL_REMOTE ?? "",
)

/**
 * Optional service token for the data-API (server-side only, never exposed).
 * Leave UNSET in the Hauldr tier: with no service token, the data client
 * forwards the signed-in user's GoTrue access token instead, so PostgREST
 * applies per-user RLS rather than a god-mode service role.
 */
export const DATA_API_TOKEN = process.env.DATA_API_TOKEN ?? ""

// ── Hauldr (GoTrue auth + PostgREST data, the "BaaS" tier) ───────────────────
// AUTH_MODE=hauldr signs in email/password against the project's GoTrue and
// keeps the access+refresh tokens in httpOnly cookies. The access token is an
// HS256 JWT verified locally against HAULDR_JWT_SECRET (the project's GoTrue
// secret) and forwarded to PostgREST for RLS. Like the data-API, the GoTrue URL
// is internal in prod / public (HAULDR_GOTRUE_URL_REMOTE) in dev.

/** Project GoTrue base URL (e.g. https://auth-<proj>.coldcodelabs.com in dev). */
export const HAULDR_GOTRUE_URL = resolveByEnv(
  process.env.HAULDR_GOTRUE_URL ?? "",
  process.env.HAULDR_GOTRUE_URL_REMOTE ?? "",
)

/**
 * The project's GoTrue HS256 JWT secret — used to verify access tokens locally
 * (signature + expiry) before trusting their claims. Same secret PostgREST is
 * configured with, so a token the app accepts is a token PostgREST accepts.
 */
export const HAULDR_JWT_SECRET = process.env.HAULDR_JWT_SECRET ?? ""

/**
 * App role granted to a Hauldr-authenticated user when the GoTrue token carries
 * no explicit app role (single-tenant default). GoTrue's `role` claim is always
 * "authenticated" (what PostgREST switches on); this is the SEPARATE capability
 * role (see config/roles.ts). Owner = full access, the natural default for a
 * single-tenant client app. Override per project with HAULDR_DEFAULT_ROLE.
 */
export const HAULDR_DEFAULT_ROLE = process.env.HAULDR_DEFAULT_ROLE || "owner"

/** edge-runtime (Deno) functions base URL, e.g. https://fn.<app>.coldcodelabs.com */
export const FUNCTIONS_URL = process.env.FUNCTIONS_URL ?? ""

/** Public base URL of this deployment (deep-links + auth redirects). */
export const APP_BASE_URL = process.env.APP_BASE_URL ?? "http://localhost:3000"

/** Fallback tenant for single-tenant deploys / users not yet linked to one. */
export const DEFAULT_TENANT_ID =
  process.env.DEFAULT_TENANT_ID ?? "00000000-0000-0000-0000-000000000000"

/**
 * Multi-tenant mode. OFF by default: every instance is born single-tenant, so
 * all data is implicitly scoped to DEFAULT_TENANT_ID and the org switcher is
 * hidden — the app behaves exactly as if tenancy didn't exist. Flip to "true"
 * to scope reads/writes by the user's organization membership (see lib/tenant).
 */
export const MULTI_TENANT = process.env.MULTI_TENANT === "true"

// ── Reuniões Gravadas (transcrição) ──────────────────────────────────────────
// The "Reuniões Gravadas" module records audio in the browser, stores it in
// PocketBase and transcribes it. Recording + storage need no key; transcription
// does. Two providers, à-la-carte (the template's golden rule still holds — with
// no key the module records/saves and the transcribe button reports the gap):
//
//   openai   = Whisper (/v1/audio/transcriptions). Plain transcript, no speakers.
//   deepgram = Deepgram (/v1/listen) with diarization → "quem falou o quê"
//              (Locutor 1/2/3…). Set TRANSCRIBE_PROVIDER=deepgram + a key.

export type TranscribeProvider = "openai" | "deepgram" | "assemblyai"

/** Which transcription backend this instance uses (default openai/Whisper). */
export const TRANSCRIBE_PROVIDER: TranscribeProvider =
  process.env.TRANSCRIBE_PROVIDER === "deepgram"
    ? "deepgram"
    : process.env.TRANSCRIBE_PROVIDER === "assemblyai"
      ? "assemblyai"
      : "openai"

/** OpenAI API key (server-side only, never exposed). Empty → transcription off. */
export const OPENAI_API_KEY = process.env.OPENAI_API_KEY ?? ""

/** Whisper model for batch transcription. */
export const OPENAI_TRANSCRIBE_MODEL =
  process.env.OPENAI_TRANSCRIBE_MODEL ?? "whisper-1"

/** OpenAI-compatible base URL (swap for a gateway/proxy without code changes). */
export const OPENAI_BASE_URL =
  process.env.OPENAI_BASE_URL ?? "https://api.openai.com/v1"

/** Deepgram API key (server-side only). Empty → Deepgram transcription off. */
export const DEEPGRAM_API_KEY = process.env.DEEPGRAM_API_KEY ?? ""

/** Deepgram model. nova-3 has better diarization than nova-2. */
export const DEEPGRAM_MODEL = process.env.DEEPGRAM_MODEL ?? "nova-3"

/** AssemblyAI API key (server-side only). Empty → AssemblyAI transcription off. */
export const ASSEMBLYAI_API_KEY = process.env.ASSEMBLYAI_API_KEY ?? ""

/**
 * Show the (experimental) live-transcription toggle in the recorder. Streaming
 * itself is not wired yet — this only surfaces the toggle for a future pass.
 */
export const MEETINGS_REALTIME = process.env.MEETINGS_REALTIME === "true"

/** The key for the active transcription provider (empty when unconfigured). */
export function transcribeProviderKey(): string {
  if (TRANSCRIBE_PROVIDER === "deepgram") return DEEPGRAM_API_KEY
  if (TRANSCRIBE_PROVIDER === "assemblyai") return ASSEMBLYAI_API_KEY
  return OPENAI_API_KEY
}

/**
 * True when a recording can actually be transcribed: data is persisted in
 * PocketBase AND the active provider's key is configured. Gates the transcribe UI.
 */
export function transcriptionEnabled(): boolean {
  return DATA_MODE === "pocketbase" && transcribeProviderKey().length > 0
}

// ── Chamados (service desk) — notifications (optional) ───────────────────────
// The Chamados module always drops an in-app notification (into the core
// `notificacoes` module) on every ticket event. Optionally, point this at an
// outbound webhook (Resend/n8n/Make/Slack/Teams) to ALSO send email/chat
// notifications — each event is POSTed as JSON. Unset → in-app only (the golden
// rule: boots and works with zero required env). See lib/chamados/notify.ts.
export const CHAMADOS_NOTIFY_WEBHOOK = process.env.CHAMADOS_NOTIFY_WEBHOOK ?? ""

// ── Chat — notifications (optional) ──────────────────────────────────────────
// The Chat module drops an in-app notification on a new DM (into the core
// `notificacoes` module). Optionally, point this at an outbound webhook
// (Resend/n8n/Make/Slack/Teams) to ALSO send email/chat notifications — each DM
// event is POSTed as JSON. Unset → in-app only (boots with zero env). Realtime
// itself needs no env: it's relayed server-side from the bundled PocketBase.
export const CHAT_NOTIFY_WEBHOOK = process.env.CHAT_NOTIFY_WEBHOOK ?? ""

// ── Assinatura / Stripe (optional) ───────────────────────────────────────────
// Apps billed monthly by Cold Code Labs get an "Assinatura" module. It does NOT
// render billing data itself — it sends the client into Stripe's own hosted,
// authenticated customer portal (update card, see/download invoices, cancel).
// We keep zero payment data; Stripe owns the whole UI. With nothing configured
// the module explains it's in demo mode (the golden rule: boots with zero env).
//
// Two ways to wire a real instance, simplest first:
//   • STRIPE_PORTAL_URL — the no-code customer-portal LOGIN link
//     (https://billing.stripe.com/p/login/…). One env var, no secret key: the
//     client signs in to Stripe by email. This is the recommended default.
//   • STRIPE_SECRET_KEY + STRIPE_CUSTOMER_ID — when set, the button instead
//     mints a one-time session straight to THIS client's portal (no email step).

/** No-code Stripe customer-portal login link. Set this for the simplest setup. */
export const STRIPE_PORTAL_URL = process.env.STRIPE_PORTAL_URL ?? ""

/** CCL Stripe secret key (server-side only, never exposed). Enables sessions. */
export const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY ?? ""

/** Stripe customer id for THIS instance/client, e.g. `cus_…`. */
export const STRIPE_CUSTOMER_ID = process.env.STRIPE_CUSTOMER_ID ?? ""

/** Stripe API base URL (swap for a gateway/proxy without code changes). */
export const STRIPE_API_BASE =
  process.env.STRIPE_API_BASE ?? "https://api.stripe.com/v1"

/** True when a customer-specific portal session can be minted via the API. */
export function portalSessionConfigured(): boolean {
  return STRIPE_SECRET_KEY.length > 0 && STRIPE_CUSTOMER_ID.length > 0
}

/**
 * True when the "Abrir portal" button can actually reach Stripe — either a
 * static portal link is set, or the API is configured to mint a session.
 */
export function portalEnabled(): boolean {
  return STRIPE_PORTAL_URL.length > 0 || portalSessionConfigured()
}
