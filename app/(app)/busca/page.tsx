import Link from "next/link"
import { Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PageShell } from "@/components/page-shell"
import { isFeatureEnabled } from "@/config/features"
import { RESOURCES } from "@/config/resources"
import { listResource } from "@/lib/resources/data"
import { searchFieldsOf } from "@/lib/resources/types"

export const dynamic = "force-dynamic"

type Hit = { id?: string; label: string; sub?: string }
type Group = { key: string; label: string; hits: Hit[] }

/** Only modules enabled on this instance are searchable. */
function searchableResources() {
  return RESOURCES.filter((def) => isFeatureEnabled(def.key))
}

async function search(q: string): Promise<Group[]> {
  const needle = q.trim().toLowerCase()
  if (!needle) return []

  const groups = await Promise.all(
    searchableResources().map(async (def) => {
      const rows = await listResource(def).catch(() => [])
      const fields = searchFieldsOf(def)
      const primary = def.columns.find((c) => c.primary)?.field ?? def.columns[0]?.field
      const hits: Hit[] = []
      for (const r of rows) {
        const match = fields.some((f) => String(r[f] ?? "").toLowerCase().includes(needle))
        if (match) {
          hits.push({
            id: r.id as string | undefined,
            label: String(r[primary] ?? "—"),
            sub: fields.filter((f) => f !== primary).map((f) => r[f]).filter(Boolean).join(" · "),
          })
        }
      }
      return { key: def.key, label: def.label, hits }
    }),
  )
  return groups.filter((g) => g.hits.length > 0)
}

export default async function BuscaPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q = "" } = await searchParams
  const groups = await search(q)
  const total = groups.reduce((n, g) => n + g.hits.length, 0)

  return (
    <PageShell
      title="Busca global"
      description="Procure em todos os módulos da plataforma de uma vez."
    >
      <form action="/busca" className="flex max-w-xl items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            name="q"
            defaultValue={q}
            placeholder="Buscar clientes, projetos, tarefas…"
            className="pl-9"
            autoFocus
          />
        </div>
        <Button type="submit">Buscar</Button>
      </form>

      {q.trim() === "" ? (
        <p className="text-sm text-muted-foreground">
          Digite um termo para buscar em {searchableResources().length} módulos.
        </p>
      ) : total === 0 ? (
        <div className="rounded-lg border border-dashed py-16 text-center text-sm text-muted-foreground">
          Nenhum resultado para <span className="font-medium text-foreground">“{q}”</span>.
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          <p className="text-sm text-muted-foreground">
            {total} resultado{total === 1 ? "" : "s"} para{" "}
            <span className="font-medium text-foreground">“{q}”</span>
          </p>
          {groups.map((g) => (
            <div key={g.key} className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold">{g.label}</h2>
                <span className="text-xs text-muted-foreground">({g.hits.length})</span>
              </div>
              <div className="overflow-hidden rounded-lg border">
                {g.hits.map((h, i) => (
                  <Link
                    key={h.id ?? i}
                    href={`/${g.key}`}
                    className="flex items-center justify-between gap-3 border-b px-4 py-3 last:border-b-0 hover:bg-accent/50"
                  >
                    <div className="flex min-w-0 flex-col">
                      <span className="truncate text-sm font-medium">{h.label}</span>
                      {h.sub ? (
                        <span className="truncate text-xs text-muted-foreground">{h.sub}</span>
                      ) : null}
                    </div>
                    <span className="shrink-0 text-xs text-muted-foreground">Abrir →</span>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </PageShell>
  )
}
