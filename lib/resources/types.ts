import type { LucideIcon } from "lucide-react"

// ─────────────────────────────────────────────────────────────────────────────
// The generic resource engine. A "resource" is a declarative description of a
// collection of records: its columns, its create/edit fields, and demo data.
// From one of these we render a full screen — searchable table, create/edit
// sheet, row actions — and back it with PocketBase (or stub data). Most custom
// modules (Financeiro, Projetos, Suporte…) are JUST one of these declarations.
// ─────────────────────────────────────────────────────────────────────────────

export type BadgeVariant = "default" | "secondary" | "outline" | "destructive"

/** How a column's value is rendered in the table. */
export type ColumnType =
  | "text" // plain
  | "muted" // dimmed (secondary info)
  | "email" // dimmed, monospace-ish
  | "badge" // pill, colored via `badges`
  | "currency" // number → R$ 1.234,56
  | "date" // ISO/date string → dd/mm/aaaa

export type ResourceColumn = {
  /** Record field this column reads. */
  field: string
  label: string
  type?: ColumnType
  /** For type "badge": map a value → badge variant. */
  badges?: Record<string, BadgeVariant>
  /** Mark the identity column (renders with an avatar lettermark). */
  primary?: boolean
}

/** How a field is edited in the create/edit sheet. */
export type FieldType = "text" | "textarea" | "email" | "number" | "select" | "date"

export type ResourceField = {
  field: string
  label: string
  type?: FieldType
  required?: boolean
  placeholder?: string
  /** For type "select". */
  options?: string[]
}

/** A row is just a bag of values keyed by field name. */
export type ResourceRow = Record<string, string | number | null | undefined> & {
  id?: string
}

export type ResourceDef = {
  /** Stable key — also the URL segment (/<key>) and PocketBase collection name. */
  key: string
  /** PocketBase collection name (defaults to `key`). */
  collection?: string
  /** Sidebar + page labels. */
  label: string
  singular: string
  description: string
  icon: LucideIcon
  /** Which sidebar group this module sits in. */
  group?: "operacoes" | "configuracoes"
  /** Default sort field for PocketBase queries. */
  sort?: string
  columns: ResourceColumn[]
  /** Fields shown in the create/edit sheet. Omit → read-only showroom screen. */
  fields?: ResourceField[]
  /** Fields matched by the search box (defaults to the primary column). */
  searchFields?: string[]
  /** Demo data shown in stub mode (and mirrored into the PocketBase seed). */
  stub: ResourceRow[]
}

/** Result shape returned by every write server action. */
export type ActionResult = { ok: boolean; error?: string; message?: string }

export function collectionOf(def: ResourceDef): string {
  return def.collection ?? def.key
}

export function searchFieldsOf(def: ResourceDef): string[] {
  if (def.searchFields?.length) return def.searchFields
  const primary = def.columns.find((c) => c.primary) ?? def.columns[0]
  return primary ? [primary.field] : []
}
