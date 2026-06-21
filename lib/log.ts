import { LOG_LEVEL } from "@/config/env"

// ─────────────────────────────────────────────────────────────────────────────
// STRUCTURED SERVER LOGGER — one seam for ALL server-side diagnostics.
//
// Every module logs through here instead of calling console.* directly, so a
// fresh deployment's container logs carry a consistent, greppable record of
// what failed and why. The golden rule of this template is "boots with zero
// env"; the corollary is "when something IS misconfigured, the logs say so".
//
//   logError("chamados", "criarChamado", e, { departamento })
//   → [tpl] ERROR chamados: criarChamado — PocketBase 400 .../chamados/records
//          :: assunto: Cannot be blank. | departamento=TI
//
// User-facing copy stays friendly + Portuguese (returned by the actions); the
// real technical detail lands here, on stderr, where the operator can see it.
//
// To ship logs elsewhere later (a drain, Sentry, Logflare) wire it once in
// `emit()` — none of the call sites change. Server-side only: never import from
// a "use client" component (it reads config/env, which is server-only).
// ─────────────────────────────────────────────────────────────────────────────

type Level = "debug" | "info" | "warn" | "error"

const ORDER: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 }

// Resolve the active threshold once. "silent" mutes everything.
const THRESHOLD = LOG_LEVEL === "silent" ? Infinity : ORDER[LOG_LEVEL]

const PREFIX = "[tpl]"

/**
 * Turn any thrown value into a single, information-dense line. PocketBase's
 * `ClientResponseError` is the common case and the most worth unpacking: its
 * `.message` is generic ("Failed to create record.") while the actionable
 * detail — HTTP status, URL, and per-field validation errors — lives on
 * `.status`/`.url`/`.response.data`. Plain Errors and anything else degrade
 * gracefully.
 */
export function describeError(e: unknown): string {
  if (e == null) return "unknown error"
  if (typeof e === "string") return e

  const err = e as {
    status?: number
    url?: string
    name?: string
    message?: string
    isAbort?: boolean
    response?: {
      message?: string
      data?: Record<string, { code?: string; message?: string }>
    }
  }

  // PocketBase ClientResponseError (has a numeric status + a response/url).
  if (typeof err.status === "number" && (err.url || err.response)) {
    const parts = [`PocketBase ${err.status}`]
    if (err.url) parts.push(err.url)
    const data = err.response?.data
    const fields = data ? Object.entries(data) : []
    if (fields.length > 0) {
      parts.push(
        ":: " +
          fields
            .map(([f, v]) => `${f}: ${v?.message ?? v?.code ?? "invalid"}`)
            .join("; "),
      )
    } else {
      const msg = err.response?.message || err.message
      if (msg) parts.push(`:: ${msg}`)
    }
    if (err.isAbort) parts.push("(aborted)")
    return parts.join(" ")
  }

  if (e instanceof Error) return `${e.name}: ${e.message}`

  try {
    return JSON.stringify(e)
  } catch {
    return String(e)
  }
}

function formatMeta(meta: Record<string, unknown>): string {
  return Object.entries(meta)
    .map(([k, v]) => {
      const val =
        v === null || v === undefined
          ? ""
          : typeof v === "object"
            ? safeJson(v)
            : String(v)
      return `${k}=${val}`
    })
    .join(" ")
}

function safeJson(v: unknown): string {
  try {
    return JSON.stringify(v)
  } catch {
    return String(v)
  }
}

function emit(
  level: Level,
  scope: string,
  message: string,
  detail?: string,
  meta?: Record<string, unknown>,
): void {
  if (ORDER[level] < THRESHOLD) return
  const metaStr = meta && Object.keys(meta).length ? ` | ${formatMeta(meta)}` : ""
  const line =
    `${PREFIX} ${level.toUpperCase()} ${scope}: ${message}` +
    (detail ? ` — ${detail}` : "") +
    metaStr
  // eslint-disable-next-line no-console
  const sink = level === "error" ? console.error : level === "warn" ? console.warn : console.log
  sink(line)
}

/**
 * Log a caught failure. `scope` is the module/area ("chamados", "boot"),
 * `message` the operation ("criarChamado"); `err` is the thrown value (unpacked
 * via describeError), and `meta` carries any extra context worth grepping for.
 */
export function logError(
  scope: string,
  message: string,
  err?: unknown,
  meta?: Record<string, unknown>,
): void {
  emit("error", scope, message, err !== undefined ? describeError(err) : undefined, meta)
}

/** Like logError, for recoverable / best-effort failures (degraded, not broken). */
export function logWarn(
  scope: string,
  message: string,
  err?: unknown,
  meta?: Record<string, unknown>,
): void {
  emit("warn", scope, message, err !== undefined ? describeError(err) : undefined, meta)
}

/** Informational line (boot summary, lifecycle). No error attached. */
export function logInfo(scope: string, message: string, meta?: Record<string, unknown>): void {
  emit("info", scope, message, undefined, meta)
}

/** Verbose line, only emitted at LOG_LEVEL=debug. */
export function logDebug(scope: string, message: string, meta?: Record<string, unknown>): void {
  emit("debug", scope, message, undefined, meta)
}
