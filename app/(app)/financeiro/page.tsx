import { ResourcePage } from "@/components/resource/resource-page"
import { requireFeature } from "@/config/features"
import { financeiro } from "@/config/resources"

export default function FinanceiroPage() {
  requireFeature("financeiro")
  return <ResourcePage def={financeiro} />
}
