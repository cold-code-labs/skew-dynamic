"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { getSession } from "@/lib/auth/session"
import { logError } from "@/lib/log"
import { getCurrentTenantId } from "@/lib/tenant"

import { getChannel, listChannelsForUser, listMessages } from "./data"
import { notificarChat } from "./notify"
import { dmSlug, parseRoles, type Channel, type ChatMessage } from "./types"

import type { ActionResult } from "@/lib/resources/types"

// Load the messages of a channel the user may see — used by the client when
// switching conversations. Returns [] when access is denied (no leak).
export async function carregarMensagens(channelId: string): Promise<ChatMessage[]> {
  const user = await getSession()
  if (!user) return []
  const channel = await getChannel(channelId, user)
  if (!channel) return []
  return listMessages(channelId)
}

// Refresh the conversation list (after creating a DM/channel or editing members)
// without a full page reload.
export async function carregarCanais(): Promise<Channel[]> {
  const user = await getSession()
  if (!user) return []
  return listChannelsForUser(user)
}

const DEMO: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase para usar o chat.",
}

// Send a message into a channel the user can see. Text + optional single file.
// DMs ping the recipient via the notification center; channels stay quiet (the
// realtime stream is the live signal there).
export async function enviarMensagem(
  channelId: string,
  form: FormData,
): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO

  const corpo = String(form.get("corpo") || "").trim()
  const anexo = form.get("anexo")
  const hasAnexo = anexo instanceof File && anexo.size > 0
  if (!corpo && !hasAnexo) return { ok: false, error: "Escreva uma mensagem." }

  try {
    const user = await getSession()
    if (!user) return { ok: false, error: "Sessão expirada." }
    const channel = await getChannel(channelId, user)
    if (!channel) return { ok: false, error: "Canal indisponível." }

    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const organization = await getCurrentTenantId()

    const payload: Record<string, unknown> = {
      channel: channelId,
      autor: user.id,
      autor_nome: user.name,
      corpo,
      tipo: "mensagem",
      organization,
    }
    if (hasAnexo) payload.anexo = anexo

    await pb.collection("chat_messages").create(payload)
    // Touch the channel so the sidebar's recency sort reflects activity.
    try {
      await pb.collection("chat_channels").update(channelId, {})
    } catch (_) {}

    if (channel.tipo === "dm") {
      await notificarChat(pb, {
        titulo: `Nova mensagem de ${user.name}`,
        mensagem: corpo || "Enviou um anexo.",
        channelId,
        organization,
      })
    }

    revalidatePath("/chat")
    return { ok: true }
  } catch (e) {
    logError("chat", "enviarMensagem", e, { channelId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao enviar." }
  }
}

// Find-or-create a 1:1 DM with another user. Idempotent via the deterministic
// slug, so re-opening the same conversation never duplicates it. Returns the
// channel id so the UI can select it.
export async function iniciarDM(
  outroUserId: string,
): Promise<ActionResult & { channelId?: string }> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO

  try {
    const user = await getSession()
    if (!user) return { ok: false, error: "Sessão expirada." }
    if (!outroUserId || outroUserId === user.id) {
      return { ok: false, error: "Selecione um destinatário." }
    }
    const slug = dmSlug(user.id, outroUserId)
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()

    try {
      const existing = await pb.collection("chat_channels").getFirstListItem(`slug = "${slug}"`)
      return { ok: true, channelId: existing.id }
    } catch (_) {
      // not found → create
    }

    // `nome` is required on the collection; for a DM it's just a stored fallback
    // (the reader resolves the display name to the *other* participant per-user),
    // so seed it with the partner's name rather than an empty string.
    let partnerName = "Mensagem direta"
    try {
      const partner = await pb.collection("users").getOne(outroUserId)
      partnerName = (partner.name as string) || (partner.email as string) || partnerName
    } catch (_) {}

    const rec = await pb.collection("chat_channels").create({
      nome: partnerName,
      slug,
      descricao: "",
      tipo: "dm",
      allowed_roles: "",
      members: [user.id, outroUserId],
      organization: await getCurrentTenantId(),
    })
    revalidatePath("/chat")
    return { ok: true, channelId: rec.id }
  } catch (e) {
    logError("chat", "iniciarDM", e, { outroUserId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao iniciar conversa." }
  }
}

// Create a role-gated group channel. Restricted to people who manage members
// (Direção/admin) — this is where "Direção cria um canal" happens.
export async function criarCanal(form: FormData): Promise<ActionResult & { channelId?: string }> {
  const denied = await requireCapability("members.manage")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO

  const nome = String(form.get("nome") || "").trim()
  if (!nome) return { ok: false, error: "Informe o nome do canal." }
  const descricao = String(form.get("descricao") || "").trim()
  // allowed_roles arrives as comma-separated RoleKeys; normalise via parseRoles.
  const allowedRoles = parseRoles(String(form.get("allowed_roles") || "")).join(",")
  const slug = slugify(nome)

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const rec = await pb.collection("chat_channels").create({
      nome,
      slug,
      descricao,
      tipo: "canal",
      allowed_roles: allowedRoles,
      members: [],
      icone: "Hash",
      organization: await getCurrentTenantId(),
    })
    revalidatePath("/chat")
    return { ok: true, channelId: rec.id, message: "Canal criado." }
  } catch (e) {
    logError("chat", "criarCanal", e, { nome })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao criar canal." }
  }
}

// Replace a channel's explicit member overrides — the "adicionar alguém a um
// canal" flow. Members see the channel regardless of their role.
export async function gerenciarMembros(
  channelId: string,
  memberIds: string[],
): Promise<ActionResult> {
  const denied = await requireCapability("members.manage")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const current = await pb.collection("chat_channels").getOne(channelId)
    const channel: Channel = {
      id: current.id,
      nome: (current.nome as string) ?? "",
      descricao: "",
      slug: (current.slug as string) ?? "",
      tipo: (current.tipo as string) === "dm" ? "dm" : "canal",
      allowedRoles: parseRoles(current.allowed_roles as string),
      members: Array.isArray(current.members) ? (current.members as string[]) : [],
      icone: "",
    }
    if (channel.tipo === "dm") return { ok: false, error: "DMs não têm gestão de membros." }

    await pb.collection("chat_channels").update(channelId, { members: memberIds })
    revalidatePath("/chat")
    return { ok: true, message: "Membros atualizados." }
  } catch (e) {
    logError("chat", "gerenciarMembros", e, { channelId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atualizar membros." }
  }
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40)
}
