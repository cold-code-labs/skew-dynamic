"use client"

import { useState, useTransition } from "react"
import { useRouter } from "next/navigation"
import { MoreHorizontal, Pencil, Trash2, UserPlus } from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { useConfirm } from "@/components/ui/confirm"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"
import { inviteMember, removeMember, updateMember } from "@/lib/acessos/actions"
import type { Member } from "@/lib/acessos/members"
import { ROLES } from "@/config/roles"

const STATUS: Record<string, "default" | "secondary" | "outline"> = {
  Ativo: "default",
  Convidado: "secondary",
  Inativo: "outline",
}

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

function initials(name: string) {
  return name.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase()
}

export function MembersTable({ members }: { members: Member[] }) {
  const router = useRouter()
  const { toast } = useToast()
  const confirm = useConfirm()
  const can = useCan()
  const canManage = can("members.manage")
  const [open, setOpen] = useState(false)
  const [edit, setEdit] = useState<Member | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()

  function openInvite() {
    setEdit(undefined)
    setError(null)
    setOpen(true)
  }
  function openEdit(m: Member) {
    setEdit(m)
    setError(null)
    setOpen(true)
  }

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    const form = new FormData(e.currentTarget)
    startTransition(async () => {
      const result = edit?.id
        ? await updateMember(edit.id, form)
        : await inviteMember(form)
      if (result.ok) {
        toast({
          title: edit ? "Membro atualizado" : "Convite criado",
          description: result.message,
          variant: "success",
        })
        setOpen(false)
        router.refresh()
      } else {
        setError(result.error ?? "Falha ao gravar.")
      }
    })
  }

  async function remove(m: Member) {
    if (!m.id) return
    const ok = await confirm({
      title: "Remover membro?",
      description: `"${m.nome}" perderá o acesso à plataforma.`,
      confirmText: "Remover",
      destructive: true,
    })
    if (!ok) return
    startTransition(async () => {
      const result = await removeMember(m.id!)
      if (result.ok) {
        toast({ title: "Membro removido", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Não foi possível remover", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <Card className="overflow-hidden p-0">
      <CardHeader className="flex flex-row items-center justify-between gap-2 p-4 pb-0">
        <CardTitle className="text-sm">Equipe</CardTitle>
        {canManage ? (
          <Button size="sm" onClick={openInvite}>
            <UserPlus data-icon="inline-start" />
            Convidar
          </Button>
        ) : null}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Membro</TableHead>
            <TableHead>Papel</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-12" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {members.map((m, i) => (
            <TableRow key={m.id ?? i}>
              <TableCell>
                <div className="flex items-center gap-3">
                  <Avatar className="size-8">
                    <AvatarFallback>{initials(m.nome)}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="font-medium">{m.nome}</span>
                    <span className="text-xs text-muted-foreground">{m.email}</span>
                  </div>
                </div>
              </TableCell>
              <TableCell>{m.papel}</TableCell>
              <TableCell>
                <Badge variant={STATUS[m.status] ?? "secondary"}>{m.status}</Badge>
              </TableCell>
              <TableCell>
                {canManage ? (
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
                      <DropdownMenuItem onClick={() => openEdit(m)}>
                        <Pencil />
                        Editar
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem variant="destructive" onClick={() => remove(m)}>
                        <Trash2 />
                        Remover
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                ) : null}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle>{edit ? "Editar membro" : "Convidar membro"}</SheetTitle>
            <SheetDescription>Defina o papel e o acesso desta pessoa.</SheetDescription>
          </SheetHeader>
          <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col">
            <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="nome">Nome</Label>
                <Input id="nome" name="nome" required defaultValue={edit?.nome ?? ""} />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email">E-mail</Label>
                <Input id="email" name="email" type="email" required defaultValue={edit?.email ?? ""} />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="papel">Papel</Label>
                <select id="papel" name="papel" defaultValue={edit?.papel ?? "Membro"} className={cn(fieldClass)}>
                  {ROLES.map((r) => (
                    <option key={r.key} value={r.label}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="status">Status</Label>
                <select id="status" name="status" defaultValue={edit?.status ?? "Convidado"} className={cn(fieldClass)}>
                  {["Ativo", "Convidado", "Inativo"].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              {error ? <p className="text-sm text-destructive">{error}</p> : null}
            </div>
            <SheetFooter>
              <Button type="submit" disabled={pending}>
                {pending ? "Salvando…" : edit ? "Salvar" : "Convidar"}
              </Button>
            </SheetFooter>
          </form>
        </SheetContent>
      </Sheet>
    </Card>
  )
}
