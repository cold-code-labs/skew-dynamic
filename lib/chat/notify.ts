import type PocketBase from "pocketbase"

import { CHAT_NOTIFY_WEBHOOK } from "@/config/env"
import { logWarn } from "@/lib/log"

// Notification seam for Chat — mirrors lib/chamados/notify.ts. Best-effort:
// a notification failure can NEVER break sending a message.
//
//   1. In-app — drops a row into `notificacoes` (the core notification center).
//   2. Webhook (optional) — when CHAT_NOTIFY_WEBHOOK is set, POSTs the event as
//      JSON (Resend/n8n/Make/Slack/Teams). Unset → in-app only.

export type ChatNotificacao = {
  titulo: string
  mensagem: string
  channelId: string
  organization?: string
}

export async function notificarChat(pb: PocketBase, ev: ChatNotificacao): Promise<void> {
  await Promise.allSettled([writeInApp(pb, ev), postWebhook(ev)])
}

async function writeInApp(pb: PocketBase, ev: ChatNotificacao): Promise<void> {
  try {
    await pb.collection("notificacoes").create({
      titulo: ev.titulo,
      mensagem: ev.mensagem,
      tipo: "info",
      lida: false,
      data: new Date().toISOString().slice(0, 10),
      organization: ev.organization ?? "",
    })
  } catch (e) {
    logWarn("chat", "in-app notification write failed", e, { channelId: ev.channelId })
  }
}

async function postWebhook(ev: ChatNotificacao): Promise<void> {
  if (!CHAT_NOTIFY_WEBHOOK) return
  try {
    const res = await fetch(CHAT_NOTIFY_WEBHOOK, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ source: "chat", ...ev, at: new Date().toISOString() }),
    })
    if (!res.ok) {
      logWarn("chat", "notification webhook returned non-OK", undefined, {
        channelId: ev.channelId,
        status: res.status,
      })
    }
  } catch (e) {
    logWarn("chat", "notification webhook POST failed", e, { channelId: ev.channelId })
  }
}
