import { DATA_MODE } from "@/config/env"
import { andFilter, tenantFilter } from "@/lib/tenant"

import { pgrest } from "@/lib/data/client"
import { collectionOf, type ResourceDef, type ResourceRow } from "./types"

// Generic reader for any resource. Mirrors the per-entity seam used elsewhere
// (stub | pocketbase | postgrest) but driven entirely by the ResourceDef, so a
// new module needs no bespoke data code.
export async function listResource(def: ResourceDef): Promise<ResourceRow[]> {
  if (DATA_MODE === "stub") return def.stub

  const collection = collectionOf(def)

  if (DATA_MODE === "pocketbase") {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const recs = await pb.collection(collection).getFullList({
      // Base collections created via the JSVM have no `created` autodate field,
      // so default to sorting by the always-present id rather than -created.
      sort: def.sort ?? "id",
      filter: andFilter(await tenantFilter()),
    })
    return recs.map((r) => ({ ...r })) as ResourceRow[]
  }

  // PostgREST: expects a view/table named after the collection. Always select
  // `id` (row actions edit/delete need it) plus the declared display columns.
  const fields = def.columns.map((c) => c.field).filter((f) => f !== "id")
  const cols = ["id", ...fields].join(",")
  const order = def.sort?.startsWith("-")
    ? `${def.sort.slice(1)}.desc`
    : `${def.sort ?? "id"}.asc`
  return pgrest<ResourceRow[]>(`/${collection}?select=${cols}&order=${order}`)
}
