import { portalEnabled } from "@/config/env"
import { requireFeature } from "@/config/features"
import { AssinaturaView } from "@/components/assinaturas/assinatura-view"
import { requirePage } from "@/lib/auth/guard"

export default async function AssinaturasPage() {
  requireFeature("assinaturas")
  // Billing is sensitive — owners/managers only (matches the sidebar gating).
  await requirePage("settings.manage")
  return <AssinaturaView portalEnabled={portalEnabled()} />
}
