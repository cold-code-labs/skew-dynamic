import { ResourcePage } from "@/components/resource/resource-page"
import { requireFeature } from "@/config/features"
import { projetos } from "@/config/resources"

export default function ProjetosPage() {
  requireFeature("projetos")
  return <ResourcePage def={projetos} />
}
