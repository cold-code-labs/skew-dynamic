import { readFileSync } from "node:fs"
import path from "node:path"

import { notFound } from "next/navigation"

import { MODULES } from "./modules"

// ─────────────────────────────────────────────────────────────────────────────
// FEATURE SELECTION — which modules this *instance* ships with.
//
// `APP_FEATURES` (env, server-side) is a comma-separated list of extra module
// keys, e.g. `APP_FEATURES=clientes,financeiro`. Core modules are always on.
//
//   unset / empty  → EVERYTHING on (the showroom default — a bare clone keeps
//                    today's behaviour and demos every module)
//   set            → core + the listed extras only; other modules disappear
//                    from the sidebar, search, and 404 their routes
//
// Provisioners (Heimdall's Ice Breaker) set this env per instance from the
// feature picker. The machine-readable catalog they read is `features.json`
// at the repo root — register new features there too (see CONTRIBUTING).
//
// CLONE PARITY: the env lives only in Coolify, so a bare `git clone` of a
// provisioned instance would have APP_FEATURES unset and fall into showroom
// mode — showing modules that aren't actually live. To avoid that, Ice Breaker
// also bakes the selection into a committed `config/app-features.json`, which
// is read as a FALLBACK below. The env still wins at runtime; the file only
// kicks in when the env is absent (i.e. a local clone). The base template
// ships WITHOUT that file, so the showroom default is preserved.
//
// SERVER-SIDE ONLY: this file reads process.env and the filesystem, so never
// import it from a "use client" component — compute the enabled set in a
// server component (e.g. the app layout) and pass it down as props.
// ─────────────────────────────────────────────────────────────────────────────

/** Modules every instance ships with, regardless of APP_FEATURES. */
export const CORE_FEATURES = [
  "dashboard",
  "notificacoes",
  "busca",
  "arquivos",
  "conta",
  "acessos",
] as const

export function isCoreFeature(key: string): boolean {
  return (CORE_FEATURES as readonly string[]).includes(key)
}

/** core ∪ the given extras, normalised (drops blanks and the "core" sentinel). */
function selectionToSet(keys: string[]): Set<string> {
  const extras = keys
    .map((k) => k.trim().toLowerCase())
    .filter((k) => k && k !== "core")
  return new Set([...CORE_FEATURES, ...extras])
}

// Committed per-instance selection (see CLONE PARITY above). Read once and
// memoised — only consulted when APP_FEATURES is unset, i.e. local clones.
let committedCache: string[] | null | undefined
function readCommittedFeatures(): string[] | null {
  if (committedCache !== undefined) return committedCache
  try {
    const file = path.join(process.cwd(), "config", "app-features.json")
    const parsed = JSON.parse(readFileSync(file, "utf8")) as { features?: unknown }
    committedCache = Array.isArray(parsed.features) ? parsed.features.map(String) : null
  } catch {
    committedCache = null // absent/unreadable → showroom
  }
  return committedCache
}

function parseAppFeatures(): Set<string> | null {
  const raw = (process.env.APP_FEATURES ?? "").trim()
  if (raw) return selectionToSet(raw.split(",")) // env wins (Coolify runtime)
  const committed = readCommittedFeatures()
  if (committed) return selectionToSet(committed) // clone parity fallback
  return null // unset & no file → all modules enabled (showroom)
}

/** Keys of all modules enabled on this instance, in registry order. */
export function enabledFeatureKeys(): string[] {
  const selected = parseAppFeatures()
  const all = MODULES.filter((m) => m.enabled).map((m) => m.key)
  if (!selected) return all
  return all.filter((k) => selected.has(k))
}

export function isFeatureEnabled(key: string): boolean {
  if (isCoreFeature(key)) return true
  const selected = parseAppFeatures()
  return selected ? selected.has(key) : true
}

/**
 * Route guard for a feature's page: 404 when the module is not part of this
 * instance. Call it first thing in the page's server component.
 */
export function requireFeature(key: string): void {
  if (!isFeatureEnabled(key)) notFound()
}
