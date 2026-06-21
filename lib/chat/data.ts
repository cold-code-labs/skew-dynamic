import { DATA_MODE } from "@/config/env"
import type { SessionUser } from "@/lib/auth/types"
import { logWarn } from "@/lib/log"

import {
  canSeeChannel,
  dmPartnerId,
  parseRoles,
  type Channel,
  type ChatMessage,
  type ChatUser,
} from "./types"

// Server-side readers for the Chat module. PocketBase stores conversations in
// `chat_channels` and messages in `chat_messages`. Access control is enforced
// HERE (and mirrored in the realtime relay) via canSeeChannel — the PB rules are
// just the authenticated gate. Client-safe types/helpers live in ./types.
// Mirrors lib/chamados/data.ts.

// ── Stub (DATA_MODE != pocketbase) ───────────────────────────────────────────
const STUB_CHANNELS: Channel[] = [
  { id: "geral", nome: "Geral", slug: "geral", descricao: "Canal aberto a toda a escola.", tipo: "canal", allowedRoles: [], members: [], icone: "Hash" },
  { id: "direcao", nome: "Direção", slug: "direcao", descricao: "Assuntos da direção.", tipo: "canal", allowedRoles: ["owner", "admin"], members: [], icone: "ShieldCheck" },
  { id: "professores", nome: "Professores", slug: "professores", descricao: "Sala dos professores.", tipo: "canal", allowedRoles: ["owner", "admin", "member"], members: [], icone: "GraduationCap" },
]

const STUB_MESSAGES: Record<string, ChatMessage[]> = {
  geral: [
    { id: "m1", channel: "geral", autor: "demo", autorNome: "Direção", corpo: "Bem-vindos ao chat da escola! 🎒", tipo: "mensagem", created: "2026-06-11T12:00:00Z" },
    { id: "m2", channel: "geral", autor: "demo", autorNome: "Coordenação", corpo: "Reunião pedagógica na sexta às 14h.", tipo: "mensagem", created: "2026-06-11T12:05:00Z" },
  ],
}

const STUB_USERS: ChatUser[] = [
  { id: "u-maria", nome: "Maria Silva", email: "maria@escola.com", papel: "Administrador" },
  { id: "u-joao", nome: "João Pereira", email: "joao@escola.com", papel: "Membro" },
  { id: "u-ana", nome: "Ana Costa", email: "ana@escola.com", papel: "Membro" },
]

// ── Mappers ──────────────────────────────────────────────────────────────────
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
    created: r.created as string,
    updated: r.updated as string,
  }
}

// ── Users (for the DM picker) ────────────────────────────────────────────────
export async function listChatUsers(excludeId?: string): Promise<ChatUser[]> {
  if (DATA_MODE !== "pocketbase") return STUB_USERS.filter((u) => u.id !== excludeId)

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("users").getFullList({ sort: "name" })
  return recs
    .filter((r) => r.id !== excludeId)
    .map((r) => ({
      id: r.id,
      nome: (r.name as string) || (r.email as string) || "Usuário",
      email: (r.email as string) ?? "",
      papel: (r.papel as string) || "Membro",
    }))
}

// ── Channels ─────────────────────────────────────────────────────────────────

/** All conversations the user may see, with DM names resolved to the partner. */
export async function listChannelsForUser(user: SessionUser): Promise<Channel[]> {
  if (DATA_MODE !== "pocketbase") {
    return STUB_CHANNELS.filter((c) => canSeeChannel(user.id, user.role, c))
  }

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("chat_channels").getFullList({ sort: "tipo,nome" })
  const all = recs.map(mapChannel).filter((c) => canSeeChannel(user.id, user.role, c))

  // Resolve DM display names to the other participant.
  const dmPartners = all
    .filter((c) => c.tipo === "dm")
    .map((c) => dmPartnerId(c, user.id))
    .filter((id): id is string => !!id)
  if (dmPartners.length) {
    const names = await userNames(pb, dmPartners)
    for (const c of all) {
      if (c.tipo === "dm") {
        const partner = dmPartnerId(c, user.id)
        c.nome = (partner && names.get(partner)) || "Conversa"
      }
    }
  }
  return all
}

export async function getChannel(id: string, user: SessionUser): Promise<Channel | null> {
  if (DATA_MODE !== "pocketbase") {
    const c = STUB_CHANNELS.find((c) => c.id === id) ?? null
    return c && canSeeChannel(user.id, user.role, c) ? c : null
  }
  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  try {
    const c = mapChannel(await pb.collection("chat_channels").getOne(id))
    return canSeeChannel(user.id, user.role, c) ? c : null
  } catch (e) {
    logWarn("chat", "getChannel: not found", e, { id })
    return null
  }
}

/** Channel ids the user may see — feeds the realtime relay's subscription. */
export async function visibleChannelIds(user: SessionUser): Promise<string[]> {
  const channels = await listChannelsForUser(user)
  return channels.map((c) => c.id)
}

// ── Messages ─────────────────────────────────────────────────────────────────
export async function listMessages(channelId: string): Promise<ChatMessage[]> {
  if (DATA_MODE !== "pocketbase") return STUB_MESSAGES[channelId] ?? []

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("chat_messages").getFullList({
    sort: "created",
    filter: `channel = "${channelId}"`,
  })
  return recs.map((r) => ({
    id: r.id as string,
    channel: r.channel as string,
    autor: (r.autor as string) ?? "",
    autorNome: (r.autor_nome as string) || "Usuário",
    corpo: (r.corpo as string) ?? "",
    anexoUrl: r.anexo ? pb.files.getURL(r, r.anexo as string) : undefined,
    tipo: ((r.tipo as string) === "evento" ? "evento" : "mensagem") as ChatMessage["tipo"],
    created: r.created as string,
  }))
}

// ── internal ─────────────────────────────────────────────────────────────────
async function userNames(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pb: any,
  ids: string[],
): Promise<Map<string, string>> {
  const map = new Map<string, string>()
  const uniq = [...new Set(ids)]
  await Promise.all(
    uniq.map(async (id) => {
      try {
        const u = await pb.collection("users").getOne(id)
        map.set(id, (u.name as string) || (u.email as string) || "Usuário")
      } catch (_) {
        map.set(id, "Usuário")
      }
    }),
  )
  return map
}
