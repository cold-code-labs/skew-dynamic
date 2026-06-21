import { notFound } from "next/navigation"

import { DATA_MODE } from "@/config/env"
import { requireFeature } from "@/config/features"
import { ChamadoDetail } from "@/components/chamados/chamado-detail"
import { getChamado, listComentarios } from "@/lib/chamados/data"

export const dynamic = "force-dynamic"

export default async function ChamadoDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  requireFeature("chamados")
  const { id } = await params
  const chamado = await getChamado(id)
  if (!chamado) notFound()
  const comentarios = await listComentarios(id)

  return (
    <ChamadoDetail
      chamado={chamado}
      comentarios={comentarios}
      persisted={DATA_MODE === "pocketbase"}
    />
  )
}
