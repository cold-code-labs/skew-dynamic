import { DATA_MODE } from "@/config/env"
import { logWarn } from "@/lib/log"
import { andFilter, tenantFilter } from "@/lib/tenant"

import {
  normalizePrioridade,
  normalizeStatus,
  type Chamado,
  type Comentario,
  type ComentarioTipo,
} from "./types"

// Server-side readers for the Chamados (service desk) module. PocketBase stores
// each ticket in the `chamados` collection and its thread (comments + system
// events) in `chamados_comentarios`. Client-safe types/helpers live in ./types.
// Mirrors lib/reunioes/meetings.ts.

const STUB: Chamado[] = [
  {
    id: "demo-1",
    assunto: "Erro ao exportar relatório",
    descricao:
      "Ao clicar em exportar PDF no dashboard, a página fica carregando e nada acontece.",
    departamento: "TI",
    prioridade: "Alta",
    status: "Aberto",
    solicitante: "maria@acme.com",
    responsavel: "",
    created: "2026-06-10T09:12:00Z",
    updated: "2026-06-10T09:12:00Z",
  },
  {
    id: "demo-2",
    assunto: "Ar-condicionado da sala 3 não liga",
    descricao: "O ar da sala de reuniões 3 parou de funcionar desde ontem.",
    departamento: "Manutenção",
    prioridade: "Média",
    status: "Em andamento",
    solicitante: "joao@globex.com",
    responsavel: "Carlos Souza",
    created: "2026-06-09T14:30:00Z",
    updated: "2026-06-10T11:05:00Z",
  },
  {
    id: "demo-3",
    assunto: "Solicitação de acesso ao financeiro",
    descricao: "Preciso de acesso de leitura ao módulo financeiro para o fechamento.",
    departamento: "Financeiro",
    prioridade: "Baixa",
    status: "Resolvido",
    solicitante: "ana@initech.com",
    responsavel: "Maria Silva",
    created: "2026-06-07T10:00:00Z",
    updated: "2026-06-08T16:20:00Z",
  },
]

const STUB_COMENTARIOS: Record<string, Comentario[]> = {
  "demo-2": [
    {
      id: "c1",
      chamado: "demo-2",
      autor: "Sistema",
      corpo: "Chamado atribuído a Carlos Souza.",
      tipo: "evento",
      created: "2026-06-09T15:00:00Z",
    },
    {
      id: "c2",
      chamado: "demo-2",
      autor: "Carlos Souza",
      corpo: "Já abri um chamado com a empresa de manutenção. Previsão de visita amanhã.",
      tipo: "comentario",
      created: "2026-06-10T11:05:00Z",
    },
  ],
}

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
    created: r.created as string,
    updated: r.updated as string,
  }
}

export async function listChamados(): Promise<Chamado[]> {
  if (DATA_MODE === "postgrest") {
    const { listChamadosRest } = await import("./rest")
    return listChamadosRest()
  }
  if (DATA_MODE !== "pocketbase") return STUB

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("chamados").getFullList({
    sort: "-created",
    filter: andFilter(await tenantFilter()),
  })
  return recs.map(mapChamado)
}

export async function getChamado(id: string): Promise<Chamado | null> {
  if (DATA_MODE === "postgrest") {
    const { getChamadoRest } = await import("./rest")
    return getChamadoRest(id)
  }
  if (DATA_MODE !== "pocketbase") return STUB.find((c) => c.id === id) ?? null

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  try {
    return mapChamado(await pb.collection("chamados").getOne(id))
  } catch (e) {
    logWarn("chamados", "getChamado: record not found", e, { id })
    return null
  }
}

export async function listComentarios(chamadoId: string): Promise<Comentario[]> {
  if (DATA_MODE === "postgrest") {
    const { listComentariosRest } = await import("./rest")
    return listComentariosRest(chamadoId)
  }
  if (DATA_MODE !== "pocketbase") return STUB_COMENTARIOS[chamadoId] ?? []

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("chamados_comentarios").getFullList({
    sort: "created",
    filter: `chamado = "${chamadoId}"`,
  })
  return recs.map((r) => ({
    id: r.id as string,
    chamado: r.chamado as string,
    autor: (r.autor as string) || "Usuário",
    corpo: (r.corpo as string) ?? "",
    tipo: ((r.tipo as string) === "evento" ? "evento" : "comentario") as ComentarioTipo,
    created: r.created as string,
  }))
}
