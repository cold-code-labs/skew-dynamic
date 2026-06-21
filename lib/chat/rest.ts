import { revalidatePath } from "next/cache"

import type { SessionUser } from "@/lib/auth/types"
import { pgrest } from "@/lib/data/client"
import { logWarn } from "@/lib/log"

import {
  canSeeChannel,
  dmPartnerId,
  dmSlug,
  parseRoles,
  type Channel,
  type ChatMessage,
  type ChatUser,
} from "./types"

import type { ActionResult } from "@/lib/resources/types"

// PostgREST path for the Chat module (DATA_MODE=postgrest, Hauldr tier). Tables
// in migration 0006 use a shared-workspace RLS (authenticated gate); visibility
// is filtered HERE via canSeeChannel, exactly like the PocketBase path. The user
// directory is the `usuarios` table; we upsert the caller (id = GoTrue sub) on
// every directory read so DMs resolve to real login identities.
//
// Notes vs PocketBase: attachments (anexo) are deferred to the storage module;
// the cross-user DM notification ping is skipped (per-user notificacoes RLS
// blocks writing a row owned by the recipient) — realtime is the live signal.

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40)
}

function safeName(name: string): string {
  return name.replace(/[^a-zA-Z0-9._-]+/g, "_").slice(0, 120) || "anexo"
}

function mapChannel(r: Record<string, unknown>): Channel {
  const members = Array.isArray(r.members) ? (r.members as string[]) : []
  return {
    id: r.id as string,
    nome: (r.nome as string) ?? "Canal",
    descricao: (r.descricao as string) ?? "",
    slug: (r.slug as string) ?? "",
    tipo: (r.tipo as string) === "dm" ? "dm" : "canal",
    allowedRoles: parseRoles(r.allowed_roles as string),
    members,
    icone: (r.icone as string) ?? "",
    created: r.created_at as string,
    updated: r.updated_at as string,
  }
}

// ── Directory (usuarios doubles as the chat user list) ───────────────────────

/** Upsert the caller into the directory so DMs key on a real login identity. */
async function ensureDirectory(user: SessionUser): Promise<void> {
  try {
    await pgrest("/usuarios", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        id: user.id,
        nome: user.name,
        email: user.email,
        papel: user.role || "Membro",
        status: "Ativo",
      }),
    })
  } catch (e) {
    logWarn("chat", "ensureDirectory upsert failed", e, { id: user.id })
  }
}

export async function listChatUsersRest(
  me: SessionUser,
  excludeId?: string,
): Promise<ChatUser[]> {
  await ensureDirectory(me)
  const rows = await pgrest<Record<string, unknown>[]>(
    "/usuarios?select=id,nome,email,papel&order=nome.asc",
  )
  return rows
    .map((r) => ({
      id: r.id as string,
      nome: (r.nome as string) || (r.email as string) || "Usuário",
      email: (r.email as string) ?? "",
      papel: (r.papel as string) || "Membro",
    }))
    .filter((u) => u.id !== excludeId)
}

async function userNames(ids: string[]): Promise<Map<string, string>> {
  const map = new Map<string, string>()
  const uniq = [...new Set(ids)].filter(Boolean)
  if (!uniq.length) return map
  try {
    const list = uniq.map((id) => `"${id}"`).join(",")
    const rows = await pgrest<Record<string, unknown>[]>(
      `/usuarios?id=in.(${list})&select=id,nome,email`,
    )
    for (const r of rows) {
      map.set(r.id as string, (r.nome as string) || (r.email as string) || "Usuário")
    }
  } catch (e) {
    logWarn("chat", "userNames lookup failed", e)
  }
  return map
}

// ── Channels ─────────────────────────────────────────────────────────────────

export async function listChannelsForUserRest(user: SessionUser): Promise<Channel[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/chat_channels?select=*&order=tipo.asc,nome.asc",
  )
  const all = rows.map(mapChannel).filter((c) => canSeeChannel(user.id, user.role, c))

  const dmPartners = all
    .filter((c) => c.tipo === "dm")
    .map((c) => dmPartnerId(c, user.id))
    .filter((id): id is string => !!id)
  if (dmPartners.length) {
    const names = await userNames(dmPartners)
    for (const c of all) {
      if (c.tipo === "dm") {
        const partner = dmPartnerId(c, user.id)
        c.nome = (partner && names.get(partner)) || "Conversa"
      }
    }
  }
  return all
}

export async function getChannelRest(
  id: string,
  user: SessionUser,
): Promise<Channel | null> {
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/chat_channels?id=eq.${id}&select=*&limit=1`,
    )
    if (!rows[0]) return null
    const c = mapChannel(rows[0])
    return canSeeChannel(user.id, user.role, c) ? c : null
  } catch (e) {
    logWarn("chat", "getChannelRest: not found", e, { id })
    return null
  }
}

// ── Messages ─────────────────────────────────────────────────────────────────

export async function listMessagesRest(channelId: string): Promise<ChatMessage[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    `/chat_messages?channel=eq.${channelId}&select=*&order=created_at.asc`,
  )
  return rows.map((r) => ({
    id: r.id as string,
    channel: r.channel as string,
    autor: (r.autor as string) ?? "",
    autorNome: (r.autor_nome as string) || "Usuário",
    corpo: (r.corpo as string) ?? "",
    anexoUrl: r.anexo ? `/api/chat/${r.id as string}/anexo` : undefined,
    tipo: ((r.tipo as string) === "evento" ? "evento" : "mensagem") as ChatMessage["tipo"],
    created: r.created_at as string,
  }))
}

// ── Writers ──────────────────────────────────────────────────────────────────

export async function enviarMensagemRest(
  channelId: string,
  form: FormData,
  user: SessionUser,
): Promise<ActionResult> {
  const texto = String(form.get("corpo") || "").trim()
  const anexo = form.get("anexo")
  const hasAnexo = anexo instanceof File && anexo.size > 0
  if (!texto && !hasAnexo) return { ok: false, error: "Escreva uma mensagem." }
  try {
    // Optional attachment → Garage. Silently skipped if storage isn't configured.
    let anexoKey: string | null = null
    if (hasAnexo) {
      const { storageEnabled, putObject } = await import("@/lib/storage/garage")
      if (storageEnabled()) {
        const file = anexo as File
        const bytes = new Uint8Array(await file.arrayBuffer())
        anexoKey = `chat/${crypto.randomUUID()}-${safeName(file.name)}`
        await putObject(anexoKey, bytes, file.type || "application/octet-stream")
      }
    }
    await pgrest("/chat_messages", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        channel: channelId,
        autor: user.id,
        autor_nome: user.name,
        corpo: texto,
        tipo: "mensagem",
        anexo: anexoKey,
      }),
    })
    // Touch the channel so the sidebar's recency sort reflects activity.
    await pgrest(`/chat_channels?id=eq.${channelId}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ updated_at: new Date().toISOString() }),
    }).catch(() => {})
    revalidatePath("/chat")
    return { ok: true }
  } catch (e) {
    logWarn("chat", "enviarMensagemRest failed", e, { channelId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao enviar." }
  }
}

export async function iniciarDMRest(
  user: SessionUser,
  outroUserId: string,
): Promise<ActionResult & { channelId?: string }> {
  if (!outroUserId || outroUserId === user.id) {
    return { ok: false, error: "Selecione um destinatário." }
  }
  const slug = dmSlug(user.id, outroUserId)
  try {
    const existing = await pgrest<Record<string, unknown>[]>(
      `/chat_channels?slug=eq.${slug}&select=id&limit=1`,
    )
    if (existing[0]) return { ok: true, channelId: existing[0].id as string }

    let partnerName = "Mensagem direta"
    const names = await userNames([outroUserId])
    partnerName = names.get(outroUserId) || partnerName

    const rows = await pgrest<{ id: string }[]>("/chat_channels", {
      method: "POST",
      headers: { Prefer: "return=representation" },
      body: JSON.stringify({
        nome: partnerName,
        slug,
        descricao: "",
        tipo: "dm",
        allowed_roles: "",
        members: [user.id, outroUserId],
      }),
    })
    revalidatePath("/chat")
    return { ok: true, channelId: rows[0]?.id }
  } catch (e) {
    logWarn("chat", "iniciarDMRest failed", e, { outroUserId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao iniciar conversa." }
  }
}

export async function criarCanalRest(
  form: FormData,
): Promise<ActionResult & { channelId?: string }> {
  const nome = String(form.get("nome") || "").trim()
  if (!nome) return { ok: false, error: "Informe o nome do canal." }
  const descricao = String(form.get("descricao") || "").trim()
  const allowedRoles = parseRoles(String(form.get("allowed_roles") || "")).join(",")
  const slug = slugify(nome)
  try {
    const rows = await pgrest<{ id: string }[]>("/chat_channels", {
      method: "POST",
      headers: { Prefer: "return=representation" },
      body: JSON.stringify({
        nome,
        slug,
        descricao,
        tipo: "canal",
        allowed_roles: allowedRoles,
        members: [],
        icone: "Hash",
      }),
    })
    revalidatePath("/chat")
    return { ok: true, channelId: rows[0]?.id, message: "Canal criado." }
  } catch (e) {
    logWarn("chat", "criarCanalRest failed", e, { nome })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao criar canal." }
  }
}

export async function gerenciarMembrosRest(
  channelId: string,
  memberIds: string[],
): Promise<ActionResult> {
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/chat_channels?id=eq.${channelId}&select=tipo&limit=1`,
    )
    if (!rows[0]) return { ok: false, error: "Canal indisponível." }
    if ((rows[0].tipo as string) === "dm") {
      return { ok: false, error: "DMs não têm gestão de membros." }
    }
    await pgrest(`/chat_channels?id=eq.${channelId}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ members: memberIds, updated_at: new Date().toISOString() }),
    })
    revalidatePath("/chat")
    return { ok: true, message: "Membros atualizados." }
  } catch (e) {
    logWarn("chat", "gerenciarMembrosRest failed", e, { channelId })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao atualizar membros." }
  }
}
