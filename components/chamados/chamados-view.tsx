"use client"

import { useMemo, useState, useTransition } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Filter, MessageSquare, Plus, Ticket } from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"
import { criarChamado } from "@/lib/chamados/actions"
import {
  CHAMADO_DEPARTAMENTOS,
  CHAMADO_PRIORITIES,
  CHAMADO_STATUSES,
  formatDate,
  isOpen,
  normalizePrioridade,
  normalizeStatus,
  PRIORITY_BADGE,
  STATUS_BADGE,
  ticketRef,
  type Chamado,
} from "@/lib/chamados/types"

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

export function ChamadosView({
  chamados,
  persisted,
}: {
  chamados: Chamado[]
  persisted: boolean
}) {
  const can = useCan()
  const canWrite = can("data.write")
  const [open, setOpen] = useState(false)
  const [fStatus, setFStatus] = useState<string>("abertos")
  const [fDepto, setFDepto] = useState<string>("todos")

  const filtered = useMemo(() => {
    return chamados.filter((c) => {
      if (fStatus === "abertos" && !isOpen(c.status)) return false
      if (fStatus !== "abertos" && fStatus !== "todos" && c.status !== fStatus) return false
      if (fDepto !== "todos" && c.departamento !== fDepto) return false
      return true
    })
  }, [chamados, fStatus, fDepto])

  const abertos = chamados.filter((c) => isOpen(c.status)).length

  return (
    <PageShell
      title="Chamados"
      description={
        abertos > 0
          ? `${abertos} chamado${abertos === 1 ? "" : "s"} em aberto na fila.`
          : "Nenhum chamado em aberto — tudo resolvido."
      }
      actions={
        canWrite ? (
          <Button size="sm" onClick={() => setOpen(true)}>
            <Plus data-icon="inline-start" />
            Novo chamado
          </Button>
        ) : undefined
      }
    >
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <Filter className="size-4 text-muted-foreground" />
        <select
          value={fStatus}
          onChange={(e) => setFStatus(e.target.value)}
          className={cn(fieldClass, "w-auto")}
          aria-label="Filtrar por status"
        >
          <option value="abertos">Em aberto</option>
          <option value="todos">Todos os status</option>
          {CHAMADO_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={fDepto}
          onChange={(e) => setFDepto(e.target.value)}
          className={cn(fieldClass, "w-auto")}
          aria-label="Filtrar por fila"
        >
          <option value="todos">Todas as filas</option>
          {CHAMADO_DEPARTAMENTOS.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <Card className="p-8 text-center text-sm text-muted-foreground">
          {chamados.length === 0
            ? "Nenhum chamado ainda. Abra o primeiro."
            : "Nenhum chamado com esses filtros."}
        </Card>
      ) : (
        <div className="flex flex-col gap-2">
          {filtered.map((c) => (
            <ChamadoRow key={c.id} chamado={c} />
          ))}
        </div>
      )}

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Novo chamado</SheetTitle>
            <SheetDescription>
              Descreva a solicitação e direcione para a fila responsável.
            </SheetDescription>
          </SheetHeader>
          <NovoChamadoForm persisted={persisted} onCreated={() => setOpen(false)} />
        </SheetContent>
      </Sheet>
    </PageShell>
  )
}

function ChamadoRow({ chamado }: { chamado: Chamado }) {
  const status = normalizeStatus(chamado.status)
  const prioridade = normalizePrioridade(chamado.prioridade)
  return (
    <Link href={`/chamados/${chamado.id}`} className="group block">
      <Card className="transition-colors group-hover:border-primary/40">
        <CardContent className="flex items-start gap-3 py-4">
          <div className="flex size-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
            <Ticket className="size-4" />
          </div>
          <div className="flex min-w-0 flex-1 flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="truncate text-sm font-medium">{chamado.assunto}</span>
              <span className="shrink-0 font-mono text-xs text-muted-foreground">
                {ticketRef(chamado.id)}
              </span>
            </div>
            <span className="truncate text-xs text-muted-foreground">
              {chamado.solicitante || "—"}
              {chamado.responsavel ? ` · resp. ${chamado.responsavel}` : ""}
              {chamado.created ? ` · ${formatDate(chamado.created)}` : ""}
            </span>
          </div>
          <div className="flex shrink-0 flex-wrap items-center justify-end gap-1.5">
            <Badge variant="outline">{chamado.departamento}</Badge>
            <Badge variant={PRIORITY_BADGE[prioridade]}>{prioridade}</Badge>
            <Badge variant={STATUS_BADGE[status]}>{status}</Badge>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

function NovoChamadoForm({
  persisted,
  onCreated,
}: {
  persisted: boolean
  onCreated: () => void
}) {
  const router = useRouter()
  const { toast } = useToast()
  const [pending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const form = new FormData(e.currentTarget)
    startTransition(async () => {
      const result = await criarChamado(form)
      if (result.ok) {
        toast({ title: "Chamado aberto", variant: "success" })
        onCreated()
        router.refresh()
      } else {
        setError(result.error ?? "Falha ao abrir o chamado.")
      }
    })
  }

  return (
    <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4">
        {!persisted ? (
          <p className="rounded-lg border border-dashed border-amber-500/40 bg-amber-500/5 px-3 py-2 text-xs text-muted-foreground">
            Modo demonstração: conecte o PocketBase (DATA_MODE=pocketbase) para
            que os chamados sejam realmente salvos.
          </p>
        ) : null}

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="assunto">Assunto</Label>
          <Input id="assunto" name="assunto" required placeholder="Ex.: Computador não liga" />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="descricao">Descrição</Label>
          <textarea
            id="descricao"
            name="descricao"
            rows={4}
            placeholder="Detalhe o que está acontecendo, desde quando, e o impacto."
            className={cn(fieldClass, "h-auto")}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="departamento">Fila</Label>
            <select id="departamento" name="departamento" defaultValue="TI" className={fieldClass}>
              {CHAMADO_DEPARTAMENTOS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="prioridade">Prioridade</Label>
            <select id="prioridade" name="prioridade" defaultValue="Média" className={fieldClass}>
              {CHAMADO_PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="solicitante">Solicitante (opcional)</Label>
          <Input id="solicitante" name="solicitante" placeholder="Usa seu usuário se vazio" />
        </div>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}
      </div>
      <SheetFooter>
        <Button type="submit" disabled={pending}>
          <MessageSquare data-icon="inline-start" />
          {pending ? "Abrindo…" : "Abrir chamado"}
        </Button>
      </SheetFooter>
    </form>
  )
}
