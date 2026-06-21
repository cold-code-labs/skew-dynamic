"use client"

import { useState, useTransition } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import {
  ArrowLeft,
  CircleDot,
  Clock,
  Send,
  Trash2,
  UserCog,
} from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useConfirm } from "@/components/ui/confirm"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"
import {
  atribuirChamado,
  comentarChamado,
  excluirChamado,
  mudarStatus,
} from "@/lib/chamados/actions"
import {
  CHAMADO_STATUSES,
  formatDateTime,
  normalizePrioridade,
  normalizeStatus,
  PRIORITY_BADGE,
  STATUS_BADGE,
  ticketRef,
  type Chamado,
  type Comentario,
} from "@/lib/chamados/types"

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).slice(0, 2)
  return parts.map((p) => p[0]?.toUpperCase() ?? "").join("") || "?"
}

export function ChamadoDetail({
  chamado,
  comentarios,
  persisted,
}: {
  chamado: Chamado
  comentarios: Comentario[]
  persisted: boolean
}) {
  const can = useCan()
  const canWrite = can("data.write")
  const canDelete = can("data.delete")
  const status = normalizeStatus(chamado.status)
  const prioridade = normalizePrioridade(chamado.prioridade)

  return (
    <PageShell
      title={chamado.assunto}
      description={`${ticketRef(chamado.id)} · fila ${chamado.departamento}`}
      actions={
        <Button variant="outline" size="sm" nativeButton={false} render={<Link href="/chamados" />}>
          <ArrowLeft data-icon="inline-start" />
          Voltar
        </Button>
      }
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <Badge variant={STATUS_BADGE[status]}>{status}</Badge>
        <Badge variant={PRIORITY_BADGE[prioridade]}>{prioridade}</Badge>
        <Badge variant="outline">{chamado.departamento}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Main column: description + thread + composer */}
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Card>
            <CardContent className="flex flex-col gap-2 py-4">
              <span className="text-xs font-medium text-muted-foreground">Descrição</span>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-pretty">
                {chamado.descricao || "Sem descrição."}
              </p>
              <span className="mt-1 text-xs text-muted-foreground">
                Aberto por {chamado.solicitante || "—"}
                {chamado.created ? ` · ${formatDateTime(chamado.created)}` : ""}
              </span>
            </CardContent>
          </Card>

          <Thread comentarios={comentarios} />

          {canWrite ? (
            <Composer chamadoId={chamado.id!} persisted={persisted} />
          ) : (
            <p className="text-sm text-muted-foreground">
              Você não tem permissão para comentar neste chamado.
            </p>
          )}
        </div>

        {/* Sidebar: workflow controls */}
        <div className="flex flex-col gap-4">
          {canWrite ? (
            <StatusControl chamadoId={chamado.id!} status={status} />
          ) : null}
          {canWrite ? (
            <AssignControl chamadoId={chamado.id!} responsavel={chamado.responsavel} />
          ) : (
            <Card>
              <CardContent className="flex flex-col gap-1 py-4 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Responsável</span>
                <span>{chamado.responsavel || "Não atribuído"}</span>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardContent className="flex flex-col gap-2 py-4 text-sm">
              <Meta label="Solicitante" value={chamado.solicitante || "—"} />
              <Separator />
              <Meta label="Atualizado" value={formatDateTime(chamado.updated) || "—"} />
            </CardContent>
          </Card>

          {canDelete ? <DeleteControl chamadoId={chamado.id!} assunto={chamado.assunto} /> : null}
        </div>
      </div>
    </PageShell>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span>{value}</span>
    </div>
  )
}

function Thread({ comentarios }: { comentarios: Comentario[] }) {
  if (comentarios.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Nenhuma movimentação ainda. Comentários e mudanças de status aparecem aqui.
      </p>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {comentarios.map((c) =>
        c.tipo === "evento" ? (
          <div
            key={c.id}
            className="flex items-center gap-2 px-1 text-xs text-muted-foreground"
          >
            <CircleDot className="size-3.5 shrink-0" />
            <span className="flex-1">
              <span className="font-medium text-foreground/80">{c.autor}</span> · {c.corpo}
            </span>
            <span className="shrink-0">{formatDateTime(c.created)}</span>
          </div>
        ) : (
          <Card key={c.id}>
            <CardContent className="flex gap-3 py-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-muted-foreground">
                {initials(c.autor)}
              </div>
              <div className="flex min-w-0 flex-1 flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{c.autor}</span>
                  <span className="text-xs text-muted-foreground">
                    {formatDateTime(c.created)}
                  </span>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-pretty">
                  {c.corpo}
                </p>
              </div>
            </CardContent>
          </Card>
        ),
      )}
    </div>
  )
}

function Composer({ chamadoId, persisted }: { chamadoId: string; persisted: boolean }) {
  const router = useRouter()
  const { toast } = useToast()
  const [corpo, setCorpo] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()

  function submit() {
    const texto = corpo.trim()
    if (!texto) return
    setError(null)
    startTransition(async () => {
      const result = await comentarChamado(chamadoId, texto)
      if (result.ok) {
        setCorpo("")
        toast({ title: "Comentário enviado", variant: "success" })
        router.refresh()
      } else {
        setError(result.error ?? "Falha ao comentar.")
      }
    })
  }

  return (
    <div className="flex flex-col gap-2">
      <textarea
        value={corpo}
        onChange={(e) => setCorpo(e.target.value)}
        rows={3}
        placeholder={
          persisted ? "Escreva um comentário…" : "Comentário (modo demonstração — não será salvo)"
        }
        className={cn(fieldClass, "h-auto")}
      />
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <div className="flex justify-end">
        <Button size="sm" onClick={submit} disabled={pending || !corpo.trim()}>
          <Send data-icon="inline-start" />
          {pending ? "Enviando…" : "Comentar"}
        </Button>
      </div>
    </div>
  )
}

function StatusControl({ chamadoId, status }: { chamadoId: string; status: string }) {
  const router = useRouter()
  const { toast } = useToast()
  const [pending, startTransition] = useTransition()

  function change(next: string) {
    if (next === status) return
    startTransition(async () => {
      const result = await mudarStatus(chamadoId, next)
      if (result.ok) {
        toast({ title: result.message ?? "Status atualizado", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Falha ao mudar status", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-2 py-4">
        <Label htmlFor="status-select" className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="size-3.5" />
          Status
        </Label>
        <select
          id="status-select"
          value={status}
          disabled={pending}
          onChange={(e) => change(e.target.value)}
          className={fieldClass}
        >
          {CHAMADO_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </CardContent>
    </Card>
  )
}

function AssignControl({
  chamadoId,
  responsavel,
}: {
  chamadoId: string
  responsavel: string
}) {
  const router = useRouter()
  const { toast } = useToast()
  const [value, setValue] = useState(responsavel)
  const [pending, startTransition] = useTransition()
  const dirty = value.trim() !== responsavel.trim()

  function save() {
    startTransition(async () => {
      const result = await atribuirChamado(chamadoId, value)
      if (result.ok) {
        toast({ title: value.trim() ? "Chamado atribuído" : "Atribuição removida", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Falha ao atribuir", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-2 py-4">
        <Label htmlFor="responsavel" className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <UserCog className="size-3.5" />
          Responsável
        </Label>
        <Input
          id="responsavel"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Nome do agente"
        />
        {dirty ? (
          <Button size="sm" variant="outline" onClick={save} disabled={pending}>
            {pending ? "Salvando…" : "Salvar responsável"}
          </Button>
        ) : null}
      </CardContent>
    </Card>
  )
}

function DeleteControl({ chamadoId, assunto }: { chamadoId: string; assunto: string }) {
  const router = useRouter()
  const { toast } = useToast()
  const confirm = useConfirm()
  const [pending, startTransition] = useTransition()

  async function remove() {
    const ok = await confirm({
      title: "Remover chamado?",
      description: `"${assunto}" e todo o seu histórico serão excluídos permanentemente.`,
      confirmText: "Remover",
      destructive: true,
    })
    if (!ok) return
    startTransition(async () => {
      const result = await excluirChamado(chamadoId)
      if (result.ok) {
        toast({ title: "Chamado removido", variant: "success" })
        router.push("/chamados")
      } else {
        toast({ title: "Não foi possível remover", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <Button variant="ghost" size="sm" className="text-destructive" onClick={remove} disabled={pending}>
      <Trash2 data-icon="inline-start" />
      Remover chamado
    </Button>
  )
}
