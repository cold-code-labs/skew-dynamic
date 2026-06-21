"use client"

import { useEffect, useRef, useState, useTransition } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import {
  AudioLines,
  CircleDot,
  FileAudio,
  Loader2,
  MoreHorizontal,
  Pause,
  Pencil,
  Play,
  PencilLine,
  Radio,
  RefreshCw,
  Square,
  Trash2,
  Upload,
  Wand2,
  X,
} from "lucide-react"

import { useCan } from "@/components/auth/use-can"
import { PageShell } from "@/components/page-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
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
import {
  criarReuniao,
  excluirReuniao,
  renomearReuniao,
  transcreverReuniao,
} from "@/lib/reunioes/actions"
import {
  formatDuracao,
  STATUS_LABELS,
  type Reuniao,
  type ReuniaoStatus,
} from "@/lib/reunioes/types"

import type { ActionResult } from "@/lib/resources/types"

// A server action runs over the network, so it can fail transiently — a dropped
// request or a 5xx from the proxy/tunnel makes the call *throw* instead of
// returning an ActionResult. Left unhandled inside startTransition, that throw
// unmounts the whole page into the app error boundary ("Algo deu errado") —
// which is especially misleading here, because the write has usually already
// succeeded server-side (the recording/transcription IS saved) and only the
// follow-up refresh blipped. Convert the throw into a normal failed result so
// the caller shows an inline message and keeps the recording for a retry.
async function runAction(
  fn: () => Promise<ActionResult>,
): Promise<ActionResult> {
  try {
    return await fn()
  } catch {
    return {
      ok: false,
      error:
        "Falha de conexão com o servidor. Confira a lista — se a reunião não aparecer, tente novamente.",
    }
  }
}

const STATUS_BADGE: Record<ReuniaoStatus, "default" | "secondary" | "outline" | "destructive"> = {
  gravada: "outline",
  transcrevendo: "secondary",
  transcrita: "default",
  erro: "destructive",
}

function formatDate(value?: string): string {
  if (!value) return ""
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString("pt-BR")
}

export function ReunioesView({
  reunioes,
  transcribeEnabled,
  realtimeEnabled,
}: {
  reunioes: Reuniao[]
  transcribeEnabled: boolean
  realtimeEnabled: boolean
}) {
  const can = useCan()
  const canRecord = can("files.upload")
  const [open, setOpen] = useState(false)

  return (
    <PageShell
      title="Reuniões Gravadas"
      description="Grave reuniões direto no navegador e transcreva o áudio com IA."
      actions={
        canRecord ? (
          <Button size="sm" onClick={() => setOpen(true)}>
            <CircleDot data-icon="inline-start" />
            Nova gravação
          </Button>
        ) : undefined
      }
    >
      {reunioes.length === 0 ? (
        <Card className="p-8 text-center text-sm text-muted-foreground">
          Nenhuma reunião gravada ainda.
        </Card>
      ) : (
        <div className="flex flex-col gap-3">
          {reunioes.map((r) => (
            <ReuniaoCard key={r.id} reuniao={r} transcribeEnabled={transcribeEnabled} />
          ))}
        </div>
      )}

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Nova gravação</SheetTitle>
            <SheetDescription>
              O áudio é capturado pelo seu microfone e fica guardado no PocketBase desta instância.
            </SheetDescription>
          </SheetHeader>
          <Recorder
            realtimeEnabled={realtimeEnabled}
            onSaved={() => setOpen(false)}
          />
        </SheetContent>
      </Sheet>
    </PageShell>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Recorder — getUserMedia + MediaRecorder. Records audio, lets the user pause /
// stop at any time, preview it, then saves it via the criarReuniao action.
// ─────────────────────────────────────────────────────────────────────────────

type RecState = "idle" | "recording" | "paused" | "preview"

function pickMime(): string {
  if (typeof MediaRecorder === "undefined") return ""
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/mp4",
  ]
  for (const c of candidates) {
    if (MediaRecorder.isTypeSupported(c)) return c
  }
  return ""
}

function Recorder({
  realtimeEnabled,
  onSaved,
}: {
  realtimeEnabled: boolean
  onSaved: () => void
}) {
  const router = useRouter()
  const { toast } = useToast()
  const [state, setState] = useState<RecState>("idle")
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [titulo, setTitulo] = useState("")
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [pending, startTransition] = useTransition()

  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const blobRef = useRef<Blob | null>(null)
  const mimeRef = useRef<string>("")
  const fileNameRef = useRef<string>("")
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const wakeLockRef = useRef<WakeLockSentinel | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  // Wall-clock duration: background tabs throttle setInterval, so deriving the
  // elapsed time from a tick counter undercounts whenever the user switches away.
  // Instead we accumulate real time — baseElapsedRef holds completed segments and
  // segmentStartRef marks when the current running segment began.
  const baseElapsedRef = useRef(0)
  const segmentStartRef = useRef(0)
  // Mirror state/url into refs so the unmount-only and visibility effects can
  // read the latest value without re-subscribing on every render.
  const stateRef = useRef<RecState>("idle")
  const audioUrlRef = useRef<string | null>(null)
  useEffect(() => {
    stateRef.current = state
  }, [state])
  useEffect(() => {
    audioUrlRef.current = audioUrl
  }, [audioUrl])

  function currentElapsed(): number {
    return baseElapsedRef.current + (Date.now() - segmentStartRef.current) / 1000
  }

  // Best-effort screen wake lock so an idle screen is less likely to put the
  // machine to sleep mid-recording. Released automatically when the tab is
  // hidden, so we re-acquire on visibilitychange while still recording.
  async function acquireWakeLock() {
    try {
      if ("wakeLock" in navigator) {
        wakeLockRef.current = await navigator.wakeLock.request("screen")
      }
    } catch {
      // Ignored — wake lock is a nicety, not a requirement.
    }
  }
  function releaseWakeLock() {
    wakeLockRef.current?.release().catch(() => {})
    wakeLockRef.current = null
  }

  // Tidy up media + object URLs on unmount ONLY. This must not depend on state:
  // re-running it on every transition would tear down the live mic stream the
  // instant recording starts (stopping the tracks fires onstop → empty preview).
  useEffect(() => {
    return () => {
      stopTimer()
      releaseWakeLock()
      streamRef.current?.getTracks().forEach((t) => t.stop())
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // The screen wake lock is auto-released when the tab is hidden; re-acquire it
  // when the tab becomes visible again while still recording. Reads stateRef so
  // the listener is registered once and never tears anything down.
  useEffect(() => {
    function onVisibility() {
      if (document.visibilityState === "visible" && stateRef.current === "recording") {
        void acquireWakeLock()
      }
    }
    document.addEventListener("visibilitychange", onVisibility)
    return () => document.removeEventListener("visibilitychange", onVisibility)
  }, [])

  function startTimer() {
    stopTimer()
    timerRef.current = setInterval(() => setElapsed(Math.round(currentElapsed())), 1000)
  }
  function stopTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  async function start() {
    setError(null)
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setError("Seu navegador não permite gravação de áudio neste contexto (use HTTPS).")
      return
    }
    const mime = pickMime()
    if (!mime) {
      setError("Gravação de áudio não suportada neste navegador.")
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      mimeRef.current = mime
      const ext = mime.includes("mp4") ? "mp4" : mime.includes("ogg") ? "ogg" : "webm"
      fileNameRef.current = `reuniao.${ext}`
      chunksRef.current = []
      const rec = new MediaRecorder(stream, { mimeType: mime })
      rec.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data)
      }
      rec.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mime })
        blobRef.current = blob
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)
        setState("preview")
        releaseWakeLock()
        streamRef.current?.getTracks().forEach((t) => t.stop())
        streamRef.current = null
      }
      recorderRef.current = rec
      // No timeslice: the media engine buffers the whole take internally, so the
      // capture keeps running even when a backgrounded tab throttles JS timers.
      // The single blob is assembled in onstop.
      rec.start()
      baseElapsedRef.current = 0
      segmentStartRef.current = Date.now()
      setElapsed(0)
      setState("recording")
      startTimer()
      void acquireWakeLock()
    } catch (e) {
      const msg =
        e instanceof DOMException && e.name === "NotAllowedError"
          ? "Permissão de microfone negada."
          : e instanceof Error
            ? e.message
            : "Não foi possível acessar o microfone."
      setError(msg)
    }
  }

  function pause() {
    recorderRef.current?.pause()
    baseElapsedRef.current = currentElapsed()
    stopTimer()
    setElapsed(Math.round(baseElapsedRef.current))
    releaseWakeLock()
    setState("paused")
  }
  function resume() {
    recorderRef.current?.resume()
    segmentStartRef.current = Date.now()
    startTimer()
    setState("recording")
    void acquireWakeLock()
  }
  function stop() {
    if (state === "recording") baseElapsedRef.current = currentElapsed()
    stopTimer()
    setElapsed(Math.round(baseElapsedRef.current))
    recorderRef.current?.stop()
    // onstop transitions to "preview"
  }

  // Bring an existing audio file (uploaded from disk) into the same preview/save
  // flow as a fresh recording. Duration is read from the file's own metadata.
  function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = "" // allow re-picking the same file
    if (!file) return
    setError(null)
    if (!file.type.startsWith("audio/")) {
      setError("Selecione um arquivo de áudio.")
      return
    }
    blobRef.current = file
    mimeRef.current = file.type
    fileNameRef.current = file.name || "upload"
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    const url = URL.createObjectURL(file)
    setAudioUrl(url)
    if (!titulo) setTitulo(file.name.replace(/\.[^.]+$/, ""))
    // Read duration from metadata; webm/opus exports may report Infinity, so we
    // only trust a finite value and otherwise leave it at 0.
    const probe = new Audio()
    probe.preload = "metadata"
    probe.onloadedmetadata = () => {
      const d = probe.duration
      setElapsed(Number.isFinite(d) ? Math.round(d) : 0)
    }
    probe.src = url
    setState("preview")
  }

  function discard() {
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    blobRef.current = null
    fileNameRef.current = ""
    setAudioUrl(null)
    setElapsed(0)
    setTitulo("")
    setError(null)
    setState("idle")
  }

  function save() {
    const blob = blobRef.current
    if (!blob) return
    setError(null)
    const form = new FormData()
    form.append("audio", blob, fileNameRef.current || "reuniao.webm")
    form.append("titulo", titulo.trim())
    form.append("duracao", String(elapsed))
    form.append("mime", mimeRef.current)
    startTransition(async () => {
      const result = await runAction(() => criarReuniao(form))
      if (result.ok) {
        toast({ title: "Reunião salva", variant: "success" })
        discard()
        onSaved()
        router.refresh()
      } else {
        setError(result.error ?? "Falha ao salvar.")
      }
    })
  }

  const live = state === "recording" || state === "paused"

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-1 flex-col gap-5 overflow-y-auto px-4">
        {/* Live transcription toggle (experimental — streaming not wired yet). */}
        {realtimeEnabled ? (
          <button
            type="button"
            disabled
            title="Transcrição ao vivo chega em breve."
            className="flex items-center justify-between rounded-lg border border-dashed border-border px-3 py-2 text-left text-sm text-muted-foreground opacity-70"
          >
            <span className="flex items-center gap-2">
              <Radio className="size-4" />
              Transcrição ao vivo
            </span>
            <Badge variant="outline">Em breve</Badge>
          </button>
        ) : null}

        {/* Recorder face */}
        <div className="flex flex-col items-center gap-4 rounded-xl border border-border bg-muted/30 py-8">
          <div
            className={cn(
              "flex size-20 items-center justify-center rounded-full bg-background text-muted-foreground shadow-sm",
              state === "recording" && "animate-pulse text-destructive",
            )}
          >
            {state === "preview" ? (
              <FileAudio className="size-8" />
            ) : (
              <AudioLines className="size-8" />
            )}
          </div>
          <div className="font-mono text-3xl tabular-nums">{formatDuracao(elapsed)}</div>
          <div className="text-xs text-muted-foreground">
            {state === "idle" && "Pronto para gravar"}
            {state === "recording" && "Gravando…"}
            {state === "paused" && "Pausado"}
            {state === "preview" && "Pré-visualização"}
          </div>

          <div className="flex items-center gap-2">
            {state === "idle" ? (
              <>
                <Button onClick={start}>
                  <CircleDotInline />
                  Iniciar gravação
                </Button>
                <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                  <Upload data-icon="inline-start" />
                  Enviar arquivo
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="audio/*"
                  className="hidden"
                  onChange={onUpload}
                />
              </>
            ) : null}
            {state === "recording" ? (
              <>
                <Button variant="outline" onClick={pause}>
                  <Pause data-icon="inline-start" />
                  Pausar
                </Button>
                <Button variant="destructive" onClick={stop}>
                  <Square data-icon="inline-start" />
                  Parar
                </Button>
              </>
            ) : null}
            {state === "paused" ? (
              <>
                <Button variant="outline" onClick={resume}>
                  <Play data-icon="inline-start" />
                  Continuar
                </Button>
                <Button variant="destructive" onClick={stop}>
                  <Square data-icon="inline-start" />
                  Parar
                </Button>
              </>
            ) : null}
          </div>
        </div>

        {state === "preview" && audioUrl ? (
          <div className="flex flex-col gap-3">
            <audio controls src={audioUrl} className="w-full" />
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="titulo">Título</Label>
              <Input
                id="titulo"
                value={titulo}
                onChange={(e) => setTitulo(e.target.value)}
                placeholder="Usa data e hora se vazio"
              />
            </div>
          </div>
        ) : null}

        {error ? <p className="text-sm text-destructive">{error}</p> : null}
      </div>

      <SheetFooter>
        {state === "preview" ? (
          <div className="flex w-full gap-2">
            <Button variant="outline" className="flex-1" onClick={discard} disabled={pending}>
              <X data-icon="inline-start" />
              Descartar
            </Button>
            <Button className="flex-1" onClick={save} disabled={pending}>
              {pending ? "Salvando…" : "Salvar reunião"}
            </Button>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            {live
              ? "Pare a gravação para pré-visualizar e salvar."
              : "Clique em “Iniciar gravação” e permita o uso do microfone."}
          </p>
        )}
      </SheetFooter>
    </div>
  )
}

function CircleDotInline() {
  return <CircleDot data-icon="inline-start" className="text-destructive" />
}

// ─────────────────────────────────────────────────────────────────────────────
// One meeting in the list: player, status, transcribe action, transcript.
// ─────────────────────────────────────────────────────────────────────────────

function ReuniaoCard({
  reuniao,
  transcribeEnabled,
}: {
  reuniao: Reuniao
  transcribeEnabled: boolean
}) {
  const router = useRouter()
  const { toast } = useToast()
  const confirm = useConfirm()
  const can = useCan()
  const canWrite = can("data.write")
  const canDelete = can("data.delete")
  const [pending, startTransition] = useTransition()
  const [showTranscript, setShowTranscript] = useState(false)

  const hasTranscript = !!reuniao.transcricao && reuniao.transcricao.trim().length > 0
  const transcribing = reuniao.status === "transcrevendo" || pending

  function transcribe() {
    if (!reuniao.id) return
    startTransition(async () => {
      const result = await runAction(() => transcreverReuniao(reuniao.id!))
      if (result.ok) {
        toast({ title: "Transcrição concluída", variant: "success" })
        setShowTranscript(true)
        router.refresh()
      } else {
        toast({ title: "Não foi possível transcrever", description: result.error, variant: "destructive" })
      }
    })
  }

  async function rename() {
    if (!reuniao.id) return
    const next = window.prompt("Novo título da reunião:", reuniao.titulo)
    if (next == null) return
    startTransition(async () => {
      const result = await runAction(() => renomearReuniao(reuniao.id!, next))
      if (result.ok) {
        toast({ title: "Título atualizado", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Falha ao renomear", description: result.error, variant: "destructive" })
      }
    })
  }

  async function remove() {
    if (!reuniao.id) return
    const ok = await confirm({
      title: "Remover reunião?",
      description: `"${reuniao.titulo}" e seu áudio serão excluídos permanentemente.`,
      confirmText: "Remover",
      destructive: true,
    })
    if (!ok) return
    startTransition(async () => {
      const result = await runAction(() => excluirReuniao(reuniao.id!))
      if (result.ok) {
        toast({ title: "Reunião removida", variant: "success" })
        router.refresh()
      } else {
        toast({ title: "Não foi possível remover", description: result.error, variant: "destructive" })
      }
    })
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-3 py-4">
        <div className="flex items-start gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
            <FileAudio className="size-4" />
          </div>
          <div className="flex flex-1 flex-col">
            <span className="text-sm font-medium">{reuniao.titulo}</span>
            <span className="text-xs text-muted-foreground">
              {formatDuracao(reuniao.duracao)}
              {reuniao.created ? ` · ${formatDate(reuniao.created)}` : ""}
            </span>
          </div>
          <Badge variant={STATUS_BADGE[reuniao.status]}>{STATUS_LABELS[reuniao.status]}</Badge>
          {(canWrite || canDelete) ? (
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
                  <DropdownMenuItem onClick={rename}>
                    <Pencil />
                    Renomear
                  </DropdownMenuItem>
                ) : null}
                {canDelete ? (
                  <DropdownMenuItem variant="destructive" onClick={remove}>
                    <Trash2 />
                    Remover
                  </DropdownMenuItem>
                ) : null}
              </DropdownMenuContent>
            </DropdownMenu>
          ) : null}
        </div>

        {reuniao.audioUrl ? <audio controls src={reuniao.audioUrl} className="w-full" /> : null}

        <div className="flex flex-wrap items-center gap-2">
          {canWrite && reuniao.audioUrl ? (
            <Button
              size="sm"
              variant={hasTranscript ? "outline" : "default"}
              onClick={transcribe}
              disabled={!transcribeEnabled || transcribing}
              title={
                transcribeEnabled
                  ? undefined
                  : "Configure OPENAI_API_KEY no servidor para transcrever."
              }
            >
              {transcribing ? (
                <Loader2 data-icon="inline-start" className="animate-spin" />
              ) : hasTranscript ? (
                <RefreshCw data-icon="inline-start" />
              ) : (
                <Wand2 data-icon="inline-start" />
              )}
              {transcribing
                ? "Transcrevendo…"
                : hasTranscript
                  ? "Transcrever novamente"
                  : "Iniciar transcrição"}
            </Button>
          ) : null}

          {hasTranscript ? (
            <Button size="sm" variant="ghost" onClick={() => setShowTranscript((v) => !v)}>
              {showTranscript ? "Ocultar transcrição" : "Ver transcrição"}
            </Button>
          ) : null}

          {hasTranscript && reuniao.id ? (
            <Button
              size="sm"
              variant="ghost"
              nativeButton={false}
              render={<Link href={`/reunioes/${reuniao.id}`} />}
            >
              <PencilLine data-icon="inline-start" />
              Editar transcrição
            </Button>
          ) : null}
        </div>

        {hasTranscript && showTranscript ? (
          <div
            className="prose prose-sm max-w-none rounded-lg border border-border bg-muted/30 p-3 text-sm leading-relaxed [&_p]:mb-2 last:[&_p]:mb-0"
            // Stored as sanitized HTML in the editor field (our own content).
            dangerouslySetInnerHTML={{ __html: reuniao.transcricao! }}
          />
        ) : null}
      </CardContent>
    </Card>
  )
}
