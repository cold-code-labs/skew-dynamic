import { DATA_MODE } from "@/config/env"
import { andFilter, tenantFilter } from "@/lib/tenant"

// Reader for the Storage / Arquivos module. PocketBase stores the file natively
// (S3-compatible if configured); we keep a `name`, `category` and `size` next to
// it so the UI can group and label without reading file bytes.
export type Documento = {
  id?: string
  name: string
  category: string
  size: number
  created?: string
  url?: string
}

const STUB: Documento[] = [
  { name: "Contrato Acme.pdf", category: "Contratos", size: 248_000, created: "2026-06-04" },
  { name: "Proposta Globex.pdf", category: "Propostas", size: 132_500, created: "2026-06-06" },
  { name: "Logo Umbrella.png", category: "Marca", size: 84_200, created: "2026-06-01" },
  { name: "Relatório Q2.xlsx", category: "Relatórios", size: 56_900, created: "2026-06-08" },
  { name: "NF Initech.pdf", category: "Financeiro", size: 41_300, created: "2026-05-29" },
  { name: "Briefing Hooli.docx", category: "Propostas", size: 73_100, created: "2026-06-07" },
]

export async function listDocumentos(): Promise<Documento[]> {
  if (DATA_MODE !== "pocketbase") return STUB

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("documentos").getFullList({
    sort: "name",
    filter: andFilter(await tenantFilter()),
  })
  // The file is a protected PB file on the internal-only PocketBase, so it can't
  // be linked directly — the browser downloads it through the same-origin proxy
  // at /api/arquivos/<id>/download (see that route).
  return recs.map((r) => ({
    id: r.id,
    name: (r.name as string) ?? "arquivo",
    category: (r.category as string) || "Geral",
    size: (r.size as number) ?? 0,
    created: r.created as string,
    url: r.file ? `/api/arquivos/${r.id}/download` : undefined,
  }))
}

/** Group documents by category for the grouped list view. */
export function groupByCategory(docs: Documento[]): [string, Documento[]][] {
  const map = new Map<string, Documento[]>()
  for (const d of docs) {
    const list = map.get(d.category) ?? []
    list.push(d)
    map.set(d.category, list)
  }
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]))
}

export function formatSize(bytes: number): string {
  if (!bytes) return "—"
  const kb = bytes / 1024
  if (kb < 1024) return `${Math.round(kb)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}
