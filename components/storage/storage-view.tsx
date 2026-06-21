"use client"

import { useState, useTransition } from "react"
import { useRouter } from "next/navigation"
import { Download, FileText, Mic, MoreHorizontal, Trash2, Upload } from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useConfirm } from "@/components/ui/confirm"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
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
import { deleteDocumento, uploadDocumento } from "@/lib/storage/actions"
import type { Documento } from "@/lib/storage/documents"
import { formatDuracao, type Reuniao } from "@/lib/reunioes/types"

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

function formatSize(bytes: number): string {
  if (!bytes) return "—"
  const kb = bytes / 1024
  return kb < 1024 ? `${Math.round(kb)} KB` : `${(kb / 1024).toFixed(1)} MB`
}

function formatDate(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString("pt-BR")
}

type FilterType = "todos" | "documentos" | "audios"

const FILTER_LABELS: Record<FilterType, string> = {
  todos: "Todos",
  documentos: "Documentos",
  audios: "Áudios",
}

export function StorageView({
  groups,
  categories,
  recordings = [],
}: {
  groups: { category: string; docs: Documento[] }[]
  categories: string[]
  recordings?: Reuniao[]
}) {
  const router = useRouter()
  const { toast } = useToast()
  const confirm = useConfirm()
  const can = useCan()
  const canUpload = can("files.upload")
  const [open, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()
  const [filter, setFilter] = useState<FilterType>("todos")

  function onUpload(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    startTransition(async () => {
      const result = await uploadDocumento(formData)
      if (result.ok) {
        toast({ title: "Arquivo enviado", variant: "success" })
        setOpen(false)
        router.refresh()
      } else {
        setError(result.error ?? "Falha no upload.")
      }
    })
  }

  async function remove(doc: Documento) {
    if (!doc.id) return
    const ok = await confirm({
      title: "Remover arquivo?",
      description: `"${doc.name}" será excluído permanentemente.`,
      confirmText: "Remover",
      destructive: true,
    })
    if (!ok) return
    startTransition(async () => {
      const result = await deleteDocumento(doc.id!)
      if (result.ok) {
        toast({ title: "Arquivo removido", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Não foi possível remover", description: result.error, variant: "destructive" })
      }
    })
  }

  const showDocs = filter === "todos" || filter === "documentos"
  const showAudios = filter === "todos" || filter === "audios"
  const isEmpty =
    (showDocs && groups.length === 0 && !showAudios) ||
    (showAudios && recordings.length === 0 && !showDocs) ||
    (showDocs && groups.length === 0 && showAudios && recordings.length === 0)

  return (
    <PageShell
      title="Arquivos"
      description="Documentos e mídias da plataforma, organizados por categoria."
      actions={
        canUpload ? (
          <Button size="sm" onClick={() => setOpen(true)}>
            <Upload data-icon="inline-start" />
            Enviar arquivo
          </Button>
        ) : undefined
      }
    >
      {/* Filter tabs */}
      <div className="flex gap-1 rounded-lg border border-border bg-muted/40 p-1 w-fit">
        {(Object.keys(FILTER_LABELS) as FilterType[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-md px-3 py-1 text-sm font-medium transition-colors",
              filter === f
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {FILTER_LABELS[f]}
            {f === "audios" && recordings.length > 0 && (
              <span className="ml-1.5 rounded-full bg-muted px-1.5 py-px text-xs tabular-nums">
                {recordings.length}
              </span>
            )}
            {f === "documentos" && groups.length > 0 && (
              <span className="ml-1.5 rounded-full bg-muted px-1.5 py-px text-xs tabular-nums">
                {groups.reduce((n, g) => n + g.docs.length, 0)}
              </span>
            )}
          </button>
        ))}
      </div>

      {isEmpty ? (
        <Card className="p-8 text-center text-sm text-muted-foreground">
          Nenhum arquivo ainda.
        </Card>
      ) : (
        <div className="flex flex-col gap-4">
          {/* Audio recordings section */}
          {showAudios && recordings.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Gravações de Áudio</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col divide-y">
                {recordings.map((rec, i) => (
                  <div key={rec.id ?? i} className="flex flex-col gap-2 py-3 first:pt-0 last:pb-0">
                    <div className="flex items-center gap-3">
                      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                        <Mic className="size-4" />
                      </div>
                      <div className="flex flex-1 flex-col min-w-0">
                        <span className="text-sm font-medium truncate">{rec.titulo}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatDuracao(rec.duracao)}
                          {rec.created ? ` · ${formatDate(rec.created)}` : ""}
                        </span>
                      </div>
                    </div>
                    {rec.audioUrl && (
                      <audio
                        src={rec.audioUrl}
                        controls
                        className="w-full h-8 ml-12"
                        style={{ maxWidth: "420px" }}
                      />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Documents sections */}
          {showDocs &&
            groups.map((group) => (
              <Card key={group.category}>
                <CardHeader>
                  <CardTitle className="text-sm">{group.category}</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col divide-y">
                  {group.docs.map((doc, i) => (
                    <div key={doc.id ?? i} className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
                      <div className="flex size-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                        <FileText className="size-4" />
                      </div>
                      <div className="flex flex-1 flex-col">
                        <span className="text-sm font-medium">{doc.name}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatSize(doc.size)}
                          {doc.created ? ` · ${formatDate(doc.created)}` : ""}
                        </span>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger
                          render={
                            <Button variant="ghost" size="icon" className="size-8">
                              <MoreHorizontal />
                              <span className="sr-only">Abrir menu</span>
                            </Button>
                          }
                        />
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            disabled={!doc.url}
                            render={
                              <a href={doc.url || "#"} target="_blank" rel="noreferrer" download>
                                <Download />
                                Baixar
                              </a>
                            }
                          />
                          {canUpload ? (
                            <DropdownMenuItem variant="destructive" onClick={() => remove(doc)}>
                              <Trash2 />
                              Remover
                            </DropdownMenuItem>
                          ) : null}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
        </div>
      )}

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Enviar arquivo</SheetTitle>
            <SheetDescription>O arquivo fica guardado no PocketBase desta instância.</SheetDescription>
          </SheetHeader>
          <form onSubmit={onUpload} className="flex min-h-0 flex-1 flex-col">
            <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="file">Arquivo</Label>
                <Input id="file" name="file" type="file" required />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="name">Nome (opcional)</Label>
                <Input id="name" name="name" placeholder="Usa o nome do arquivo se vazio" />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="category">Categoria</Label>
                <input
                  id="category"
                  name="category"
                  list="storage-categories"
                  defaultValue="Geral"
                  className={cn(fieldClass)}
                />
                <datalist id="storage-categories">
                  {categories.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </div>
              {error ? <p className="text-sm text-destructive">{error}</p> : null}
            </div>
            <SheetFooter>
              <Button type="submit" disabled={pending}>
                {pending ? "Enviando…" : "Enviar"}
              </Button>
            </SheetFooter>
          </form>
        </SheetContent>
      </Sheet>
    </PageShell>
  )
}
