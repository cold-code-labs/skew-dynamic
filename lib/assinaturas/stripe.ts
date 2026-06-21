import {
  APP_BASE_URL,
  STRIPE_API_BASE,
  STRIPE_CUSTOMER_ID,
  STRIPE_SECRET_KEY,
} from "@/config/env"
import { logWarn } from "@/lib/log"

// Server-side Stripe call for the Assinatura module. Only imported from the
// "use server" action, so the secret key stays on the server. We do exactly one
// thing: mint a one-time billing-portal session for this instance's customer and
// hand back its URL. No SDK, no billing data read — Stripe owns the whole UI.

/**
 * Create a Stripe billing-portal session for the configured customer and return
 * its one-time URL. The portal lets the client update the card, see/download
 * invoices and cancel — all on Stripe's hosted, authenticated UI.
 */
export async function createPortalSession(): Promise<
  { ok: true; url: string } | { ok: false; error: string }
> {
  let res: Response
  try {
    res = await fetch(`${STRIPE_API_BASE}/billing_portal/sessions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        customer: STRIPE_CUSTOMER_ID,
        return_url: `${APP_BASE_URL}/assinaturas`,
      }).toString(),
      cache: "no-store",
    })
  } catch (e) {
    logWarn("assinaturas", "Stripe portal session: network failure", e)
    return {
      ok: false,
      error: e instanceof Error ? `Falha de rede: ${e.message}` : "Falha de rede.",
    }
  }

  let json: { url?: string; error?: { message?: string } }
  try {
    json = (await res.json()) as typeof json
  } catch (e) {
    logWarn("assinaturas", "Stripe portal session: invalid response body", e, {
      status: res.status,
    })
    return { ok: false, error: `Resposta inválida da Stripe (${res.status}).` }
  }
  if (!res.ok) {
    logWarn("assinaturas", "Stripe portal session rejected", undefined, {
      status: res.status,
      detail: json?.error?.message,
    })
    return { ok: false, error: `Stripe recusou a requisição (${json?.error?.message ?? res.status}).` }
  }
  if (!json.url) {
    logWarn("assinaturas", "Stripe portal session: response had no url", undefined, {
      status: res.status,
    })
    return { ok: false, error: "Portal sem URL de retorno." }
  }
  return { ok: true, url: json.url }
}
