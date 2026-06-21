"use client"

import { useCallback, useEffect, useMemo, useRef, useState, useTransition } from "react"
import { Hash, Lock, Plus, Send, Settings2, UserPlus, Users } from "lucide-react"

import { PageShell } from "@/components/page-shell"
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
import { ChatMessages, ChatComposer, ChatProvider } from "@/components/ui/chat"
import type { ChatMessageData } from "@/components/ui/chat"
import { HauldrLive, type RealtimeProps } from "@/lib/realtime/live"
import { ROLES, type RoleKey } from "@/config/roles"
import { cn } from "@/lib/utils"
import {
  carregarCanais,
  carregarMensagens,
  criarCanal,
  enviarMensagem,
  gerenciarMembros,
  iniciarDM,
} from "@/lib/chat/actions"
import { initials, type Channel, type ChatMessage, type ChatUser } from "@/lib/chat/types"

type CurrentUser = { id: string; name: string; avatar?: string }

const fieldClass =
  "flex h-8 w-full rounded-lg border border-border bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

function toChatData(m: ChatMessage): ChatMessageData {
  return {
    id: m.id,
    senderId: m.autor,
    senderName: m.autorNome,
    text: m.corpo,
    timestamp: m.created ? new Date(m.created) : Date.now(),
    isSystem: m.tipo === "evento",
    systemEvent: m.tipo === "evento" ? m.corpo : undefined,
    files: m.anexoUrl
      ? [{ name: "anexo", size: 0, type: "", url: m.anexoUrl }]
      : undefined,
  }
}

export function ChatView({
  currentUser,
  channels: initialChannels,
  activeId: initialActiveId,
  initialMessages,
  users,
  canManage,
  persisted,
  sseRelay,
  realtime,
}: {
  currentUser: CurrentUser
  channels: Channel[]
  activeId: string
  initialMessages: ChatMessage[]
  users: ChatUser[]
  canManage: boolean
  persisted: boolean
  /** PocketBase tier only: use the SSE relay at /api/chat/stream. */
  sseRelay?: boolean
  /** Hauldr tier: live updates via the shared Realtime service (broadcast). */
  realtime?: RealtimeProps | null
}) {
  const { toast } = useToast()
  const [channels, setChannels] = useState<Channel[]>(initialChannels)
  const [activeId, setActiveId] = useState<string>(initialActiveId)
  const [cache, setCache] = useState<Record<string, ChatMessage[]>>(
    initialActiveId ? { [initialActiveId]: initialMessages } : {},
  )
  const [unread, setUnread] = useState<Record<string, boolean>>({})
  const [live, setLive] = useState(false)
  const [, startTransition] = useTransition()

  // Sheets
  const [dmOpen, setDmOpen] = useState(false)
  const [canalOpen, setCanalOpen] = useState(false)
  const [membrosOpen, setMembrosOpen] = useState(false)

  const activeIdRef = useRef(activeId)
  activeIdRef.current = activeId
  const meRef = useRef(currentUser.id)

  const active = channels.find((c) => c.id === activeId)
  const messages = cache[activeId] ?? []

  // ── Realtime (PocketBase tier): SSE relay once, fan out by channel ─────────
  useEffect(() => {
    if (!sseRelay) return
    const es = new EventSource("/api/chat/stream")
    es.addEventListener("ready", () => setLive(true))
    es.addEventListener("error", () => setLive(false))
    es.onmessage = (e) => {
      let payload: { action?: string; record?: Record<string, unknown> }
      try {
        payload = JSON.parse(e.data)
      } catch {
        return
      }
      const r = payload.record
      if (!r || (payload.action && payload.action !== "create")) return
      const msg: ChatMessage = {
        id: r.id as string,
        channel: r.channel as string,
        autor: (r.autor as string) ?? "",
        autorNome: (r.autor_nome as string) || "Usuário",
        corpo: (r.corpo as string) ?? "",
        tipo: (r.tipo as string) === "evento" ? "evento" : "mensagem",
        created: r.created as string,
      }
      setCache((prev) => {
        const list = prev[msg.channel] ?? []
        if (list.some((m) => m.id === msg.id)) return prev // already have it
        // Reconcile an optimistic temp from this user (same body).
        let next = list
        if (msg.autor === meRef.current) {
          const idx = next.findIndex((m) => m.id.startsWith("tmp-") && m.corpo === msg.corpo)
          if (idx !== -1) next = next.filter((_, i) => i !== idx)
        }
        return { ...prev, [msg.channel]: [...next, msg] }
      })
      if (msg.channel !== activeIdRef.current && msg.autor !== meRef.current) {
        setUnread((u) => ({ ...u, [msg.channel]: true }))
      }
    }
    return () => es.close()
  }, [sseRelay])

  // ── Realtime (Hauldr tier): a write broadcasts "changed" on the active
  // channel's private topic → reload that conversation's messages through
  // RLS-guarded PostgREST. Re-subscribes when the active channel changes.
  useEffect(() => {
    if (!realtime || !activeId) return
    const getToken = async () => {
      try {
        const r = await fetch("/api/auth/token", { cache: "no-store" })
        if (!r.ok) return undefined
        return ((await r.json()) as { accessToken?: string }).accessToken
      } catch {
        return undefined
      }
    }
    const channelId = activeId
    const live = new HauldrLive(realtime.url, realtime.accessToken, getToken)
    setLive(true)
    const sub = live.on(
      `chat:${channelId}`,
      () => {
        carregarMensagens(channelId).then((msgs) =>
          setCache((prev) => ({ ...prev, [channelId]: msgs })),
        )
      },
      { private: true },
    )
    return () => {
      sub.unsubscribe()
      setLive(false)
    }
  }, [realtime, activeId])

  // ── Select a conversation (load history on first open) ─────────────────────
  const selectChannel = useCallback(
    (id: string) => {
      setActiveId(id)
      setUnread((u) => ({ ...u, [id]: false }))
      if (!cache[id]) {
        startTransition(async () => {
          const msgs = await carregarMensagens(id)
          setCache((prev) => ({ ...prev, [id]: msgs }))
        })
      }
    },
    [cache],
  )

  const refreshChannels = useCallback(async (selectId?: string) => {
    const list = await carregarCanais()
    setChannels(list)
    if (selectId) {
      setActiveId(selectId)
      const msgs = await carregarMensagens(selectId)
      setCache((prev) => ({ ...prev, [selectId]: msgs }))
    }
  }, [])

  // ── Send ───────────────────────────────────────────────────────────────────
  const send = useCallback(
    (text: string, file?: File) => {
      const trimmed = text.trim()
      if (!trimmed && !file) return
      if (!activeId) return
      const tempId = `tmp-${Date.now()}`
      const optimistic: ChatMessage = {
        id: tempId,
        channel: activeId,
        autor: currentUser.id,
        autorNome: currentUser.name,
        corpo: trimmed,
        tipo: "mensagem",
        created: new Date().toISOString(),
      }
      setCache((prev) => ({
        ...prev,
        [activeId]: [...(prev[activeId] ?? []), optimistic],
      }))
      const form = new FormData()
      form.set("corpo", trimmed)
      if (file) form.set("anexo", file)
      startTransition(async () => {
        const res = await enviarMensagem(activeId, form)
        if (!res.ok) {
          // roll back the optimistic message + surface the error
          setCache((prev) => ({
            ...prev,
            [activeId]: (prev[activeId] ?? []).filter((m) => m.id !== tempId),
          }))
          toast({ title: "Não enviado", description: res.error, variant: "destructive" })
        }
      })
    },
    [activeId, currentUser.id, currentUser.name, toast],
  )

  const canais = useMemo(() => channels.filter((c) => c.tipo === "canal"), [channels])
  const dms = useMemo(() => channels.filter((c) => c.tipo === "dm"), [channels])

  return (
    <PageShell
      title="Chat"
      description="Canais da escola e mensagens diretas, em tempo real."
      actions={
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
              live && persisted
                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                : "bg-muted text-muted-foreground",
            )}
          >
            <span
              className={cn(
                "size-1.5 rounded-full",
                live && persisted ? "bg-emerald-500" : "bg-muted-foreground/50",
              )}
            />
            {!persisted ? "Demonstração" : live ? "Ao vivo" : "Conectando…"}
          </span>
          <Button size="sm" variant="outline" onClick={() => setDmOpen(true)}>
            <UserPlus className="size-4" /> Nova conversa
          </Button>
          {canManage ? (
            <Button size="sm" onClick={() => setCanalOpen(true)}>
              <Plus className="size-4" /> Novo canal
            </Button>
          ) : null}
        </div>
      }
    >
      {!persisted ? (
        <p className="rounded-lg border border-dashed border-border bg-muted/30 px-3 py-2 text-sm text-muted-foreground">
          Modo demonstração: conecte o PocketBase para enviar e receber mensagens em tempo real.
        </p>
      ) : null}

      <div className="flex min-h-0 flex-1 overflow-hidden rounded-xl border border-border bg-card">
        {/* Sidebar: conversations */}
        <aside className="flex w-64 shrink-0 flex-col border-r border-border">
          <div className="flex-1 overflow-y-auto p-2">
            <SidebarSection label="Canais" />
            {canais.map((c) => (
              <ConversationButton
                key={c.id}
                label={c.nome}
                icon={c.allowedRoles.length ? <Lock className="size-3.5" /> : <Hash className="size-3.5" />}
                active={c.id === activeId}
                unread={!!unread[c.id]}
                onClick={() => selectChannel(c.id)}
              />
            ))}
            {dms.length ? (
              <>
                <SidebarSection label="Mensagens diretas" />
                {dms.map((c) => (
                  <ConversationButton
                    key={c.id}
                    label={c.nome}
                    avatar={c.nome}
                    active={c.id === activeId}
                    unread={!!unread[c.id]}
                    onClick={() => selectChannel(c.id)}
                  />
                ))}
              </>
            ) : null}
          </div>
        </aside>

        {/* Active conversation */}
        <section className="flex min-w-0 flex-1 flex-col">
          {active ? (
            <>
              <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    {active.tipo === "canal" ? (
                      active.allowedRoles.length ? (
                        <Lock className="size-4 text-muted-foreground" />
                      ) : (
                        <Hash className="size-4 text-muted-foreground" />
                      )
                    ) : null}
                    <h2 className="truncate text-sm font-semibold">{active.nome}</h2>
                  </div>
                  {active.descricao ? (
                    <p className="truncate text-xs text-muted-foreground">{active.descricao}</p>
                  ) : null}
                </div>
                {canManage && active.tipo === "canal" ? (
                  <Button size="sm" variant="ghost" onClick={() => setMembrosOpen(true)}>
                    <Settings2 className="size-4" /> Membros
                  </Button>
                ) : null}
              </header>

              <ChatProvider
                currentUser={{ id: currentUser.id, name: currentUser.name, avatar: currentUser.avatar }}
                theme="lunar"
                dateFormat="time-only"
                className="flex min-h-0 flex-1 flex-col"
              >
                <ChatMessages messages={messages.map(toChatData)} className="flex-1" />
                <ChatComposer
                  onSend={(text) => send(text)}
                  onFileUpload={(files) => files[0] && send("", files[0])}
                  placeholder={`Mensagem para ${active.nome}`}
                  disabled={!persisted}
                />
              </ChatProvider>
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center p-8 text-center text-sm text-muted-foreground">
              Selecione um canal ou inicie uma conversa.
            </div>
          )}
        </section>
      </div>

      {/* Nova conversa (DM) */}
      <Sheet open={dmOpen} onOpenChange={setDmOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Nova conversa</SheetTitle>
            <SheetDescription>Escolha com quem você quer conversar.</SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-1 overflow-y-auto px-4">
            {users.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                Nenhum outro usuário disponível.
              </p>
            ) : (
              users.map((u) => (
                <button
                  key={u.id}
                  className="flex items-center gap-3 rounded-lg px-2 py-2 text-left hover:bg-accent"
                  onClick={() => {
                    setDmOpen(false)
                    startTransition(async () => {
                      const res = await iniciarDM(u.id)
                      if (res.ok && res.channelId) {
                        await refreshChannels(res.channelId)
                        setUnread((x) => ({ ...x, [res.channelId!]: false }))
                      } else {
                        toast({ title: "Erro", description: res.error, variant: "destructive" })
                      }
                    })
                  }}
                >
                  <Avatar name={u.nome} />
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{u.nome}</div>
                    <div className="truncate text-xs text-muted-foreground">{u.papel}</div>
                  </div>
                </button>
              ))
            )}
          </div>
        </SheetContent>
      </Sheet>

      {/* Novo canal */}
      {canManage ? (
        <Sheet open={canalOpen} onOpenChange={setCanalOpen}>
          <SheetContent>
            <form
              action={(form) => {
                setCanalOpen(false)
                startTransition(async () => {
                  const res = await criarCanal(form)
                  if (res.ok && res.channelId) {
                    await refreshChannels(res.channelId)
                    toast({ title: "Canal criado" })
                  } else {
                    toast({ title: "Erro", description: res.error, variant: "destructive" })
                  }
                })
              }}
              className="flex h-full flex-col"
            >
              <SheetHeader>
                <SheetTitle>Novo canal</SheetTitle>
                <SheetDescription>
                  Defina quais papéis enxergam o canal. Você poderá adicionar pessoas específicas depois.
                </SheetDescription>
              </SheetHeader>
              <div className="flex flex-col gap-4 overflow-y-auto px-4">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="ch-nome">Nome</Label>
                  <Input id="ch-nome" name="nome" placeholder="Ex.: Coordenação" required />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="ch-desc">Descrição</Label>
                  <Input id="ch-desc" name="descricao" placeholder="Opcional" />
                </div>
                <fieldset className="flex flex-col gap-2">
                  <legend className="mb-1 text-sm font-medium">Papéis com acesso</legend>
                  <p className="mb-1 text-xs text-muted-foreground">
                    Nenhum marcado = aberto a todos os usuários.
                  </p>
                  {ROLES.map((r) => (
                    <label key={r.key} className="flex items-center gap-2 text-sm">
                      <input type="checkbox" name="allowed_roles" value={r.key} className="size-4" />
                      {r.label}
                    </label>
                  ))}
                </fieldset>
              </div>
              <SheetFooter>
                <Button type="submit">Criar canal</Button>
              </SheetFooter>
            </form>
          </SheetContent>
        </Sheet>
      ) : null}

      {/* Gerenciar membros do canal ativo */}
      {canManage && active && active.tipo === "canal" ? (
        <MembrosSheet
          key={active.id}
          open={membrosOpen}
          onOpenChange={setMembrosOpen}
          channel={active}
          users={users}
          onSave={(ids) => {
            setMembrosOpen(false)
            startTransition(async () => {
              const res = await gerenciarMembros(active.id, ids)
              if (res.ok) {
                await refreshChannels()
                toast({ title: "Membros atualizados" })
              } else {
                toast({ title: "Erro", description: res.error, variant: "destructive" })
              }
            })
          }}
        />
      ) : null}
    </PageShell>
  )
}

function SidebarSection({ label }: { label: string }) {
  return (
    <div className="px-2 pb-1 pt-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
      {label}
    </div>
  )
}

function ConversationButton({
  label,
  icon,
  avatar,
  active,
  unread,
  onClick,
}: {
  label: string
  icon?: React.ReactNode
  avatar?: string
  active?: boolean
  unread?: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm",
        active ? "bg-accent font-medium text-accent-foreground" : "hover:bg-accent/60",
      )}
    >
      {avatar ? <Avatar name={avatar} size="sm" /> : <span className="text-muted-foreground">{icon}</span>}
      <span className="min-w-0 flex-1 truncate">{label}</span>
      {unread ? <span className="size-2 shrink-0 rounded-full bg-primary" /> : null}
    </button>
  )
}

function Avatar({ name, size = "md" }: { name: string; size?: "sm" | "md" }) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full bg-primary/10 font-medium text-primary",
        size === "sm" ? "size-6 text-[10px]" : "size-8 text-xs",
      )}
    >
      {initials(name)}
    </span>
  )
}

function MembrosSheet({
  open,
  onOpenChange,
  channel,
  users,
  onSave,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  channel: Channel
  users: ChatUser[]
  onSave: (ids: string[]) => void
}) {
  const [selected, setSelected] = useState<string[]>(channel.members)
  const toggle = (id: string) =>
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))

  const roleLabels = channel.allowedRoles
    .map((k) => ROLES.find((r) => r.key === (k as RoleKey))?.label ?? k)
    .join(", ")

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>
            <span className="inline-flex items-center gap-2">
              <Users className="size-4" /> Membros · {channel.nome}
            </span>
          </SheetTitle>
          <SheetDescription>
            {channel.allowedRoles.length
              ? `Já visível para: ${roleLabels}. Adicione pessoas específicas abaixo.`
              : "Canal aberto a todos. Os marcados continuam com acesso garantido."}
          </SheetDescription>
        </SheetHeader>
        <div className="flex flex-col gap-1 overflow-y-auto px-4">
          {users.map((u) => (
            <label key={u.id} className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-accent">
              <input
                type="checkbox"
                className="size-4"
                checked={selected.includes(u.id)}
                onChange={() => toggle(u.id)}
              />
              <Avatar name={u.nome} size="sm" />
              <div className="min-w-0">
                <div className="truncate text-sm font-medium">{u.nome}</div>
                <div className="truncate text-xs text-muted-foreground">{u.papel}</div>
              </div>
            </label>
          ))}
        </div>
        <SheetFooter>
          <Button onClick={() => onSave(selected)}>
            <Send className="size-4" /> Salvar membros
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
