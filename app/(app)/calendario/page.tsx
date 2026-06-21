import { PageShell } from "@/components/page-shell"
import { requireFeature } from "@/config/features"
import { financeiro, projetos, tarefas } from "@/config/resources"
import { listResource } from "@/lib/resources/data"
import { cn } from "@/lib/utils"

export const dynamic = "force-dynamic"

type Evento = { date: string; label: string; tipo: "Projeto" | "Financeiro" | "Tarefa" }

const TIPO_DOT: Record<Evento["tipo"], string> = {
  Projeto: "bg-sky-500",
  Financeiro: "bg-emerald-500",
  Tarefa: "bg-amber-500",
}

const WEEKDAYS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"]
const MONTHS = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

// Pull dated rows from the existing modules into a single event list — no new
// collection. Each module contributes its date field + identity column.
async function collectEvents(): Promise<Evento[]> {
  const [projs, fins, tasks] = await Promise.all([
    listResource(projetos).catch(() => []),
    listResource(financeiro).catch(() => []),
    listResource(tarefas).catch(() => []),
  ])
  const out: Evento[] = []
  for (const r of projs) if (r.prazo) out.push({ date: String(r.prazo), label: String(r.nome ?? "Projeto"), tipo: "Projeto" })
  for (const r of fins) if (r.vencimento) out.push({ date: String(r.vencimento), label: String(r.descricao ?? "Lançamento"), tipo: "Financeiro" })
  for (const r of tasks) if (r.prazo) out.push({ date: String(r.prazo), label: String(r.titulo ?? "Tarefa"), tipo: "Tarefa" })
  return out
}

export default async function CalendarioPage() {
  requireFeature("calendario")
  const events = await collectEvents()

  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() // 0-based
  const todayKey = `${year}-${String(month + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`

  const firstWeekday = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  // Group events by ISO day for the current month.
  const byDay = new Map<string, Evento[]>()
  for (const e of events) {
    if (e.date.startsWith(`${year}-${String(month + 1).padStart(2, "0")}`)) {
      const list = byDay.get(e.date) ?? []
      list.push(e)
      byDay.set(e.date, list)
    }
  }

  // Build the grid cells (leading blanks + days).
  const cells: (number | null)[] = []
  for (let i = 0; i < firstWeekday; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)

  return (
    <PageShell
      title="Calendário"
      description={`${MONTHS[month]} de ${year} — prazos de projetos, vencimentos e tarefas.`}
      actions={
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          {(Object.keys(TIPO_DOT) as Evento["tipo"][]).map((t) => (
            <span key={t} className="flex items-center gap-1.5">
              <span className={cn("size-2 rounded-full", TIPO_DOT[t])} />
              {t}
            </span>
          ))}
        </div>
      }
    >
      <div className="overflow-hidden rounded-lg border">
        <div className="grid grid-cols-7 border-b bg-muted/40 text-center text-xs font-medium text-muted-foreground">
          {WEEKDAYS.map((w) => (
            <div key={w} className="py-2 capitalize">{w}</div>
          ))}
        </div>
        <div className="grid grid-cols-7">
          {cells.map((day, i) => {
            const key = day
              ? `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`
              : null
            const dayEvents = key ? byDay.get(key) ?? [] : []
            const isToday = key === todayKey
            return (
              <div
                key={i}
                className={cn(
                  "min-h-24 border-b border-r p-1.5 last:border-r-0 [&:nth-child(7n)]:border-r-0",
                  !day && "bg-muted/20",
                )}
              >
                {day ? (
                  <>
                    <div
                      className={cn(
                        "mb-1 flex size-6 items-center justify-center rounded-full text-xs",
                        isToday ? "bg-primary font-semibold text-primary-foreground" : "text-muted-foreground",
                      )}
                    >
                      {day}
                    </div>
                    <div className="flex flex-col gap-1">
                      {dayEvents.slice(0, 3).map((e, j) => (
                        <div key={j} className="flex items-center gap-1 truncate text-[11px]" title={`${e.tipo}: ${e.label}`}>
                          <span className={cn("size-1.5 shrink-0 rounded-full", TIPO_DOT[e.tipo])} />
                          <span className="truncate">{e.label}</span>
                        </div>
                      ))}
                      {dayEvents.length > 3 ? (
                        <span className="text-[11px] text-muted-foreground">+{dayEvents.length - 3}</span>
                      ) : null}
                    </div>
                  </>
                ) : null}
              </div>
            )
          })}
        </div>
      </div>
    </PageShell>
  )
}
