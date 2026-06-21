import { redirect } from "next/navigation"

import { AppSidebar } from "@/components/app-sidebar"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { enabledFeatureKeys } from "@/config/features"
import { AuthProvider } from "@/lib/auth/context"
import { getSession } from "@/lib/auth/session"

// Authoritative auth gate for the app shell. Runs server-side on every request
// (works for both stub and logto modes); proxy.ts adds a fast pre-render
// bounce in stub mode. The resolved user seeds the client AuthProvider.
export default async function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const user = await getSession()
  if (!user) redirect("/login")

  return (
    <AuthProvider user={user}>
      <SidebarProvider>
        {/* Feature selection is env-driven (server-only) — resolve it here. */}
        <AppSidebar enabledKeys={enabledFeatureKeys()} />
        <SidebarInset>{children}</SidebarInset>
      </SidebarProvider>
    </AuthProvider>
  )
}
