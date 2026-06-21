import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { pgrest } from "@/lib/data/client"
import { logWarn } from "@/lib/log"

// Audio proxy for the Reuniões Gravadas module (Hauldr tier). The recording
// lives in the project's Garage bucket (never public); this same-origin route is
// authenticated as the requesting user, fetches the bytes (honouring HTTP Range
// so the <audio> player can seek), and streams them back. Mirrors the Arquivos
// download proxy.

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
      `/reunioes?id=eq.${id}&select=audio_key&limit=1`,
    )
    const key = rows[0]?.audio_key as string | undefined
    if (!key) return new Response("Sem áudio.", { status: 404 })

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
    logWarn("reunioes", "audio proxy error", e, { id })
    return new Response("Não encontrado.", { status: 404 })
  }
}
