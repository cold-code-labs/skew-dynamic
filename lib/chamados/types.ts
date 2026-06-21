// Client-safe types + pure helpers for the Chamados (service desk) module. Kept
// apart from data.ts/actions.ts (which import the server-only PocketBase client)
// so client components can use these without dragging server code into the
// browser bundle. This is the file you tweak per project: rename departments,
// add a status, recolor a priority.

import type { BadgeVariant } from "@/lib/resources/types"

// ── Status workflow ──────────────────────────────────────────────────────────
// Ordered open → closed. The detail screen drives a ticket along this path.
// Values are stored verbatim in PocketBase (human-readable, Portuguese).

export const CHAMADO_STATUSES = [
  "Aberto",
  "Em andamento",
  "Aguardando",
  "Resolvido",
  "Fechado",
] as const

export type ChamadoStatus = (typeof CHAMADO_STATUSES)[number]

export const STATUS_BADGE: Record<ChamadoStatus, BadgeVariant> = {
  Aberto: "default",
  "Em andamento": "secondary",
  Aguardando: "outline",
  Resolvido: "outline",
  Fechado: "outline",
}

/** Statuses that count as "encerrado" — used for filters and the resolved tint. */
export const CLOSED_STATUSES: ChamadoStatus[] = ["Resolvido", "Fechado"]

export function isOpen(status: string): boolean {
  return !CLOSED_STATUSES.includes(status as ChamadoStatus)
}

// ── Priority ─────────────────────────────────────────────────────────────────

export const CHAMADO_PRIORITIES = ["Urgente", "Alta", "Média", "Baixa"] as const
export type ChamadoPrioridade = (typeof CHAMADO_PRIORITIES)[number]

export const PRIORITY_BADGE: Record<ChamadoPrioridade, BadgeVariant> = {
  Urgente: "destructive",
  Alta: "destructive",
  Média: "secondary",
  Baixa: "outline",
}

// ── Departments (the "fila") ─────────────────────────────────────────────────
// Where a ticket is routed: TI, Manutenção, … Rename these to the client's
// internal teams; the create form and filters read straight from this list.

export const CHAMADO_DEPARTAMENTOS = [
  "TI",
  "Manutenção",
  "Financeiro",
  "RH",
  "Geral",
] as const
export type ChamadoDepartamento = (typeof CHAMADO_DEPARTAMENTOS)[number]

// ── Records ──────────────────────────────────────────────────────────────────

export type Chamado = {
  id?: string
  assunto: string
  descricao: string
  departamento: string
  prioridade: string
  status: string
  solicitante: string
  /** Agent the ticket is assigned to (name); empty = unassigned. */
  responsavel: string
  created?: string
  updated?: string
}

/** A thread entry: a human comment OR a system event (status/assignment). */
export type ComentarioTipo = "comentario" | "evento"

export type Comentario = {
  id?: string
  chamado: string
  autor: string
  corpo: string
  tipo: ComentarioTipo
  created?: string
}

// ── Pure helpers ─────────────────────────────────────────────────────────────

export function normalizeStatus(value: unknown): ChamadoStatus {
  return CHAMADO_STATUSES.includes(value as ChamadoStatus)
    ? (value as ChamadoStatus)
    : "Aberto"
}

export function normalizePrioridade(value: unknown): ChamadoPrioridade {
  return CHAMADO_PRIORITIES.includes(value as ChamadoPrioridade)
    ? (value as ChamadoPrioridade)
    : "Média"
}

/** A short, human ticket reference from the PB id, e.g. "#a1b2c3". */
export function ticketRef(id?: string): string {
  return id ? `#${id.slice(0, 6)}` : "#—"
}

export function formatDateTime(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ""
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function formatDate(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString("pt-BR")
}
