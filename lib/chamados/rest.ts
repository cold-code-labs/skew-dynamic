import { revalidatePath } from "next/cache"

import { getSession } from "@/lib/auth/session"
import { pgrest } from "@/lib/data/client"
import { logError, logWarn } from "@/lib/log"

import { CHAMADOS_NOTIFY_WEBHOOK } from "@/config/env"

import {
  normalizePrioridade,
  normalizeStatus,
  ticketRef,
  type Chamado,
  type Comentario,
  type ComentarioTipo,
} from "./types"

import type { ActionResult } from "@/lib/resources/types"
import type { NotifyTipo } from "./notify"

// PostgREST path for the Chamados slice (DATA_MODE=postgrest, the Hauldr tier).
// The same module behaviour as the PocketBase path, but over HTTP against the
// project's `rest` service. RLS is per-user: the data client forwards the GoTrue
// access token, so PostgREST scopes every row to the caller (owner = JWT sub,
// filled by the column default — we never send `owner`). Tables: 0002 migration.

// PostgREST stores timestamps as created_at/updated_at; the app type uses
// created/updated, so map them here. owner stays server-side (never surfaced).
function mapChamado(r: Record<string, unknown>): Chamado {
  return {
    id: r.id as string,
    assunto: (r.assunto as string) ?? "Chamado",
    descricao: (r.descricao as string) ?? "",
    departamento: (r.departamento as string) || "Geral",
    prioridade: normalizePrioridade(r.prioridade),
    status: normalizeStatus(r.status),
    solicitante: (r.solicitante as string) ?? "",
    responsavel: (r.responsavel as string) ?? "",
    created: r.created_at as string,
    updated: r.updated_at as string,
  }
}

// ── Readers ──────────────────────────────────────────────────────────────────

export async function listChamadosRest(): Promise<Chamado[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/chamados?select=*&order=created_at.desc",
  )
  return rows.map(mapChamado)
}

export async function getChamadoRest(id: string): Promise<Chamado | null> {
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/chamados?id=eq.${id}&select=*&limit=1`,
    )
    return rows[0] ? mapChamado(rows[0]) : null
  } catch (e) {
    logWarn("chamados", "getChamadoRest: not found", e, { id })
    return null
  }
}

export async function listComentariosRest(chamadoId: string): Promise<Comentario[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    `/chamados_comentarios?chamado=eq.${chamadoId}&select=*&order=created_at.asc`,
  )
  return rows.map((r) => ({
    id: r.id as string,
    chamado: r.chamado as string,
    autor: (r.autor as string) || "Usuário",
    corpo: (r.corpo as string) ?? "",
    tipo: ((r.tipo as string) === "evento" ? "evento" : "comentario") as ComentarioTipo,
    created: r.created_at as string,
  }))
}

// ── Internal helpers ─────────────────────────────────────────────────────────

/** Insert one row, returning the created record (PostgREST representation). */
async function insert<T>(path: string, body: Record<string, unknown>): Promise<T> {
  const rows = await pgrest<T[]>(path, {
    method: "POST",
    headers: { Prefer: "return=representation" },
    body: JSON.stringify(body),
  })
  return rows[0]
}

/** Append a system "evento" row to a ticket's thread (best-effort). */
async function addEvento(
  chamadoId: string,
  autor: string | undefined,
  corpo: string,
): Promise<void> {
  try {
    await pgrest("/chamados_comentarios", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        chamado: chamadoId,
        autor: autor || "Sistema",
        corpo,
        tipo: "evento",
      }),
    })
  } catch (e) {
    logWarn("chamados", "addEvento failed (timeline entry skipped)", e, { chamadoId })
  }
}

/** Drop an in-app notification (+ optional outbound webhook). Best-effort. */
async function notify(ev: {
  titulo: string
  mensagem: string
  tipo: NotifyTipo
  chamadoId?: string
}): Promise<void> {
  await Promise.allSettled([
    pgrest("/notificacoes", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        titulo: ev.titulo,
        mensagem: ev.mensagem,
        tipo: ev.tipo,
        lida: false,
      }),
    }).catch((e) =>
      logWarn("chamados", "in-app notification write failed", e, {
        chamadoId: ev.chamadoId,
      }),
    ),
    postWebhook(ev),
  ])
}

async function postWebhook(ev: {
  titulo: string
  mensagem: string
  tipo: NotifyTipo
  chamadoId?: string
}): Promise<void> {
  if (!CHAMADOS_NOTIFY_WEBHOOK) return
  try {
    const res = await fetch(CHAMADOS_NOTIFY_WEBHOOK, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ source: "chamados", ...ev, at: new Date().toISOString() }),
    })
    if (!res.ok) {
      logWarn("chamados", "notification webhook returned non-OK", undefined, {
        chamadoId: ev.chamadoId,
        status: res.status,
      })
    }
  } catch (e) {
    logWarn("chamados", "notification webhook POST failed", e, { chamadoId: ev.chamadoId })
  }
}

// ── Writers (the action bodies; capability is gated by the caller) ────────────

export async function criarChamadoRest(form: FormData): Promise<ActionResult> {
  const assunto = String(form.get("assunto") || "").trim()
  if (!assunto) return { ok: false, error: "Informe o assunto do chamado." }
  const descricao = String(form.get("descricao") || "").trim()
  const departamento = String(form.get("departamento") || "Geral").trim()
  const prioridade = normalizePrioridade(form.get("prioridade"))
  const solicitanteForm = String(form.get("solicitante") || "").trim()

  try {
    const user = await getSession()
    const solicitante = solicitanteForm || user?.email || user?.name || "—"

    const rec = await insert<{ id: string }>("/chamados", {
      assunto,
      descricao,
      departamento,
      prioridade,
      status: "Aberto",
      solicitante,
      responsavel: "",
    })

    await addEvento(rec.id, user?.name, `Chamado aberto na fila ${departamento}.`)
    await notify({
      titulo: `Novo chamado ${ticketRef(rec.id)} · ${departamento}`,
      mensagem: `${assunto} (prioridade ${prioridade}).`,
      tipo: prioridade === "Urgente" || prioridade === "Alta" ? "alerta" : "info",
      chamadoId: rec.id,
    })

    revalidatePath("/chamados")
    return { ok: true, message: "Chamado aberto." }
  } catch (e) {
    logError("chamados", "criarChamadoRest", e, { departamento, prioridade })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao abrir o chamado." }
  }
}

export async function comentarChamadoRest(
  chamadoId: string,
  corpo: string,
): Promise<ActionResult> {
  const texto = corpo.trim()
  if (!texto) return { ok: false, error: "Escreva um comentário." }

  try {
    const user = await getSession()
    const chamado = await getChamadoRest(chamadoId)
    if (!chamado) return { ok: false, error: "Chamado não encontrado." }

    await pgrest("/chamados_comentarios", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        chamado: chamadoId,
        autor: user?.name || "Usuário",
        corpo: texto,
        tipo: "comentario",
      }),
    })
    // Touch the ticket so list sort + "updated" reflect activity.
    await pgrest(`/chamados?id=eq.${chamadoId}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ updated_at: new Date().toISOString() }),
    })

    await notify({
      titulo: `Novo comentário em ${ticketRef(chamadoId)}`,
      mensagem: `${user?.name || "Alguém"} comentou em "${chamado.assunto}".`,
      tipo: "info",
      chamadoId,
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true }
  } catch (e) {
    logError("chamados", "comentarChamadoRest", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao comentar." }
  }
}

export async function mudarStatusRest(
  chamadoId: string,
  status: string,
): Promise<ActionResult> {
  const novo = normalizeStatus(status)
  try {
    const user = await getSession()
    const chamado = await getChamadoRest(chamadoId)
    if (!chamado) return { ok: false, error: "Chamado não encontrado." }
    const anterior = chamado.status
    if (anterior === novo) return { ok: true }

    await pgrest(`/chamados?id=eq.${chamadoId}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ status: novo, updated_at: new Date().toISOString() }),
    })
    await addEvento(chamadoId, user?.name, `Status alterado de "${anterior}" para "${novo}".`)
    await notify({
      titulo: `${ticketRef(chamadoId)} · ${novo}`,
      mensagem: `"${chamado.assunto}" agora está "${novo}".`,
      tipo: novo === "Resolvido" ? "sucesso" : "info",
      chamadoId,
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true, message: `Status: ${novo}.` }
  } catch (e) {
    logError("chamados", "mudarStatusRest", e, { chamadoId, status: novo })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao mudar o status." }
  }
}

export async function atribuirChamadoRest(
  chamadoId: string,
  responsavel: string,
): Promise<ActionResult> {
  const nome = responsavel.trim()
  try {
    const user = await getSession()
    const chamado = await getChamadoRest(chamadoId)
    if (!chamado) return { ok: false, error: "Chamado não encontrado." }

    await pgrest(`/chamados?id=eq.${chamadoId}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ responsavel: nome, updated_at: new Date().toISOString() }),
    })
    await addEvento(
      chamadoId,
      user?.name,
      nome ? `Chamado atribuído a ${nome}.` : "Atribuição removida.",
    )
    await notify({
      titulo: `${ticketRef(chamadoId)} atribuído`,
      mensagem: nome
        ? `"${chamado.assunto}" foi atribuído a ${nome}.`
        : `"${chamado.assunto}" ficou sem responsável.`,
      tipo: "info",
      chamadoId,
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true }
  } catch (e) {
    logError("chamados", "atribuirChamadoRest", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atribuir." }
  }
}

export async function excluirChamadoRest(chamadoId: string): Promise<ActionResult> {
  try {
    // chamados_comentarios cascades on the FK, so deleting the ticket is enough.
    await pgrest(`/chamados?id=eq.${chamadoId}`, {
      method: "DELETE",
      headers: { Prefer: "return=minimal" },
    })
    revalidatePath("/chamados")
    return { ok: true, message: "Chamado removido." }
  } catch (e) {
    logError("chamados", "excluirChamadoRest", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}
