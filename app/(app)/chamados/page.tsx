import { DATA_MODE } from "@/config/env"
import { requireFeature } from "@/config/features"
import { ChamadosView } from "@/components/chamados/chamados-view"
import { listChamados } from "@/lib/chamados/data"

export const dynamic = "force-dynamic"

export default async function ChamadosPage() {
  requireFeature("chamados")
  const chamados = await listChamados()
  return <ChamadosView chamados={chamados} persisted={DATA_MODE === "pocketbase"} />
}
