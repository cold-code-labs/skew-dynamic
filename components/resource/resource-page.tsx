import { listResource } from "@/lib/resources/data"
import type { ResourceDef } from "@/lib/resources/types"

import { ResourceTable } from "./resource-table"

// Server component: fetches the rows for a resource and hands them to the
// client table. A module's page.tsx is then a one-liner:
//   export default () => <ResourcePage def={financeiro} />
export async function ResourcePage({ def }: { def: ResourceDef }) {
  const rows = await listResource(def)
  return <ResourceTable defKey={def.key} rows={rows} />
}
