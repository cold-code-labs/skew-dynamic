// Thin client over the shared Hauldr Realtime service (WebSocket). Vendored from
// @hauldr/client's `live` namespace and trimmed to what this template uses —
// broadcast + presence on a topic, public or private (RLS-gated). Kept
// dependency-free so it runs in the browser as-is; `broadcast` also works
// server-side (fetch). The tenant is resolved from the URL host's first label.

export type LiveMessage = { event: string; payload: unknown }

/** Who is on a channel: member key → the state each member published. */
export type PresenceState = Record<string, Array<Record<string, unknown>>>

export type ChannelOptions = { private?: boolean }
export type PresenceOptions = ChannelOptions & {
  key?: string
  initial?: Record<string, unknown>
}
export type Subscription = { unsubscribe(): void }
export type PresenceChannel = Subscription & {
  track(state: Record<string, unknown>): void
  untrack(): void
}

/** Client-side realtime config a server component hands to a client component:
 *  the public WSS URL + the user's own access token + their presence identity. */
export type RealtimeProps = {
  url: string
  accessToken: string
  me: { key: string; name: string }
}

const HEARTBEAT_MS = 30_000

type Frame = { event?: string; payload?: unknown; ref?: string }
type MetaState = Record<string, Array<Record<string, unknown>>>

function flatten(meta: MetaState): PresenceState {
  const out: PresenceState = {}
  for (const [key, metas] of Object.entries(meta)) {
    out[key] = metas.map((m) => {
      const { phx_ref: _r, phx_ref_prev: _p, ...rest } = m
      return rest
    })
  }
  return out
}
function applyState(meta: MetaState, state: Record<string, { metas?: Array<Record<string, unknown>> }>) {
  for (const k of Object.keys(meta)) delete meta[k]
  for (const [key, v] of Object.entries(state)) meta[key] = [...(v.metas ?? [])]
}
function applyDiff(
  meta: MetaState,
  diff: {
    joins?: Record<string, { metas?: Array<Record<string, unknown>> }>
    leaves?: Record<string, { metas?: Array<Record<string, unknown>> }>
  },
) {
  for (const [key, v] of Object.entries(diff.leaves ?? {})) {
    const gone = new Set((v.metas ?? []).map((m) => m.phx_ref))
    meta[key] = (meta[key] ?? []).filter((m) => !gone.has(m.phx_ref))
    if (!meta[key].length) delete meta[key]
  }
  for (const [key, v] of Object.entries(diff.joins ?? {})) {
    const have = new Set((meta[key] ?? []).map((m) => m.phx_ref))
    meta[key] = [...(meta[key] ?? []), ...(v.metas ?? []).filter((m) => !have.has(m.phx_ref))]
  }
}

/** Read a JWT's `exp` (secs) without verifying — to schedule a refresh before it. */
function decodeExp(token?: string): number | undefined {
  const part = token?.split(".")[1]
  if (!part) return undefined
  try {
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/")
    const pad = "=".repeat((4 - (b64.length % 4)) % 4)
    const json = JSON.parse(
      typeof atob === "function" ? atob(b64 + pad) : Buffer.from(b64 + pad, "base64").toString("utf8"),
    )
    return typeof json.exp === "number" ? json.exp : undefined
  } catch {
    return undefined
  }
}

export type GetToken = () => string | null | undefined | Promise<string | null | undefined>

export class HauldrLive {
  private readonly httpUrl: string
  private readonly wsUrl: string
  private currentToken?: string
  private readonly channels = new Set<(event: string, payload: unknown) => void>()
  private refreshTimer?: ReturnType<typeof setTimeout>
  constructor(
    url: string,
    accessToken?: string,
    private readonly getToken?: GetToken,
  ) {
    this.httpUrl = url.replace(/\/+$/, "")
    this.wsUrl = this.httpUrl.replace(/^http/, "ws")
    this.currentToken = accessToken
  }

  /** Push a fresh token to every open channel (re-authorizes private ones). */
  setAuth(token: string): void {
    this.currentToken = token
    for (const send of this.channels) send("access_token", { access_token: token })
    this.scheduleRefresh()
  }

  private scheduleRefresh(delayMs?: number): void {
    if (!this.getToken || this.channels.size === 0) return
    if (this.refreshTimer) clearTimeout(this.refreshTimer)
    const exp = decodeExp(this.currentToken)
    const ms = delayMs ?? (exp ? Math.max(5_000, exp * 1000 - Date.now() - 60_000) : 50 * 60_000)
    this.refreshTimer = setTimeout(async () => {
      this.refreshTimer = undefined
      try {
        const t = await this.getToken!()
        if (t) this.setAuth(t)
        else this.scheduleRefresh(30_000)
      } catch {
        this.scheduleRefresh(30_000)
      }
    }, ms)
  }

  /** Subscribe to broadcast events on a topic. */
  on(topic: string, cb: (m: LiveMessage) => void, opts: ChannelOptions = {}): Subscription {
    const h = this.open(topic, opts, {}, (f) => {
      if (f.event === "broadcast" && f.payload) {
        const p = f.payload as { event?: string; payload?: unknown }
        cb({ event: p.event ?? "", payload: p.payload })
      }
    })
    return { unsubscribe: h.stop }
  }

  /** Track who is on a channel; `onSync` fires with the full state on every change. */
  presence(topic: string, onSync: (s: PresenceState) => void, opts: PresenceOptions = {}): PresenceChannel {
    const meta: MetaState = {}
    const emit = () => onSync(flatten(meta))
    const h = this.open(topic, opts, { presence: { key: opts.key ?? "" } }, (f) => {
      if (f.event === "presence_state" && f.payload) {
        applyState(meta, f.payload as Record<string, { metas?: Array<Record<string, unknown>> }>)
        emit()
      } else if (f.event === "presence_diff" && f.payload) {
        applyDiff(meta, f.payload as Parameters<typeof applyDiff>[1])
        emit()
      }
    })
    if (opts.initial) h.send("presence", { type: "presence", event: "track", payload: opts.initial })
    return {
      track: (state) => h.send("presence", { type: "presence", event: "track", payload: state }),
      untrack: () => h.send("presence", { type: "presence", event: "untrack" }),
      unsubscribe: h.stop,
    }
  }

  /** Publish an event to a topic (server-side after a write, or client-to-client). */
  async broadcast(topic: string, event: string, payload: unknown, opts: ChannelOptions = {}): Promise<void> {
    const r = await fetch(`${this.httpUrl}/api/broadcast`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        ...(this.currentToken
          ? { apikey: this.currentToken, Authorization: `Bearer ${this.currentToken}` }
          : {}),
      },
      body: JSON.stringify({ messages: [{ topic, event, payload, private: !!opts.private }] }),
    })
    if (!r.ok && r.status !== 202) throw new Error(`hauldr.live.broadcast → ${r.status}`)
  }

  private open(
    topic: string,
    opts: ChannelOptions,
    configOverride: Record<string, unknown>,
    onFrame: (f: Frame) => void,
  ): { stop(): void; send(event: string, payload: unknown): void } {
    const WS = (globalThis as { WebSocket?: typeof WebSocket }).WebSocket
    if (!WS) throw new Error("hauldr realtime needs a WebSocket (browser)")
    const apikey = encodeURIComponent(this.currentToken ?? "")
    const ws = new WS(`${this.wsUrl}/socket/websocket?vsn=1.0.0&apikey=${apikey}`)
    const realtimeTopic = `realtime:${topic}`
    const joinRef = "1"
    let ref = 1
    const nextRef = () => String(++ref)
    let heartbeat: ReturnType<typeof setInterval> | undefined
    let joined = false
    const pending: string[] = []

    const rawSend = (s: string) => {
      try {
        ws.send(s)
      } catch {
        /* closing */
      }
    }
    const send = (event: string, payload: unknown) => {
      const s = JSON.stringify({ topic: realtimeTopic, event, ref: nextRef(), payload })
      if (joined) rawSend(s)
      else pending.push(s)
    }

    ws.onopen = () => {
      rawSend(
        JSON.stringify({
          topic: realtimeTopic,
          event: "phx_join",
          ref: joinRef,
          join_ref: joinRef,
          payload: {
            config: {
              broadcast: { self: false },
              presence: { key: "" },
              postgres_changes: [],
              private: !!opts.private,
              ...configOverride,
            },
            ...(this.currentToken ? { access_token: this.currentToken } : {}),
          },
        }),
      )
      heartbeat = setInterval(
        () => rawSend(JSON.stringify({ topic: "phoenix", event: "heartbeat", ref: nextRef(), payload: {} })),
        HEARTBEAT_MS,
      )
    }
    ws.onmessage = (ev: MessageEvent) => {
      let m: Frame
      try {
        m = JSON.parse(typeof ev.data === "string" ? ev.data : String(ev.data))
      } catch {
        return
      }
      if (!joined && m.event === "phx_reply" && m.ref === joinRef) {
        if ((m.payload as { status?: string } | undefined)?.status === "ok") {
          joined = true
          for (const s of pending.splice(0)) rawSend(s)
          this.channels.add(send)
          if (this.getToken && !this.refreshTimer) this.scheduleRefresh()
        }
      }
      onFrame(m)
    }
    const stop = () => {
      if (heartbeat) clearInterval(heartbeat)
      this.channels.delete(send)
      if (this.channels.size === 0 && this.refreshTimer) {
        clearTimeout(this.refreshTimer)
        this.refreshTimer = undefined
      }
      try {
        ws.close()
      } catch {
        /* closed */
      }
    }
    ws.onclose = () => {
      if (heartbeat) clearInterval(heartbeat)
    }
    return { stop, send }
  }
}
