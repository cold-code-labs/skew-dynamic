import { AlertTriangle, CheckCircle2, CheckCheck, Info } from "lucide-react"

import { Button } from "@/components/ui/button"
import { PageShell } from "@/components/page-shell"
import { cn } from "@/lib/utils"
import { listNotificacoes } from "@/lib/notificacoes/data"
import { markAllReadForm } from "@/lib/notificacoes/actions"

export const dynamic = "force-dynamic"

const ICON = {
  sucesso: { Icon: CheckCircle2, className: "text-emerald-500" },
  alerta: { Icon: AlertTriangle, className: "text-amber-500" },
  info: { Icon: Info, className: "text-sky-500" },
} as const

function fmtDate(iso: string): string {
  if (!iso) return ""
  const [y, m, d] = iso.split("-")
  return d && m && y ? `${d}/${m}/${y}` : iso
}

export default async function NotificacoesPage() {
  const items = await listNotificacoes()
  const unread = items.filter((n) => !n.lida).length

  return (
    <PageShell
      title="Notificações"
      description={
        unread > 0
          ? `Você tem ${unread} notificação${unread === 1 ? "" : "ões"} não lida${unread === 1 ? "" : "s"}.`
          : "Tudo em dia — nenhuma notificação não lida."
      }
      actions={
        unread > 0 ? (
          <form action={markAllReadForm}>
            <Button type="submit" variant="outline" size="sm">
              <CheckCheck className="size-4" />
              Marcar todas como lidas
            </Button>
          </form>
        ) : undefined
      }
    >
      {items.length === 0 ? (
        <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed py-16 text-center">
          <Info className="size-6 text-muted-foreground" />
          <p className="text-sm font-medium">Sem notificações</p>
          <p className="text-sm text-muted-foreground">Novas notificações aparecerão aqui.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((n) => {
            const { Icon, className } = ICON[n.tipo as keyof typeof ICON] ?? ICON.info
            return (
              <div
                key={n.id ?? n.titulo}
                className={cn(
                  "flex items-start gap-3 rounded-lg border p-4",
                  n.lida ? "bg-card" : "bg-accent/40 border-accent",
                )}
              >
                <Icon className={cn("mt-0.5 size-5 shrink-0", className)} />
                <div className="flex min-w-0 flex-1 flex-col gap-0.5">
                  <div className="flex items-center gap-2">
                    <span className={cn("text-sm", !n.lida && "font-semibold")}>
                      {n.titulo}
                    </span>
                    {!n.lida ? (
                      <span className="size-2 shrink-0 rounded-full bg-primary" aria-label="Não lida" />
                    ) : null}
                  </div>
                  <p className="text-sm text-muted-foreground text-pretty">{n.mensagem}</p>
                </div>
                <span className="shrink-0 text-xs text-muted-foreground">{fmtDate(n.data)}</span>
              </div>
            )
          })}
        </div>
      )}
    </PageShell>
  )
}
