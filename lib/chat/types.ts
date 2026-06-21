// Client-safe types + pure helpers for the Chat module. Kept apart from
// data.ts/actions.ts (which import the server-only PocketBase client) so client
// components can use these without dragging server code into the browser bundle.
// This is the file you tweak per project: rename channels, change who sees what.

import { type RoleKey, resolveRole } from "@/config/roles"

// ── Records ──────────────────────────────────────────────────────────────────

export type ChannelTipo = "canal" | "dm"

export type Channel = {
  id: string
  nome: string
  descricao: string
  slug: string
  tipo: ChannelTipo
  /** RoleKeys that may see a `canal` (empty = everyone logged in). */
  allowedRoles: RoleKey[]
  /** Explicit member ids: overrides for a `canal`, the 2 participants for a `dm`. */
  members: string[]
  icone: string
  created?: string
  updated?: string
}

export type MensagemTipo = "mensagem" | "evento"

export type ChatMessage = {
  id: string
  channel: string
  autor: string
  autorNome: string
  corpo: string
  /** Absolute URL of the attachment, when present. */
  anexoUrl?: string
  tipo: MensagemTipo
  created?: string
}

/** Minimal user shape for the "nova conversa" (DM) picker. */
export type ChatUser = {
  id: string
  nome: string
  email: string
  papel: string
}

// ── Access control (pure) ────────────────────────────────────────────────────
// The single source of truth for "can this user see this channel". Used both to
// build the sidebar (lib/chat/data) and to scope the realtime relay.

export function parseRoles(csv: string | undefined): RoleKey[] {
  return (csv ?? "")
    .split(",")
    .map((r) => r.trim().toLowerCase())
    .filter(Boolean) as RoleKey[]
}

/** Whether `userId` (role `userRole`) may see `channel`. */
export function canSeeChannel(
  userId: string,
  userRole: string | undefined,
  channel: Channel,
): boolean {
  if (channel.members.includes(userId)) return true // explicit member / DM participant
  if (channel.tipo === "dm") return false // DMs are members-only
  if (channel.allowedRoles.length === 0) return true // open canal
  const role = resolveRole(userRole)?.key
  return role ? channel.allowedRoles.includes(role) : false
}

// ── Pure helpers ─────────────────────────────────────────────────────────────

/** Deterministic slug for a DM between two user ids (order-independent). */
export function dmSlug(a: string, b: string): string {
  return `dm_${[a, b].sort().join("_")}`
}

/** The "other" participant of a DM, from the current user's perspective. */
export function dmPartnerId(channel: Channel, userId: string): string | undefined {
  return channel.members.find((m) => m !== userId)
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return "?"
  return (parts[0][0] + (parts[1]?.[0] ?? "")).toUpperCase()
}

export function formatTime(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ""
  return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
}

export function formatDateTime(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ""
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

/** Day label for grouping messages ("Hoje", "Ontem", or a date). */
export function dayLabel(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ""
  const today = new Date()
  const yest = new Date()
  yest.setDate(today.getDate() - 1)
  const same = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  if (same(d, today)) return "Hoje"
  if (same(d, yest)) return "Ontem"
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "long" })
}
