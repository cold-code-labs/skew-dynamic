import { FolderKanban, ListChecks, Users, Wallet } from "lucide-react"

import type { ResourceDef } from "@/lib/resources/types"

// ─────────────────────────────────────────────────────────────────────────────
// THE CORE BUSINESS FILE.
//
// Each entry below is a full screen in the app — sidebar item, searchable table,
// create/edit sheet, and a PocketBase-backed (or demo) data source. To make a
// new instance "yours", this is the main file you edit:
//   • rename labels / columns to the client's domain
//   • drop modules you don't want (delete the entry)
//   • add a module by copying one block and changing the fields
//
// Everything ships ON and seeded, so a fresh deploy already looks like a real,
// populated internal platform (the "showroom"). Prune from there.
// ─────────────────────────────────────────────────────────────────────────────

export const clientes: ResourceDef = {
  key: "clientes",
  label: "Clientes",
  singular: "Cliente",
  description: "Gerencie os clientes da sua plataforma.",
  icon: Users,
  group: "operacoes",
  sort: "nome",
  columns: [
    { field: "nome", label: "Cliente", primary: true },
    { field: "contato", label: "Contato", type: "email" },
    { field: "plano", label: "Plano" },
    {
      field: "status",
      label: "Status",
      type: "badge",
      badges: { Ativo: "default", Inativo: "outline", Pendente: "secondary" },
    },
  ],
  fields: [
    { field: "nome", label: "Nome", required: true, placeholder: "Acme Corp" },
    { field: "contato", label: "Contato", type: "email", placeholder: "maria@acme.com" },
    { field: "plano", label: "Plano", type: "select", options: ["Starter", "Pro", "Enterprise"] },
    { field: "status", label: "Status", type: "select", options: ["Ativo", "Inativo", "Pendente"] },
  ],
  searchFields: ["nome", "contato"],
  stub: [
    { nome: "Acme Corp", contato: "maria@acme.com", plano: "Enterprise", status: "Ativo" },
    { nome: "Globex", contato: "joao@globex.com", plano: "Pro", status: "Ativo" },
    { nome: "Initech", contato: "ana@initech.com", plano: "Pro", status: "Inativo" },
    { nome: "Umbrella", contato: "carlos@umbrella.com", plano: "Starter", status: "Ativo" },
    { nome: "Soylent", contato: "lucia@soylent.com", plano: "Enterprise", status: "Pendente" },
    { nome: "Hooli", contato: "pedro@hooli.com", plano: "Starter", status: "Ativo" },
  ],
}

export const financeiro: ResourceDef = {
  key: "financeiro",
  collection: "lancamentos",
  label: "Financeiro",
  singular: "Lançamento",
  description: "Lançamentos, cobranças e recebíveis.",
  icon: Wallet,
  group: "operacoes",
  sort: "-vencimento",
  columns: [
    { field: "descricao", label: "Descrição", primary: true },
    { field: "categoria", label: "Categoria", type: "muted" },
    { field: "valor", label: "Valor", type: "currency" },
    {
      field: "status",
      label: "Status",
      type: "badge",
      badges: { Pago: "default", Pendente: "secondary", Atrasado: "destructive" },
    },
    { field: "vencimento", label: "Vencimento", type: "date" },
  ],
  fields: [
    { field: "descricao", label: "Descrição", required: true, placeholder: "Mensalidade Acme" },
    { field: "categoria", label: "Categoria", type: "select", options: ["Assinatura", "Serviço", "Reembolso"] },
    { field: "valor", label: "Valor (R$)", type: "number", placeholder: "1500" },
    { field: "status", label: "Status", type: "select", options: ["Pago", "Pendente", "Atrasado"] },
    { field: "vencimento", label: "Vencimento", type: "date" },
  ],
  searchFields: ["descricao", "categoria"],
  stub: [
    { descricao: "Mensalidade Acme", categoria: "Assinatura", valor: 4900, status: "Pago", vencimento: "2026-06-05" },
    { descricao: "Setup Globex", categoria: "Serviço", valor: 12000, status: "Pendente", vencimento: "2026-06-18" },
    { descricao: "Mensalidade Initech", categoria: "Assinatura", valor: 1900, status: "Atrasado", vencimento: "2026-05-28" },
    { descricao: "Consultoria Umbrella", categoria: "Serviço", valor: 8500, status: "Pago", vencimento: "2026-06-02" },
    { descricao: "Reembolso Hooli", categoria: "Reembolso", valor: 320, status: "Pendente", vencimento: "2026-06-20" },
  ],
}

export const projetos: ResourceDef = {
  key: "projetos",
  label: "Projetos",
  singular: "Projeto",
  description: "Acompanhe entregas e responsáveis.",
  icon: FolderKanban,
  group: "operacoes",
  sort: "prazo",
  columns: [
    { field: "nome", label: "Projeto", primary: true },
    { field: "responsavel", label: "Responsável", type: "muted" },
    {
      field: "fase",
      label: "Fase",
      type: "badge",
      badges: { Planejamento: "secondary", "Em andamento": "default", Concluído: "outline" },
    },
    { field: "prazo", label: "Prazo", type: "date" },
  ],
  fields: [
    { field: "nome", label: "Nome", required: true, placeholder: "Onboarding Acme" },
    { field: "responsavel", label: "Responsável", placeholder: "Maria Silva" },
    { field: "fase", label: "Fase", type: "select", options: ["Planejamento", "Em andamento", "Concluído"] },
    { field: "prazo", label: "Prazo", type: "date" },
  ],
  searchFields: ["nome", "responsavel"],
  stub: [
    { nome: "Onboarding Acme", responsavel: "Maria Silva", fase: "Em andamento", prazo: "2026-06-30" },
    { nome: "Migração Globex", responsavel: "João Pereira", fase: "Planejamento", prazo: "2026-07-15" },
    { nome: "Portal Umbrella", responsavel: "Ana Costa", fase: "Em andamento", prazo: "2026-06-22" },
    { nome: "Relatórios Hooli", responsavel: "Carlos Souza", fase: "Concluído", prazo: "2026-05-20" },
  ],
}

// NOTE: "Chamados" (service desk) is no longer a flat resource — it graduated
// into a full custom module with comments, a status workflow and notifications.
// See lib/chamados/* and app/(app)/chamados/. It owns the `chamados` collection.

export const tarefas: ResourceDef = {
  key: "tarefas",
  label: "Tarefas",
  singular: "Tarefa",
  description: "Atividades e pendências da equipe.",
  icon: ListChecks,
  group: "operacoes",
  sort: "prazo",
  columns: [
    { field: "titulo", label: "Tarefa", primary: true },
    { field: "responsavel", label: "Responsável", type: "muted" },
    {
      field: "prioridade",
      label: "Prioridade",
      type: "badge",
      badges: { Alta: "destructive", Média: "secondary", Baixa: "outline" },
    },
    {
      field: "status",
      label: "Status",
      type: "badge",
      badges: { "A fazer": "secondary", "Em progresso": "default", Concluída: "outline" },
    },
    { field: "prazo", label: "Prazo", type: "date" },
  ],
  fields: [
    { field: "titulo", label: "Título", required: true, placeholder: "Revisar contrato" },
    { field: "responsavel", label: "Responsável", placeholder: "Maria Silva" },
    { field: "prioridade", label: "Prioridade", type: "select", options: ["Alta", "Média", "Baixa"] },
    { field: "status", label: "Status", type: "select", options: ["A fazer", "Em progresso", "Concluída"] },
    { field: "prazo", label: "Prazo", type: "date" },
  ],
  searchFields: ["titulo", "responsavel"],
  stub: [
    { titulo: "Revisar contrato Acme", responsavel: "Maria Silva", prioridade: "Alta", status: "Em progresso", prazo: "2026-06-12" },
    { titulo: "Preparar relatório mensal", responsavel: "João Pereira", prioridade: "Média", status: "A fazer", prazo: "2026-06-18" },
    { titulo: "Onboarding novo cliente", responsavel: "Ana Costa", prioridade: "Alta", status: "A fazer", prazo: "2026-06-10" },
    { titulo: "Atualizar documentação", responsavel: "Carlos Souza", prioridade: "Baixa", status: "Concluída", prazo: "2026-06-05" },
    { titulo: "Follow-up proposta Globex", responsavel: "Maria Silva", prioridade: "Média", status: "Em progresso", prazo: "2026-06-22" },
  ],
}

/** The resource catalog. Order here = order in the sidebar. */
export const RESOURCES: ResourceDef[] = [clientes, financeiro, projetos, tarefas]

export function resourceByKey(key: string): ResourceDef | undefined {
  return RESOURCES.find((r) => r.key === key)
}
