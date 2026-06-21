import { ResourcePage } from "@/components/resource/resource-page"
import { requireFeature } from "@/config/features"
import { clientes } from "@/config/resources"

export default function ClientesPage() {
  requireFeature("clientes")
  return <ResourcePage def={clientes} />
}
