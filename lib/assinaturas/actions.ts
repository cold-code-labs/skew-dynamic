"use server"

import { portalSessionConfigured, STRIPE_PORTAL_URL } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"

// Server action for the Assinatura module. Returns a URL the client redirects to
// so the customer can manage their CCL subscription in Stripe's hosted portal.
// Two paths, simplest first:
//   • STRIPE_PORTAL_URL set → use the no-code portal login link directly.
//   • else, API configured → mint a one-time billing-portal session on Stripe.
// In demo mode (neither configured) it returns a friendly notice.

export type PortalResult =
  | { ok: true; url: string }
  | { ok: false; error: string }

export async function abrirPortal(): Promise<PortalResult> {
  const denied = await requireCapability("settings.manage")
  if (denied) return { ok: false, error: denied }

  if (STRIPE_PORTAL_URL) return { ok: true, url: STRIPE_PORTAL_URL }

  if (!portalSessionConfigured()) {
    return {
      ok: false,
      error:
        "Modo demonstração: configure o Stripe (STRIPE_PORTAL_URL, ou STRIPE_SECRET_KEY + STRIPE_CUSTOMER_ID) para abrir o portal.",
    }
  }

  const { createPortalSession } = await import("./stripe")
  return createPortalSession()
}
