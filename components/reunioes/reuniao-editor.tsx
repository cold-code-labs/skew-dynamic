"use client"

import { useEffect, useMemo, useRef, useState, useTransition } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ArrowLeft, Check, Plus, RotateCcw, Save, UserCog } from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useToast } from "@/components/ui/toast"
import { cn } from "@/lib/utils"
import { salvarTranscricao } from "@/lib/reunioes/actions"
import {
  formatDuracao,
  formatTimestamp,
  htmlToSegmentos,
  isEdited,
  parseSegmentos,
  speakerKeys,
  speakerLabel,
  STATUS_LABELS,
  type Locutores,
  type Reuniao,
  type Segmento,
} from "@/lib/reunioes/types"

import type { ActionResult } from "@/lib/resources/types"

// Same network-throw guard the list uses: a server action can fail transiently
// (dropped request / 5xx from the tunnel) and throw instead of returning a
// result. Convert it to a normal failed result so the editor shows a message
// and keeps the user's unsaved edits.
async function runAction(fn: () => Promise<ActionResult>): Promise<ActionResult> {
  try {
    return await fn()
  } catch {
    return { ok: false, error: "Falha de conexão. Tente salvar novamente." }
  }
}

// A small fixed palette so each speaker reads as a distinct color. Keyed by the
// speaker's position in the meeting, not its letter, so colors stay stable. The
// theme's --chart-* tokens are grayscale, so these are explicit hues.
const SPEAKER_COLORS = [
  "#6366f1",
  "#ec4899",
  "#f59e0b",
  "#10b981",
  "#06b6d4",
  "#8b5cf6",
  "#ef4444",
  "#84cc16",
]

const textareaClass =
  "w-full resize-none rounded-lg border border-transparent bg-transparent px-2 py-1.5 text-sm leading-relaxed outline-none transition-colors hover:border-border focus-visible:border-ring focus-visible:bg-background focus-visible:ring-3 focus-visible:ring-ring/50"

export function ReuniaoEditor({
  reuniao,
  persisted,
}: {
  reuniao: Reuniao
  persisted: boolean
}) {
  const router = useRouter()
  const { toast } = useToast()
  const can = useCan()
  const canEdit = can("data.write") && persisted
  const [pending, startTransition] = useTransition()

  // Seed from structured segments; fall back to recovering them from the legacy
  // flat HTML so meetings transcribed before timestamps existed are still editable.
  const initial = useMemo<Segmento[]>(() => {
    // parseSegmentos normalizes shape and fills `original` (baseline = current
    // text) for any source missing it, so the edited/restore logic always works.
    const segs =
      reuniao.segmentos && reuniao.segmentos.length > 0
        ? reuniao.segmentos
        : htmlToSegmentos(reuniao.transcricao ?? "")
    return parseSegmentos(segs)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const [segmentos, setSegmentos] = useState<Segmento[]>(initial)
  const [locutores, setLocutores] = useState<Locutores>(reuniao.locutores ?? {})
  const [dirty, setDirty] = useState(false)
  const [activeIdx, setActiveIdx] = useState<number>(-1)

  const audioRef = useRef<HTMLAudioElement | null>(null)
  const speakers = useMemo(() => speakerKeys(segmentos), [segmentos])
  const colorOf = (speaker: string) =>
    SPEAKER_COLORS[Math.max(0, speakers.indexOf(speaker)) % SPEAKER_COLORS.length]
  const hasTiming = useMemo(() => segmentos.some((s) => s.end > 0), [segmentos])

  // Warn before leaving with unsaved edits (closing the tab / hard nav).
  useEffect(() => {
    if (!dirty) return
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ""
    }
    window.addEventListener("beforeunload", onBeforeUnload)
    return () => window.removeEventListener("beforeunload", onBeforeUnload)
  }, [dirty])

  // ── editing ────────────────────────────────────────────────────────────────
  function editText(idx: number, text: string) {
    setSegmentos((prev) => prev.map((s, i) => (i === idx ? { ...s, text } : s)))
    setDirty(true)
  }
  function reassign(idx: number, speaker: string) {
    setSegmentos((prev) => prev.map((s, i) => (i === idx ? { ...s, speaker } : s)))
    setDirty(true)
  }
  function renameSpeaker(key: string, name: string) {
    setLocutores((prev) => {
      const next = { ...prev }
      if (name.trim()) next[key] = name.trim()
      else delete next[key]
      return next
    })
    setDirty(true)
  }
  // Next free speaker key (A, B, C… then S1, S2 once letters run out).
  function nextSpeakerKey(): string {
    for (let i = 0; i < 26; i++) {
      const k = String.fromCharCode(65 + i)
      if (!speakers.includes(k)) return k
    }
    let n = 1
    while (speakers.includes(`S${n}`)) n++
    return `S${n}`
  }

  // ── audio sync ───────────────────────────────────────────────────────────────
  function seekTo(seconds: number) {
    const el = audioRef.current
    if (!el) return
    el.currentTime = seconds
    void el.play().catch(() => {})
  }
  function onTimeUpdate() {
    const t = audioRef.current?.currentTime ?? 0
    // Find the last segment whose start is at or before the playhead.
    let idx = -1
    for (let i = 0; i < segmentos.length; i++) {
      if (segmentos[i].start <= t + 0.05) idx = i
      else break
    }
    setActiveIdx((cur) => (cur === idx ? cur : idx))
  }

  function save() {
    startTransition(async () => {
      const result = await runAction(() => salvarTranscricao(reuniao.id!, { segmentos, locutores }))
      if (result.ok) {
        toast({ title: "Transcrição salva", variant: "success" })
        setDirty(false)
        router.refresh()
      } else {
        toast({ title: "Não foi possível salvar", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <PageShell
      title={reuniao.titulo}
      description={`${formatDuracao(reuniao.duracao)} · ${STATUS_LABELS[reuniao.status]}`}
      actions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" nativeButton={false} render={<Link href="/reunioes" />}>
            <ArrowLeft data-icon="inline-start" />
            Voltar
          </Button>
          {canEdit ? (
            <Button size="sm" onClick={save} disabled={!dirty || pending}>
              <Save data-icon="inline-start" />
              {pending ? "Salvando…" : "Salvar"}
            </Button>
          ) : null}
        </div>
      }
    >
      {/* Audio player — sticks under the header so it's reachable while scrolling. */}
      {reuniao.audioUrl ? (
        <div className="sticky top-0 z-10 -mx-1 rounded-xl border border-border bg-background/80 p-3 backdrop-blur">
          <audio
            ref={audioRef}
            controls
            src={reuniao.audioUrl}
            onTimeUpdate={onTimeUpdate}
            className="w-full"
          />
        </div>
      ) : null}

      {/* Speaker legend — rename a speaker here and every turn relabels at once. */}
      {speakers.length > 0 ? (
        <Card>
          <CardContent className="flex flex-wrap items-center gap-2 py-3">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <UserCog className="size-3.5" />
              Locutores
            </span>
            {speakers.map((key) => (
              <SpeakerChip
                key={key}
                color={colorOf(key)}
                name={speakerLabel(key, locutores)}
                turns={segmentos.filter((s) => s.speaker === key).length}
                editable={canEdit}
                onRename={(name) => renameSpeaker(key, name)}
              />
            ))}
          </CardContent>
        </Card>
      ) : null}

      {segmentos.length === 0 ? (
        <Card className="p-8 text-center text-sm text-muted-foreground">
          {reuniao.status === "transcrita"
            ? "Transcrição vazia."
            : "Esta reunião ainda não foi transcrita. Inicie a transcrição na lista de reuniões."}
        </Card>
      ) : (
        <div className="flex flex-col">
          {!hasTiming ? (
            <p className="px-1 pb-2 text-xs text-muted-foreground">
              Esta transcrição não tem marcação de tempo (gerada antes do recurso). Transcreva
              novamente para obter o tempo por fala.
            </p>
          ) : null}
          {segmentos.map((seg, idx) => (
            <SegmentRow
              key={idx}
              seg={seg}
              color={colorOf(seg.speaker)}
              name={speakerLabel(seg.speaker, locutores)}
              active={idx === activeIdx}
              editable={canEdit}
              hasTiming={hasTiming}
              speakers={speakers}
              locutores={locutores}
              onSeek={() => seekTo(seg.start)}
              onText={(t) => editText(idx, t)}
              onReassign={(s) => reassign(idx, s)}
              onNewSpeaker={() => reassign(idx, nextSpeakerKey())}
              onRestore={() => seg.original != null && editText(idx, seg.original)}
            />
          ))}
        </div>
      )}
    </PageShell>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Speaker chip — click the name (when editable) to rename inline.
// ─────────────────────────────────────────────────────────────────────────────
function SpeakerChip({
  color,
  name,
  turns,
  editable,
  onRename,
}: {
  color: string
  name: string
  turns: number
  editable: boolean
  onRename: (name: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(name)
  useEffect(() => setValue(name), [name])

  function commit() {
    setEditing(false)
    if (value.trim() && value.trim() !== name) onRename(value.trim())
    else setValue(name)
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/40 py-0.5 pl-2 pr-2.5 text-xs">
      <span className="size-2.5 rounded-full" style={{ backgroundColor: color }} />
      {editing ? (
        <input
          autoFocus
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit()
            if (e.key === "Escape") {
              setValue(name)
              setEditing(false)
            }
          }}
          className="w-24 bg-transparent font-medium outline-none"
        />
      ) : (
        <button
          type="button"
          disabled={!editable}
          onClick={() => setEditing(true)}
          className={cn("font-medium", editable && "hover:underline")}
          title={editable ? "Renomear locutor" : undefined}
        >
          {name}
        </button>
      )}
      <span className="text-muted-foreground">· {turns}</span>
    </span>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// One transcript turn: timestamp + speaker (reassignable) + editable text.
// ─────────────────────────────────────────────────────────────────────────────
function SegmentRow({
  seg,
  color,
  name,
  active,
  editable,
  hasTiming,
  speakers,
  locutores,
  onSeek,
  onText,
  onReassign,
  onNewSpeaker,
  onRestore,
}: {
  seg: Segmento
  color: string
  name: string
  active: boolean
  editable: boolean
  hasTiming: boolean
  speakers: string[]
  locutores: Locutores
  onSeek: () => void
  onText: (text: string) => void
  onReassign: (speaker: string) => void
  onNewSpeaker: () => void
  onRestore: () => void
}) {
  const edited = isEdited(seg)
  const taRef = useRef<HTMLTextAreaElement | null>(null)
  // Auto-grow the textarea to fit its content.
  function autosize(el: HTMLTextAreaElement | null) {
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${el.scrollHeight}px`
  }
  useEffect(() => {
    autosize(taRef.current)
  }, [seg.text])

  return (
    <div
      className={cn(
        "group flex items-start gap-2 rounded-lg px-2 py-2 transition-colors sm:gap-3",
        active ? "bg-primary/5" : "hover:bg-muted/40",
      )}
    >
      {/* Column 1: timestamp (click to seek). Top-padded to line up with the
          first line of the speaker and text columns. */}
      <button
        type="button"
        onClick={onSeek}
        disabled={!hasTiming}
        className={cn(
          "w-12 shrink-0 border border-transparent pt-1.5 text-left font-mono text-xs leading-relaxed tabular-nums text-muted-foreground",
          hasTiming && "hover:text-foreground",
        )}
        title={hasTiming ? "Reproduzir a partir daqui" : undefined}
      >
        {formatTimestamp(seg.start)}
      </button>

      {/* Column 2: speaker (reassignable). */}
      <div className="w-28 shrink-0 pt-1">
        {editable ? (
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <button
                  type="button"
                  className="inline-flex max-w-full items-center gap-1.5 rounded-md border border-transparent px-1 py-0.5 text-left text-xs font-medium leading-relaxed hover:bg-muted"
                >
                  <span className="size-2 shrink-0 rounded-full" style={{ backgroundColor: color }} />
                  <span className="truncate">{name}</span>
                </button>
              }
            />
            <DropdownMenuContent align="start">
              {speakers.map((key) => (
                <DropdownMenuItem key={key} onClick={() => onReassign(key)}>
                  {seg.speaker === key ? <Check /> : <span className="size-4" />}
                  {speakerLabel(key, locutores)}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onNewSpeaker}>
                <Plus />
                Novo locutor
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <span className="inline-flex items-center gap-1.5 border border-transparent px-1 py-0.5 text-xs font-medium leading-relaxed">
            <span className="size-2 shrink-0 rounded-full" style={{ backgroundColor: color }} />
            <span className="truncate">{name}</span>
          </span>
        )}
      </div>

      {/* Column 3: editable text + (when edited) the original baseline. */}
      <div className="flex min-w-0 flex-1 flex-col">
        {editable ? (
          <textarea
            ref={taRef}
            value={seg.text}
            rows={1}
            onChange={(e) => {
              onText(e.target.value)
              autosize(e.target)
            }}
            className={cn(textareaClass, "w-full")}
          />
        ) : (
          <p className="w-full border border-transparent px-2 py-1.5 text-sm leading-relaxed">{seg.text}</p>
        )}

        {edited ? (
          <div className="mt-0.5 flex items-start gap-2 px-2 text-xs text-muted-foreground">
            <span className="mt-px shrink-0 font-medium uppercase tracking-wide text-[10px] text-amber-600 dark:text-amber-500">
              editado
            </span>
            <span className="min-w-0 flex-1 italic">
              <span className="text-muted-foreground/70">original: </span>
              {seg.original}
            </span>
            {editable ? (
              <button
                type="button"
                onClick={onRestore}
                className="inline-flex shrink-0 items-center gap-1 font-medium hover:text-foreground hover:underline"
                title="Restaurar o texto original"
              >
                <RotateCcw className="size-3" />
                Restaurar
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}
