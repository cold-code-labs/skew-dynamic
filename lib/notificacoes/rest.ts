import { revalidatePath } from "next/cache"

import { pgrest } from "@/lib/data/client"
import { logError } from "@/lib/log"

import type { Notificacao } from "./data"
import type { ActionResult } from "./actions"

// PostgREST path for the Notificacoes module (DATA_MODE=postgrest, Hauldr tier).
// The `notificacoes` table ships in migration 0002 (chamados writes to it), so
// no extra DDL is needed here. RLS is per-user (owner = JWT sub); the data
// client forwards the GoTrue access token so PostgREST scopes every row.

function mapNotificacao(r: Record<string, unknown>): Notificacao {
  return {
    id: r.id as string,
    titulo: (r.titulo as string) ?? "",
    mensagem: (r.mensagem as string) ?? "",
    tipo: (r.tipo as string) ?? "info",
    lida: Boolean(r.lida),
    data: (r.data as string) ?? "",
  }
}

export async function listNotificacoesRest(): Promise<Notificacao[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/notificacoes?select=*&order=data.desc,created_at.desc",
  )
  return rows.map(mapNotificacao)
}

export async function markAllReadRest(): Promise<ActionResult> {
  try {
    await pgrest("/notificacoes?lida=eq.false", {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ lida: true }),
    })
    revalidatePath("/notificacoes")
    return { ok: true }
  } catch (e) {
    logError("notificacoes", "markAllReadRest", e)
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atualizar." }
  }
}
