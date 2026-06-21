import type PocketBase from "pocketbase"

import { CHAMADOS_NOTIFY_WEBHOOK } from "@/config/env"
import { logWarn } from "@/lib/log"

// ─────────────────────────────────────────────────────────────────────────────
// NOTIFICATION SEAM for Chamados.
//
// Every meaningful ticket event (opened, commented, status changed, assigned)
// flows through here. Today it does two things, both best-effort so a
// notification failure can NEVER break the underlying action:
//
//   1. In-app — drops a row into the `notificacoes` collection, so the event
//      shows up in the platform's notification center (the core module).
//   2. Webhook (optional, à-la-carte) — when CHAMADOS_NOTIFY_WEBHOOK is set,
//      POSTs the event as JSON. This is the wire for email/Slack/Teams: point
//      it at a Resend/n8n/Make endpoint and you get outbound notifications with
//      zero code change. Unset → no-op (the golden rule: boots with zero env).
//
// To add email natively later, branch inside `dispatch()` on a new env flag —
// callers don't change.
// ─────────────────────────────────────────────────────────────────────────────

export type NotifyTipo = "info" | "sucesso" | "alerta"

export type ChamadoNotificacao = {
  titulo: string
  mensagem: string
  tipo: NotifyTipo
  /** The ticket this is about (for the webhook payload + deep links). */
  chamadoId?: string
  organization?: string
}

export async function notificarChamado(
  pb: PocketBase,
  ev: ChamadoNotificacao,
): Promise<void> {
  await Promise.allSettled([writeInApp(pb, ev), postWebhook(ev)])
}

async function writeInApp(pb: PocketBase, ev: ChamadoNotificacao): Promise<void> {
  try {
    await pb.collection("notificacoes").create({
      titulo: ev.titulo,
      mensagem: ev.mensagem,
      tipo: ev.tipo,
      lida: false,
      data: new Date().toISOString().slice(0, 10),
      organization: ev.organization ?? "",
    })
  } catch (e) {
    // Notification center is best-effort — never surface to the caller, but log
    // it: a missing `notificacoes` collection on a fresh instance is silent
    // otherwise (the ticket action still succeeds, the bell just stays empty).
    logWarn("chamados", "in-app notification write failed", e, { chamadoId: ev.chamadoId })
  }
}

async function postWebhook(ev: ChamadoNotificacao): Promise<void> {
  if (!CHAMADOS_NOTIFY_WEBHOOK) return
  try {
    const res = await fetch(CHAMADOS_NOTIFY_WEBHOOK, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        source: "chamados",
        ...ev,
        at: new Date().toISOString(),
      }),
    })
    // fetch only rejects on network failure; a 4xx/5xx from the endpoint
    // (wrong URL, auth, downstream error) resolves — surface it too.
    if (!res.ok) {
      logWarn("chamados", "notification webhook returned non-OK", undefined, {
        chamadoId: ev.chamadoId,
        status: res.status,
      })
    }
  } catch (e) {
    // Outbound notification is best-effort — log so a broken webhook URL is
    // visible without breaking ticket actions.
    logWarn("chamados", "notification webhook POST failed", e, {
      chamadoId: ev.chamadoId,
    })
  }
}
