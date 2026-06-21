import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { pgrest } from "@/lib/data/client"
import { logWarn } from "@/lib/log"

// Attachment proxy for chat messages (Hauldr tier). The file lives in the
// project's Garage bucket (never public); this same-origin route authenticates
// the caller, looks up the message's object key, and streams the bytes back
// (HTTP Range honoured). Mirrors the Arquivos download proxy.

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const denied = await requireCapability("data.read")
  if (denied) return new Response(denied, { status: 401 })
  if (DATA_MODE !== "postgrest") return new Response("Indisponível.", { status: 404 })

  const { id } = await params
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/chat_messages?id=eq.${id}&select=anexo&limit=1`,
    )
    const key = rows[0]?.anexo as string | undefined
    if (!key) return new Response("Sem anexo.", { status: 404 })

    const { getObject } = await import("@/lib/storage/garage")
    const obj = await getObject(key, request.headers.get("range") ?? undefined)

    const headers = new Headers()
    headers.set("content-type", obj.contentType)
    if (obj.contentLength != null) headers.set("content-length", String(obj.contentLength))
    if (obj.contentRange) headers.set("content-range", obj.contentRange)
    headers.set("accept-ranges", "bytes")
    headers.set("cache-control", "private, no-store")
    return new Response(obj.body, { status: obj.status, headers })
  } catch (e) {
    logWarn("chat", "anexo proxy error", e, { id })
    return new Response("Não encontrado.", { status: 404 })
  }
}
