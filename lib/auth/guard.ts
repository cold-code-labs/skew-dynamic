import { redirect } from "next/navigation"

import { can, type Capability } from "@/config/roles"

import { getSession } from "./session"

// Server-side capability gate for write actions. Returns an error message to
// hand back to the client, or null when allowed. Use at the top of every
// mutating server action so the UI gating (useCan) is never the only check.
export async function requireCapability(capability: Capability): Promise<string | null> {
  const user = await getSession()
  if (!user) return "Sessão expirada. Faça login novamente."
  if (!can(user.role, capability)) {
    return "Você não tem permissão para esta ação."
  }
  return null
}

/**
 * Page-level gate. Bounces unauthenticated users to /login and users without the
 * capability to /dashboard — so a route can't be reached by typing the URL, not
 * just by hiding it in the nav. Call at the top of a protected page.
 */
export async function requirePage(capability: Capability): Promise<void> {
  const user = await getSession()
  if (!user) redirect("/login")
  if (!can(user.role, capability)) redirect("/dashboard")
}
