"use client"

import { useState, useTransition } from "react"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
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
import { createRecord, updateRecord } from "@/lib/resources/actions"
import type { ResourceDef, ResourceField, ResourceRow } from "@/lib/resources/types"

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

function Field({ field, row }: { field: ResourceField; row?: ResourceRow }) {
  const defaultValue = row?.[field.field] ?? ""
  const common = { id: field.field, name: field.field, required: field.required }

  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={field.field}>{field.label}</Label>
      {field.type === "textarea" ? (
        <textarea
          {...common}
          defaultValue={String(defaultValue)}
          placeholder={field.placeholder}
          rows={3}
          className={cn(fieldClass, "h-auto")}
        />
      ) : field.type === "select" ? (
        <select {...common} defaultValue={String(defaultValue)} className={fieldClass}>
          <option value="">—</option>
          {field.options?.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      ) : (
        <Input
          {...common}
          type={
            field.type === "number" ? "number" : field.type === "date" ? "date" : field.type === "email" ? "email" : "text"
          }
          defaultValue={String(defaultValue)}
          placeholder={field.placeholder}
        />
      )}
    </div>
  )
}

export function ResourceFormSheet({
  def,
  open,
  onOpenChange,
  row,
}: {
  def: ResourceDef
  open: boolean
  onOpenChange: (open: boolean) => void
  /** Present → edit mode; absent → create mode. */
  row?: ResourceRow
}) {
  const router = useRouter()
  const { toast } = useToast()
  const [pending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)
  const editing = !!row?.id

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const formData = new FormData(e.currentTarget)
    startTransition(async () => {
      const result = editing
        ? await updateRecord(def.key, String(row!.id), formData)
        : await createRecord(def.key, formData)
      if (result.ok) {
        toast({ title: editing ? "Alterações salvas" : `${def.singular} criado`, variant: "success" })
        onOpenChange(false)
        router.refresh()
      } else {
        setError(result.error ?? "Falha ao gravar.")
      }
    })
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>
            {editing ? `Editar ${def.singular.toLowerCase()}` : `Novo ${def.singular.toLowerCase()}`}
          </SheetTitle>
          <SheetDescription>{def.description}</SheetDescription>
        </SheetHeader>

        <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col">
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4">
            {(def.fields ?? []).map((field) => (
              <Field key={field.field} field={field} row={row} />
            ))}
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
          </div>
          <SheetFooter>
            <Button type="submit" disabled={pending}>
              {pending ? "Salvando…" : editing ? "Salvar" : "Criar"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  )
}
