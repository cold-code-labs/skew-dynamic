"use client"

import { useMemo, useState, useTransition } from "react"
import { useRouter } from "next/navigation"
import { Download, Inbox, MoreHorizontal, Pencil, Plus, Search, Trash2 } from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useConfirm } from "@/components/ui/confirm"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useToast } from "@/components/ui/toast"
import { resourceByKey } from "@/config/resources"
import { deleteRecord } from "@/lib/resources/actions"
import { downloadCsv } from "@/lib/resources/csv"
import { formatCurrency, formatDate, initials, rowMatches } from "@/lib/resources/format"
import { searchFieldsOf, type ResourceColumn, type ResourceRow } from "@/lib/resources/types"

import { ResourceFormSheet } from "./resource-form"

function Cell({ column, row }: { column: ResourceColumn; row: ResourceRow }) {
  const value = row[column.field]

  if (column.primary) {
    const text = String(value ?? "—")
    return (
      <div className="flex items-center gap-3">
        <Avatar className="size-8">
          <AvatarFallback>{initials(text)}</AvatarFallback>
        </Avatar>
        <span className="font-medium">{text}</span>
      </div>
    )
  }

  switch (column.type) {
    case "badge":
      return (
        <Badge variant={column.badges?.[String(value)] ?? "secondary"}>
          {String(value ?? "—")}
        </Badge>
      )
    case "currency":
      return <span className="tabular-nums">{formatCurrency(value)}</span>
    case "date":
      return <span className="text-muted-foreground tabular-nums">{formatDate(value)}</span>
    case "email":
    case "muted":
      return <span className="text-muted-foreground">{String(value ?? "—")}</span>
    default:
      return <span>{String(value ?? "—")}</span>
  }
}

export function ResourceTable({ defKey, rows }: { defKey: string; rows: ResourceRow[] }) {
  const def = resourceByKey(defKey)!
  const router = useRouter()
  const { toast } = useToast()
  const confirm = useConfirm()
  const can = useCan()
  const [query, setQuery] = useState("")
  const [formOpen, setFormOpen] = useState(false)
  const [editRow, setEditRow] = useState<ResourceRow | undefined>(undefined)
  const [, startTransition] = useTransition()

  const hasForm = !!def.fields?.length
  const canWrite = hasForm && can("data.write")
  const canDelete = hasForm && can("data.delete")
  const showActions = canWrite || canDelete

  const searchFields = useMemo(() => searchFieldsOf(def), [def])
  const filtered = useMemo(
    () => rows.filter((r) => rowMatches(r, searchFields, query)),
    [rows, searchFields, query],
  )

  function openCreate() {
    setEditRow(undefined)
    setFormOpen(true)
  }
  function openEdit(row: ResourceRow) {
    setEditRow(row)
    setFormOpen(true)
  }
  async function remove(row: ResourceRow) {
    if (!row.id) return
    const ok = await confirm({
      title: `Remover ${def.singular.toLowerCase()}?`,
      description: `"${row[def.columns[0].field]}" será excluído permanentemente.`,
      confirmText: "Remover",
      destructive: true,
    })
    if (!ok) return
    startTransition(async () => {
      const result = await deleteRecord(def.key, String(row.id))
      if (result.ok) {
        toast({ title: "Removido", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Não foi possível remover", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <PageShell
      title={def.label}
      description={def.description}
      actions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => downloadCsv(def.key, def.columns, filtered)}>
            <Download data-icon="inline-start" />
            Exportar CSV
          </Button>
          {canWrite ? (
            <Button size="sm" onClick={openCreate}>
              <Plus data-icon="inline-start" />
              Novo {def.singular.toLowerCase()}
            </Button>
          ) : null}
        </div>
      }
    >
      <div className="relative w-full max-w-sm">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Buscar ${def.label.toLowerCase()}...`}
          className="pl-9"
        />
      </div>

      <Card className="overflow-hidden p-0">
        <Table>
          <TableHeader>
            <TableRow>
              {def.columns.map((c) => (
                <TableHead key={c.field}>{c.label}</TableHead>
              ))}
              {showActions ? <TableHead className="w-12" /> : null}
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={def.columns.length + (showActions ? 1 : 0)}
                  className="h-32"
                >
                  <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground">
                    <Inbox className="size-6" />
                    <span className="text-sm">
                      {query ? "Nada encontrado para essa busca." : `Nenhum ${def.singular.toLowerCase()} ainda.`}
                    </span>
                    {canWrite && !query ? (
                      <Button variant="outline" size="sm" onClick={openCreate}>
                        <Plus data-icon="inline-start" />
                        Adicionar o primeiro
                      </Button>
                    ) : null}
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((row, i) => (
                <TableRow key={String(row.id ?? i)}>
                  {def.columns.map((c) => (
                    <TableCell key={c.field}>
                      <Cell column={c} row={row} />
                    </TableCell>
                  ))}
                  {showActions ? (
                    <TableCell>
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
                          {canWrite ? (
                            <DropdownMenuItem onClick={() => openEdit(row)}>
                              <Pencil />
                              Editar
                            </DropdownMenuItem>
                          ) : null}
                          {canWrite && canDelete ? <DropdownMenuSeparator /> : null}
                          {canDelete ? (
                            <DropdownMenuItem variant="destructive" onClick={() => remove(row)}>
                              <Trash2 />
                              Remover
                            </DropdownMenuItem>
                          ) : null}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  ) : null}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {hasForm ? (
        <ResourceFormSheet def={def} open={formOpen} onOpenChange={setFormOpen} row={editRow} />
      ) : null}
    </PageShell>
  )
}
