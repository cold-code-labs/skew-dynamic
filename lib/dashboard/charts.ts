import { clientes, financeiro, projetos } from "@/config/resources"
import { listChamados } from "@/lib/chamados/data"
import { logWarn } from "@/lib/log"
import { listResource } from "@/lib/resources/data"
import type { ResourceRow } from "@/lib/resources/types"

// Dashboard chart data, aggregated server-side from the collections that already
// exist — no extra tables. Works in both stub and pocketbase modes because it
// goes through listResource().

export type Slice = { name: string; value: number }
export type MonthPoint = { name: string; total: number }

const MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

function countBy(rows: ResourceRow[], field: string): Slice[] {
  const map = new Map<string, number>()
  for (const r of rows) {
    const key = String(r[field] ?? "—")
    map.set(key, (map.get(key) ?? 0) + 1)
  }
  return [...map.entries()].map(([name, value]) => ({ name, value }))
}

function monthlySum(rows: ResourceRow[], dateField: string, valueField: string): MonthPoint[] {
  const map = new Map<string, number>()
  for (const r of rows) {
    const d = new Date(String(r[dateField] ?? ""))
    if (Number.isNaN(d.getTime())) continue
    const key = `${d.getFullYear()}-${String(d.getMonth()).padStart(2, "0")}`
    const value = Number(r[valueField]) || 0
    map.set(key, (map.get(key) ?? 0) + value)
  }
  return [...map.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([key, total]) => ({ name: MONTHS[Number(key.split("-")[1])] ?? key, total }))
}

export type DashboardCharts = {
  receitaMensal: MonthPoint[]
  clientesPorStatus: Slice[]
  projetosPorFase: Slice[]
  chamadosPorPrioridade: Slice[]
}

// Run a reader but never let one missing collection sink the whole dashboard:
// on a fresh instance a not-yet-seeded collection logs a warning and that chart
// just renders empty.
async function safeRows<T>(label: string, read: () => Promise<T[]>): Promise<T[]> {
  try {
    return await read()
  } catch (e) {
    logWarn("dashboard", `chart source "${label}" unavailable`, e)
    return []
  }
}

export async function getDashboardCharts(): Promise<DashboardCharts> {
  const [cli, fin, proj, chamados] = await Promise.all([
    safeRows("clientes", () => listResource(clientes)),
    safeRows("financeiro", () => listResource(financeiro)),
    safeRows("projetos", () => listResource(projetos)),
    safeRows("chamados", () => listChamados()),
  ])
  return {
    receitaMensal: monthlySum(fin, "vencimento", "valor"),
    clientesPorStatus: countBy(cli, "status"),
    projetosPorFase: countBy(proj, "fase"),
    chamadosPorPrioridade: countBy(chamados as unknown as ResourceRow[], "prioridade"),
  }
}
