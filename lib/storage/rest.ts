import { revalidatePath } from "next/cache"

import { pgrest } from "@/lib/data/client"
import { logError } from "@/lib/log"

import type { Documento } from "./documents"
import type { ActionResult } from "@/lib/resources/types"

// PostgREST + Garage path for the Storage module (Hauldr tier). Metadata in the
// `documentos` table (migration 0007); bytes in the project's Garage bucket. The
// browser downloads through the same-origin proxy at /api/arquivos/<id>/download,
// so the bucket itself is never public.

function safeName(name: string): string {
  return name.replace(/[^a-zA-Z0-9._-]+/g, "_").slice(0, 120) || "arquivo"
}

export async function listDocumentosRest(): Promise<Documento[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/documentos?select=*&order=name.asc",
  )
  return rows.map((r) => ({
    id: r.id as string,
    name: (r.name as string) ?? "arquivo",
    category: (r.category as string) || "Geral",
    size: Number(r.size ?? 0),
    created: r.created_at as string,
    url: `/api/arquivos/${r.id as string}/download`,
  }))
}

export async function uploadDocumentoRest(form: FormData): Promise<ActionResult> {
  const { storageEnabled, putObject } = await import("./garage")
  if (!storageEnabled()) {
    return { ok: false, error: "Armazenamento não configurado nesta instância." }
  }
  const file = form.get("file")
  if (!(file instanceof File) || file.size === 0) {
    return { ok: false, error: "Selecione um arquivo." }
  }
  try {
    const bytes = new Uint8Array(await file.arrayBuffer())
    const contentType = file.type || "application/octet-stream"
    const key = `documentos/${crypto.randomUUID()}-${safeName(file.name)}`
    await putObject(key, bytes, contentType)
    await pgrest("/documentos", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        name: String(form.get("name") || file.name),
        category: String(form.get("category") || "Geral"),
        size: file.size,
        s3_key: key,
        content_type: contentType,
      }),
    })
    revalidatePath("/arquivos")
    return { ok: true }
  } catch (e) {
    logError("arquivos", "uploadDocumentoRest", e)
    return { ok: false, error: e instanceof Error ? e.message : "Falha no upload." }
  }
}

export async function deleteDocumentoRest(id: string): Promise<ActionResult> {
  try {
    // Look up the object key first, then drop the row, then best-effort remove
    // the bytes (an orphaned object is harmless; a dangling row is not).
    const rows = await pgrest<Record<string, unknown>[]>(
      `/documentos?id=eq.${id}&select=s3_key&limit=1`,
    )
    await pgrest(`/documentos?id=eq.${id}`, {
      method: "DELETE",
      headers: { Prefer: "return=minimal" },
    })
    const key = rows[0]?.s3_key as string | undefined
    if (key) {
      const { deleteObject } = await import("./garage")
      await deleteObject(key).catch(() => {})
    }
    revalidatePath("/arquivos")
    return { ok: true }
  } catch (e) {
    logError("arquivos", "deleteDocumentoRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}
