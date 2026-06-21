import { DATA_MODE } from "@/config/env"
import { logWarn } from "@/lib/log"

import { pgrest } from "./client"

export type Stat = { key: string; label: string; value: string; delta: string }
export type Activity = { who: string; what: string; when: string }

const STUB_STATS: Stat[] = [
  { key: "revenue", label: "Receita total", value: "R$ 45.231", delta: "+20,1%" },
  { key: "clients", label: "Clientes ativos", value: "2.350", delta: "+12,4%" },
  { key: "sessions", label: "Sessões hoje", value: "1.204", delta: "+5,2%" },
  { key: "conversion", label: "Conversão", value: "3,8%", delta: "+0,6%" },
]

const STUB_ACTIVITY: Activity[] = [
  { who: "Maria Silva", what: "criou um novo cliente", when: "há 5 min" },
  { who: "João Pereira", what: "atualizou as configurações", when: "há 22 min" },
  { who: "Ana Costa", what: "convidou um novo usuário", when: "há 1 h" },
  { who: "Carlos Souza", what: "exportou um relatório", when: "há 3 h" },
]

export async function getDashboardStats(): Promise<Stat[]> {
  if (DATA_MODE === "stub") return STUB_STATS

  if (DATA_MODE === "pocketbase") {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    // Cheap counts via getList(page=1, perPage=1).totalItems. Each is guarded so
    // a not-yet-seeded collection on a fresh instance shows "—" instead of
    // 500-ing the whole dashboard (the first page after login). The failure is
    // logged so the operator knows which collection is missing.
    const count = async (collection: string, filter?: string): Promise<string> => {
      try {
        const res = await pb
          .collection(collection)
          .getList(1, 1, filter ? { filter } : undefined)
        return String(res.totalItems)
      } catch (e) {
        logWarn("dashboard", `count failed for "${collection}"`, e)
        return "—"
      }
    }
    const [clientes, ativos, usuarios] = await Promise.all([
      count("clientes"),
      count("clientes", 'status = "Ativo"'),
      count("usuarios"),
    ])
    return [
      { key: "clients", label: "Clientes", value: clientes, delta: "cadastrados" },
      { key: "active", label: "Clientes ativos", value: ativos, delta: "status Ativo" },
      { key: "sessions", label: "Usuários", value: usuarios, delta: "equipe" },
      { key: "conversion", label: "Conversão", value: "—", delta: "—" },
    ]
  }

  // Expose a `dashboard_stats` view through PostgREST returning these columns.
  return pgrest<Stat[]>("/dashboard_stats?select=key,label,value,delta")
}

export async function getRecentActivity(): Promise<Activity[]> {
  if (DATA_MODE === "stub") return STUB_ACTIVITY
  // PocketBase: no activity-log collection in the template — show the demo feed.
  // Add a `recent_activity` collection and query it here for a real feed.
  if (DATA_MODE === "pocketbase") return STUB_ACTIVITY
  return pgrest<Activity[]>(
    "/recent_activity?select=who,what,when&order=when.desc&limit=8",
  )
}
