import type { ResourceRow } from "./types"

// Display formatters shared by the table cells. Locale is pt-BR.

const BRL = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

export function formatCurrency(value: unknown): string {
  const n = typeof value === "number" ? value : Number(value)
  return Number.isFinite(n) ? BRL.format(n) : "—"
}

export function formatDate(value: unknown): string {
  if (!value) return "—"
  const d = new Date(String(value))
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" })
}

export function initials(name: string): string {
  return (
    name
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "—"
  )
}

/** Case-insensitive match of a row against a query over the given fields. */
export function rowMatches(row: ResourceRow, fields: string[], query: string): boolean {
  if (!query) return true
  const q = query.toLowerCase()
  return fields.some((f) => String(row[f] ?? "").toLowerCase().includes(q))
}
