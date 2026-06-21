import { notFound } from "next/navigation"

import { DATA_MODE } from "@/config/env"
import { requireFeature } from "@/config/features"
import { ReuniaoEditor } from "@/components/reunioes/reuniao-editor"
import { getReuniao } from "@/lib/reunioes/meetings"

export const dynamic = "force-dynamic"

export default async function ReuniaoDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  requireFeature("reunioes")
  const { id } = await params
  const reuniao = await getReuniao(id)
  if (!reuniao) notFound()

  return <ReuniaoEditor reuniao={reuniao} persisted={DATA_MODE !== "stub"} />
}
