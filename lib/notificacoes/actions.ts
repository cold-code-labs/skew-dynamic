"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { getSession } from "@/lib/auth/session"
import { logError } from "@/lib/log"

export type ActionResult = { ok: boolean; error?: string }

/** Mark every unread notification as read. No-op in stub mode. */
export async function markAllRead(): Promise<ActionResult> {
  const user = await getSession()
  if (!user) return { ok: false, error: "Sessão expirada." }
  if (DATA_MODE !== "pocketbase") return { ok: true }

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const unread = await pb
      .collection("notificacoes")
      .getFullList({ filter: "lida = false" })
    for (const n of unread) {
      await pb.collection("notificacoes").update(n.id, { lida: true })
    }
  } catch (e) {
    logError("notificacoes", "markAllRead", e)
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atualizar." }
  }
  revalidatePath("/notificacoes")
  return { ok: true }
}

/** Void-returning wrapper for use directly as a <form action>. */
export async function markAllReadForm(): Promise<void> {
  await markAllRead()
}
