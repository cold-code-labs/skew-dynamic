"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { getSession } from "@/lib/auth/session"
import { logError, logWarn } from "@/lib/log"
import { getCurrentTenantId } from "@/lib/tenant"

import { notificarChamado } from "./notify"
import { normalizePrioridade, normalizeStatus, ticketRef } from "./types"

import type { ActionResult } from "@/lib/resources/types"

const DEMO: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase para gerir chamados.",
}

// Open a new ticket. Anyone who can write data can open one. Drops a thread
// "evento" so the timeline starts populated, and fires a notification.
export async function criarChamado(form: FormData): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { criarChamadoRest } = await import("./rest")
    return criarChamadoRest(form)
  }
  if (DATA_MODE !== "pocketbase") return DEMO

  const assunto = String(form.get("assunto") || "").trim()
  if (!assunto) return { ok: false, error: "Informe o assunto do chamado." }
  const descricao = String(form.get("descricao") || "").trim()
  const departamento = String(form.get("departamento") || "Geral").trim()
  const prioridade = normalizePrioridade(form.get("prioridade"))
  const solicitanteForm = String(form.get("solicitante") || "").trim()

  try {
    const user = await getSession()
    const solicitante = solicitanteForm || user?.email || user?.name || "—"
    const organization = await getCurrentTenantId()
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()

    const rec = await pb.collection("chamados").create({
      assunto,
      descricao,
      departamento,
      prioridade,
      status: "Aberto",
      solicitante,
      responsavel: "",
      organization,
    })

    await addEvento(pb, rec.id, user?.name, `Chamado aberto na fila ${departamento}.`)
    await notificarChamado(pb, {
      titulo: `Novo chamado ${ticketRef(rec.id)} · ${departamento}`,
      mensagem: `${assunto} (prioridade ${prioridade}).`,
      tipo: prioridade === "Urgente" || prioridade === "Alta" ? "alerta" : "info",
      chamadoId: rec.id,
      organization,
    })

    revalidatePath("/chamados")
    return { ok: true, message: "Chamado aberto." }
  } catch (e) {
    logError("chamados", "criarChamado", e, { departamento, prioridade })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao abrir o chamado." }
  }
}

// Post a comment on the thread. Notifies so the other side is pinged.
export async function comentarChamado(
  chamadoId: string,
  corpo: string,
): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { comentarChamadoRest } = await import("./rest")
    return comentarChamadoRest(chamadoId, corpo)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  const texto = corpo.trim()
  if (!texto) return { ok: false, error: "Escreva um comentário." }

  try {
    const user = await getSession()
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const chamado = await pb.collection("chamados").getOne(chamadoId)

    await pb.collection("chamados_comentarios").create({
      chamado: chamadoId,
      autor: user?.name || "Usuário",
      corpo: texto,
      tipo: "comentario",
      organization: (chamado.organization as string) || "",
    })
    // Touch the ticket so list sort (-created) and "updated" reflect activity.
    await pb.collection("chamados").update(chamadoId, {})

    await notificarChamado(pb, {
      titulo: `Novo comentário em ${ticketRef(chamadoId)}`,
      mensagem: `${user?.name || "Alguém"} comentou em "${chamado.assunto as string}".`,
      tipo: "info",
      chamadoId,
      organization: (chamado.organization as string) || "",
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true }
  } catch (e) {
    logError("chamados", "comentarChamado", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao comentar." }
  }
}

// Move the ticket along its workflow. Logs an event + notifies; resolving is a
// "sucesso" notification.
export async function mudarStatus(
  chamadoId: string,
  status: string,
): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { mudarStatusRest } = await import("./rest")
    return mudarStatusRest(chamadoId, status)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  const novo = normalizeStatus(status)

  try {
    const user = await getSession()
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const chamado = await pb.collection("chamados").getOne(chamadoId)
    const anterior = chamado.status as string
    if (anterior === novo) return { ok: true }

    await pb.collection("chamados").update(chamadoId, { status: novo })
    await addEvento(
      pb,
      chamadoId,
      user?.name,
      `Status alterado de "${anterior}" para "${novo}".`,
    )
    await notificarChamado(pb, {
      titulo: `${ticketRef(chamadoId)} · ${novo}`,
      mensagem: `"${chamado.assunto as string}" agora está "${novo}".`,
      tipo: novo === "Resolvido" ? "sucesso" : "info",
      chamadoId,
      organization: (chamado.organization as string) || "",
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true, message: `Status: ${novo}.` }
  } catch (e) {
    logError("chamados", "mudarStatus", e, { chamadoId, status: novo })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao mudar o status." }
  }
}

// Assign (or unassign with an empty string) the ticket to an agent.
export async function atribuirChamado(
  chamadoId: string,
  responsavel: string,
): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { atribuirChamadoRest } = await import("./rest")
    return atribuirChamadoRest(chamadoId, responsavel)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  const nome = responsavel.trim()

  try {
    const user = await getSession()
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const chamado = await pb.collection("chamados").getOne(chamadoId)

    await pb.collection("chamados").update(chamadoId, { responsavel: nome })
    await addEvento(
      pb,
      chamadoId,
      user?.name,
      nome ? `Chamado atribuído a ${nome}.` : "Atribuição removida.",
    )
    await notificarChamado(pb, {
      titulo: `${ticketRef(chamadoId)} atribuído`,
      mensagem: nome
        ? `"${chamado.assunto as string}" foi atribuído a ${nome}.`
        : `"${chamado.assunto as string}" ficou sem responsável.`,
      tipo: "info",
      chamadoId,
      organization: (chamado.organization as string) || "",
    })

    revalidatePath(`/chamados/${chamadoId}`)
    revalidatePath("/chamados")
    return { ok: true }
  } catch (e) {
    logError("chamados", "atribuirChamado", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atribuir." }
  }
}

export async function excluirChamado(chamadoId: string): Promise<ActionResult> {
  const denied = await requireCapability("data.delete")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { excluirChamadoRest } = await import("./rest")
    return excluirChamadoRest(chamadoId)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    // Remove the thread first (cascadeDelete also covers this; explicit is safe).
    const comentarios = await pb
      .collection("chamados_comentarios")
      .getFullList({ filter: `chamado = "${chamadoId}"` })
    for (const c of comentarios) {
      await pb.collection("chamados_comentarios").delete(c.id)
    }
    await pb.collection("chamados").delete(chamadoId)
    revalidatePath("/chamados")
    return { ok: true, message: "Chamado removido." }
  } catch (e) {
    logError("chamados", "excluirChamado", e, { chamadoId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}

// Internal: append a system "evento" row to a ticket's thread.
async function addEvento(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pb: any,
  chamadoId: string,
  autor: string | undefined,
  corpo: string,
): Promise<void> {
  try {
    await pb.collection("chamados_comentarios").create({
      chamado: chamadoId,
      autor: autor || "Sistema",
      corpo,
      tipo: "evento",
    })
  } catch (e) {
    // The event log is best-effort; never block the primary mutation — but do
    // surface it, since a silently empty timeline is otherwise baffling.
    logWarn("chamados", "addEvento failed (timeline entry skipped)", e, { chamadoId })
  }
}
