import * as env from "@/config/env"
import { isFeatureEnabled } from "@/config/features"

import { logInfo, logWarn } from "./log"

// ─────────────────────────────────────────────────────────────────────────────
// BOOT CONFIG SUMMARY — printed once, at server start (via instrumentation.ts).
//
// This is the single most useful thing in the logs of a freshly-deployed
// instance: it states the resolved auth/data modes and, for every optional
// feature this instance ships (APP_FEATURES), whether it's actually wired or
// running in demo mode because an env var is missing. So "why isn't
// transcription/billing working?" is answered the moment the container boots,
// not after digging through a failed user action.
//
// It logs ONLY about features that are enabled on this instance, so the summary
// stays quiet and relevant per deployment.
// ─────────────────────────────────────────────────────────────────────────────

export function logStartupSummary(): void {
  logInfo("boot", "Cold Code Labs template starting", {
    env: process.env.NODE_ENV ?? "unknown",
    auth: env.AUTH_MODE,
    data: env.DATA_MODE,
    multiTenant: env.MULTI_TENANT,
    appBaseUrl: env.APP_BASE_URL,
    logLevel: env.LOG_LEVEL,
  })

  // Writes need a real backend. stub = in-memory demo (nothing persists);
  // postgrest = Hauldr/PostgREST, where ported modules (e.g. chamados) persist
  // per-user via RLS and the rest still return the demo notice; pocketbase =
  // bundled PB. Flag it once so a "nothing saves" report is self-explanatory.
  if (env.DATA_MODE === "stub") {
    logWarn("boot", "DATA_MODE=stub: in-memory demo data, write actions do not persist")
  } else if (env.DATA_MODE === "postgrest") {
    logInfo("boot", `PostgREST data-API at ${env.DATA_API_URL || "(DATA_API_URL unset!)"}`)
  } else {
    logInfo("boot", `PocketBase backend at ${env.POCKETBASE_URL}`)
  }

  if (env.AUTH_MODE === "stub") {
    logWarn("boot", "AUTH_MODE=stub: one-click demo login, no real authentication")
  }

  // ── Reuniões Gravadas (transcription) ──────────────────────────────────────
  if (isFeatureEnabled("reunioes")) {
    if (env.transcribeProviderKey()) {
      logInfo("boot", `reunioes: transcription via ${env.TRANSCRIBE_PROVIDER} (key set)`)
    } else {
      const keyVar = env.TRANSCRIBE_PROVIDER === "deepgram" ? "DEEPGRAM_API_KEY" : "OPENAI_API_KEY"
      logWarn(
        "boot",
        `reunioes: recording works but transcription is OFF — set ${keyVar} (provider=${env.TRANSCRIBE_PROVIDER})`,
      )
    }
  }

  // ── Assinatura (Stripe billing portal) ─────────────────────────────────────
  if (isFeatureEnabled("assinaturas")) {
    if (env.STRIPE_PORTAL_URL) {
      logInfo("boot", "assinaturas: Stripe portal via STRIPE_PORTAL_URL (no-code link)")
    } else if (env.portalSessionConfigured()) {
      logInfo("boot", "assinaturas: Stripe portal via API session (secret key + customer id)")
    } else {
      logWarn(
        "boot",
        "assinaturas: demo mode — set STRIPE_PORTAL_URL, or STRIPE_SECRET_KEY + STRIPE_CUSTOMER_ID",
      )
    }
  }

  // ── Chamados (outbound notification webhook is optional) ────────────────────
  if (isFeatureEnabled("chamados")) {
    logInfo(
      "boot",
      env.CHAMADOS_NOTIFY_WEBHOOK
        ? "chamados: in-app notifications + outbound webhook"
        : "chamados: in-app notifications only (set CHAMADOS_NOTIFY_WEBHOOK to fan out to email/chat)",
    )
  }

  // ── Chat (realtime needs PocketBase; DM webhook is optional) ────────────────
  if (isFeatureEnabled("chat")) {
    if (env.DATA_MODE === "pocketbase") {
      logInfo(
        "boot",
        env.CHAT_NOTIFY_WEBHOOK
          ? "chat: realtime via PocketBase SSE relay · DM notifications in-app + webhook"
          : "chat: realtime via PocketBase SSE relay · DM notifications in-app only (set CHAT_NOTIFY_WEBHOOK to also fan out)",
      )
    } else {
      logWarn(
        "boot",
        "chat: demo mode — channels/DMs are read-only and realtime is OFF (needs DATA_MODE=pocketbase)",
      )
    }
  }
}
