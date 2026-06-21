import {
  DATA_MODE,
  PB_CF_ACCESS_CLIENT_ID,
  PB_CF_ACCESS_CLIENT_SECRET,
  POCKETBASE_URL,
} from "@/config/env"
import { pbServer } from "@/lib/auth/pocketbase"
import { getSession } from "@/lib/auth/session"
import { visibleChannelIds } from "@/lib/chat/data"
import { logWarn } from "@/lib/log"

// ─────────────────────────────────────────────────────────────────────────────
// Realtime relay for Chat — SERVER-SIDE bridge to PocketBase's realtime SSE.
//
// The bundled PocketBase is internal (never exposed to the browser). This route
// is the seam: it subscribes to PB's realtime stream server-side, AUTHENTICATED
// as the requesting user and SCOPED to exactly the channels the app says they
// may see (visibleChannelIds — the same access logic as the sidebar), then pipes
// new-message events to the browser as a plain same-origin SSE stream.
//
// We talk to PB's realtime API with raw fetch (not the SDK) so we don't depend
// on a global EventSource in Node. PB realtime is two calls:
//   1. GET  /api/realtime           → SSE; first event PB_CONNECT carries clientId
//   2. POST /api/realtime           → set this client's subscriptions
// then every matching record change arrives on the GET stream. We re-emit each
// as an unnamed SSE event so the browser's EventSource.onmessage catches it.
// ─────────────────────────────────────────────────────────────────────────────

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

function cfHeaders(): Record<string, string> {
  if (PB_CF_ACCESS_CLIENT_ID && PB_CF_ACCESS_CLIENT_SECRET) {
    return {
      "CF-Access-Client-Id": PB_CF_ACCESS_CLIENT_ID,
      "CF-Access-Client-Secret": PB_CF_ACCESS_CLIENT_SECRET,
    }
  }
  return {}
}

const SSE_HEADERS = {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache, no-transform",
  Connection: "keep-alive",
  "X-Accel-Buffering": "no",
}

export async function GET(request: Request): Promise<Response> {
  const user = await getSession()
  if (!user) return new Response("Unauthorized", { status: 401 })

  // Golden rule: with no real backend (stub/postgrest) there's no PocketBase to
  // relay from — return a benign, closed SSE stream so the client degrades
  // gracefully (demo channels stay static) instead of hammering a dead PB URL.
  if (DATA_MODE !== "pocketbase") {
    return new Response("event: disabled\ndata: {}\n\n", { headers: SSE_HEADERS })
  }

  const channelIds = await visibleChannelIds(user)
  const pb = await pbServer()
  const token = pb.authStore.token

  const encoder = new TextEncoder()
  const upstream = new AbortController()
  // Tie the upstream PB connection to the browser disconnecting.
  request.signal.addEventListener("abort", () => upstream.abort())

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (data: string) => {
        try {
          controller.enqueue(encoder.encode(data))
        } catch (_) {
          // controller already closed
        }
      }

      try {
        const res = await fetch(`${POCKETBASE_URL}/api/realtime`, {
          headers: { Accept: "text/event-stream", ...cfHeaders() },
          signal: upstream.signal,
        })
        if (!res.ok || !res.body) {
          send(`event: error\ndata: ${JSON.stringify({ status: res.status })}\n\n`)
          controller.close()
          return
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ""
        let subscribed = false

        // Heartbeat so proxies don't drop an idle connection.
        const ping = setInterval(() => send(`: ping\n\n`), 25000)

        const cleanup = () => {
          clearInterval(ping)
          try {
            reader.cancel()
          } catch (_) {}
          try {
            controller.close()
          } catch (_) {}
        }
        upstream.signal.addEventListener("abort", cleanup)

        // Tell the client we're connected (so the UI can flip to "ao vivo").
        send(`event: ready\ndata: {}\n\n`)

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })

          // SSE frames are separated by a blank line.
          let sep
          while ((sep = buffer.indexOf("\n\n")) !== -1) {
            const frame = buffer.slice(0, sep)
            buffer = buffer.slice(sep + 2)
            const evt = parseFrame(frame)
            if (!evt) continue

            if (evt.event === "PB_CONNECT") {
              const clientId = safeJson(evt.data)?.clientId as string | undefined
              if (clientId && !subscribed) {
                subscribed = true
                await setSubscriptions(clientId, channelIds, token)
              }
              continue
            }

            // Any other named event is a subscription notification: a record
            // change. Forward the payload as an unnamed SSE event for onmessage.
            if (evt.data) send(`data: ${evt.data}\n\n`)
          }
        }
        cleanup()
      } catch (e) {
        if (!upstream.signal.aborted) {
          logWarn("chat", "realtime relay failed", e)
          send(`event: error\ndata: {}\n\n`)
        }
        try {
          controller.close()
        } catch (_) {}
      }
    },
    cancel() {
      upstream.abort()
    },
  })

  return new Response(stream, { headers: SSE_HEADERS })
}

// POST the client's subscriptions to PB. We subscribe to `chat_messages` scoped
// by a filter to the user's visible channels (PB encodes per-subscription query
// options as `?options=<json>`). With no visible channels we subscribe to a
// no-match filter so the connection stays open but quiet.
async function setSubscriptions(
  clientId: string,
  channelIds: string[],
  token: string,
): Promise<void> {
  const filter = channelIds.length
    ? channelIds.map((id) => `channel="${id}"`).join(" || ")
    : 'id=""'
  const options = encodeURIComponent(JSON.stringify({ query: { filter } }))
  const subscriptions = [`chat_messages?options=${options}`]

  await fetch(`${POCKETBASE_URL}/api/realtime`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: token } : {}),
      ...cfHeaders(),
    },
    body: JSON.stringify({ clientId, subscriptions }),
  })
}

function parseFrame(frame: string): { event: string; data: string } | null {
  let event = "message"
  const dataLines: string[] = []
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim()
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim())
  }
  if (!dataLines.length && event === "message") return null
  return { event, data: dataLines.join("\n") }
}

function safeJson(s: string): Record<string, unknown> | null {
  try {
    return JSON.parse(s)
  } catch (_) {
    return null
  }
}
