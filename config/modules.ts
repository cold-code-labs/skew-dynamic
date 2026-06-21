import {
  Bell,
  CalendarDays,
  CreditCard,
  FolderArchive,
  LayoutDashboard,
  LifeBuoy,
  MessagesSquare,
  Mic,
  Search,
  ShieldCheck,
  UserCircle,
  type LucideIcon,
} from "lucide-react"

import type { Capability } from "./roles"
import { RESOURCES } from "./resources"

// ─────────────────────────────────────────────────────────────────────────────
// MODULE REGISTRY — what shows in the sidebar.
//
// Resource modules (Clientes, Financeiro, …) come straight from config/resources
// so the catalog stays in one place. The fixed modules below are toggled here:
// flip `enabled` to hide one from the nav without deleting its code. Everything
// ships ON — prune per project. Order within a group follows MODULES order.
// ─────────────────────────────────────────────────────────────────────────────

export type ModuleGroup = "navegacao" | "operacoes" | "configuracoes"

export type ModuleItem = {
  key: string
  label: string
  href: string
  icon: LucideIcon
  group: ModuleGroup
  enabled: boolean
  /** If set, the module only shows for users with this capability. */
  capability?: Capability
}

// Navegação — cross-cutting tools at the top of the sidebar.
const NAV_MODULES: ModuleItem[] = [
  { key: "dashboard", label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "navegacao", enabled: true },
  { key: "calendario", label: "Calendário", href: "/calendario", icon: CalendarDays, group: "navegacao", enabled: true },
  { key: "notificacoes", label: "Notificações", href: "/notificacoes", icon: Bell, group: "navegacao", enabled: true },
  { key: "busca", label: "Busca global", href: "/busca", icon: Search, group: "navegacao", enabled: true },
]

// Operações — custom (non-resource) modules sit after the resource modules.
// Chamados: full service desk (open tickets, route to a queue, comment thread,
// status workflow, notifications) — a custom module, not a flat resource.
const CHAMADOS: ModuleItem = { key: "chamados", label: "Chamados", href: "/chamados", icon: LifeBuoy, group: "operacoes", enabled: true }
// Chat: team chat with role-gated channels (Direção, Professores…) + 1:1 DMs,
// delivered in real time (PocketBase realtime relayed over SSE). A custom module.
const CHAT: ModuleItem = { key: "chat", label: "Chat", href: "/chat", icon: MessagesSquare, group: "operacoes", enabled: true }
// Reuniões Gravadas: in-browser recording + Whisper transcription (à-la-carte).
const REUNIOES: ModuleItem = { key: "reunioes", label: "Reuniões Gravadas", href: "/reunioes", icon: Mic, group: "operacoes", enabled: true }
const ARQUIVOS: ModuleItem = { key: "arquivos", label: "Arquivos", href: "/arquivos", icon: FolderArchive, group: "operacoes", enabled: true }

// Configurações — account + team/access management.
// Assinatura: deep-link into Stripe's hosted billing portal (à-la-carte); only
// shown to users who manage settings, since it exposes the app's billing.
const CONFIG_MODULES: ModuleItem[] = [
  { key: "conta", label: "Minha conta", href: "/conta", icon: UserCircle, group: "configuracoes", enabled: true },
  { key: "assinaturas", label: "Assinatura", href: "/assinaturas", icon: CreditCard, group: "configuracoes", enabled: true, capability: "settings.manage" },
  { key: "acessos", label: "Usuários e Acessos", href: "/acessos", icon: ShieldCheck, group: "configuracoes", enabled: true, capability: "members.manage" },
]

const RESOURCE_MODULES: ModuleItem[] = RESOURCES.map((r) => ({
  key: r.key,
  label: r.label,
  href: `/${r.key}`,
  icon: r.icon,
  group: r.group ?? "operacoes",
  enabled: true,
}))

export const MODULES: ModuleItem[] = [
  ...NAV_MODULES,
  ...RESOURCE_MODULES,
  CHAMADOS,
  CHAT,
  REUNIOES,
  ARQUIVOS,
  ...CONFIG_MODULES,
]

export const GROUP_LABELS: Record<ModuleGroup, string> = {
  navegacao: "Navegação",
  operacoes: "Operações",
  configuracoes: "Configurações",
}

export const MODULE_GROUPS: ModuleGroup[] = ["navegacao", "operacoes", "configuracoes"]

export function modulesByGroup(group: ModuleGroup): ModuleItem[] {
  return MODULES.filter((m) => m.enabled && m.group === group)
}
