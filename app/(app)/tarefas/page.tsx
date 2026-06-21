import { ResourcePage } from "@/components/resource/resource-page"
import { requireFeature } from "@/config/features"
import { tarefas } from "@/config/resources"

export default function TarefasPage() {
  requireFeature("tarefas")
  return <ResourcePage def={tarefas} />
}
