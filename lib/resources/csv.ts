import type { ResourceColumn, ResourceRow } from "./types"

// Client-side CSV export. Builds a UTF-8 CSV (with BOM so Excel/pt-BR opens it
// correctly) from the resource columns + the currently shown rows.
function escape(value: unknown): string {
  const s = String(value ?? "")
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

export function downloadCsv(
  filename: string,
  columns: ResourceColumn[],
  rows: ResourceRow[],
): void {
  const header = columns.map((c) => escape(c.label)).join(",")
  const body = rows
    .map((r) => columns.map((c) => escape(r[c.field])).join(","))
    .join("\n")
  const csv = `﻿${header}\n${body}`
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
