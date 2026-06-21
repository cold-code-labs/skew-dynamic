import { MEETINGS_REALTIME, transcriptionEnabled } from "@/config/env"
import { requireFeature } from "@/config/features"
import { ReunioesView } from "@/components/reunioes/reunioes-view"
import { listReunioes } from "@/lib/reunioes/meetings"

export default async function ReunioesPage() {
  requireFeature("reunioes")
  const reunioes = await listReunioes()
  return (
    <ReunioesView
      reunioes={reunioes}
      transcribeEnabled={transcriptionEnabled()}
      realtimeEnabled={MEETINGS_REALTIME}
    />
  )
}
