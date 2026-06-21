import {
  PB_CF_ACCESS_CLIENT_ID,
  PB_CF_ACCESS_CLIENT_SECRET,
} from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { pbServer } from "@/lib/auth/pocketbase"
import { logWarn } from "@/lib/log"

// ─────────────────────────────────────────────────────────────────────────────
// File download proxy for the Arquivos (Storage) module.
//
// The bundled PocketBase is internal (127.0.0.1:8090) and NEVER exposed to the
// browser, so a signed PB file URL (pb.files.getURL) is unreachable from the
// client — the download link just fails. This route is the same-origin seam:
// authenticated as the requesting user, it resolves the protected file, mints a
// short-lived file token, fetches the bytes from the internal PB, and streams
// them back through the app's public origin with a friendly download filename.
// HTTP Range is forwarded so large files / resumable downloads work.
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

// RFC 5987 Content-Disposition with a UTF-8 filename (plus an ASCII fallback).
function contentDisposition(name: string): string {
  const ascii = name.replace(/[^\x20-\x7e]/g, "_").replace(/["\\]/g, "_")
  return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(name)}`
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const denied = await requireCapability("data.read")
  if (denied) return new Response(denied, { status: 401 })

  const { id } = await params
  try {
    const pb = await pbServer()
    const rec = await pb.collection("documentos").getOne(id)
    const filename = rec.file as string
    if (!filename) return new Response("Sem arquivo.", { status: 404 })

    const token = await pb.files.getToken()
    const fileUrl = pb.files.getURL(rec, filename, { token })

    const range = request.headers.get("range")
    const upstream = await fetch(fileUrl, {
      headers: {
        ...cfHeaders(),
        ...(range ? { Range: range } : {}),
      },
    })
    if (!upstream.ok && upstream.status !== 206) {
      logWarn("storage", "download proxy upstream failed", undefined, {
        id,
        status: upstream.status,
      })
      return new Response("Falha ao ler o arquivo.", { status: 502 })
    }

    const headers = new Headers()
    for (const h of ["content-type", "content-length", "content-range", "accept-ranges"]) {
      const v = upstream.headers.get(h)
      if (v) headers.set(h, v)
    }
    if (!headers.has("accept-ranges")) headers.set("accept-ranges", "bytes")
    if (!headers.has("content-type")) headers.set("content-type", "application/octet-stream")
    headers.set("content-disposition", contentDisposition((rec.name as string) || "arquivo"))
    // Per-user protected file — never cache at the edge.
    headers.set("cache-control", "private, no-store")

    return new Response(upstream.body, { status: upstream.status, headers })
  } catch (e) {
    logWarn("storage", "download proxy error", e, { id })
    return new Response("Não encontrado.", { status: 404 })
  }
}
