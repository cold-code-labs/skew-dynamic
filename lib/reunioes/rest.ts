import { revalidatePath } from "next/cache"

import { transcribeProviderKey } from "@/config/env"
import { pgrest } from "@/lib/data/client"
import { logError, logWarn } from "@/lib/log"

import { transcribeAudio } from "./transcribe"
import {
  normalizeStatus,
  parseLocutores,
  parseSegmentos,
  segmentosToHtml,
  type Locutores,
  type Reuniao,
  type Segmento,
} from "./types"

import type { ActionResult } from "@/lib/resources/types"

// PostgREST + Garage path for Reuniões Gravadas (Hauldr tier). Metadata + the
// structured transcript in the `reunioes` table (migration 0008); audio bytes in
// the project's Garage bucket. Audio streams back through the same-origin proxy
// /api/reunioes/<id>/audio. Transcription reuses the provider-agnostic
// transcribeAudio() — identical to the PocketBase path.

function safeName(name: string): string {
  return name.replace(/[^a-zA-Z0-9._-]+/g, "_").slice(0, 120) || "audio.webm"
}

function mapReuniao(r: Record<string, unknown>): Reuniao {
  return {
    id: r.id as string,
    titulo: (r.titulo as string) ?? "Reunião",
    status: normalizeStatus(r.status),
    duracao: (r.duracao as number) ?? 0,
    mime: (r.mime as string) || undefined,
    idioma: (r.idioma as string) || undefined,
    transcricao: (r.transcricao as string) || "",
    segmentos: parseSegmentos(r.segmentos),
    locutores: parseLocutores(r.locutores),
    created: r.created_at as string,
    audioUrl: r.audio_key ? `/api/reunioes/${r.id as string}/audio` : undefined,
  }
}

export async function listReunioesRest(): Promise<Reuniao[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/reunioes?select=*&order=created_at.desc",
  )
  return rows.map(mapReuniao)
}

export async function getReuniaoRest(id: string): Promise<Reuniao | null> {
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/reunioes?id=eq.${id}&select=*&limit=1`,
    )
    return rows[0] ? mapReuniao(rows[0]) : null
  } catch (e) {
    logWarn("reunioes", "getReuniaoRest: not found", e, { id })
    return null
  }
}

export async function criarReuniaoRest(form: FormData): Promise<ActionResult> {
  const { storageEnabled, putObject } = await import("@/lib/storage/garage")
  if (!storageEnabled()) {
    return { ok: false, error: "Armazenamento não configurado nesta instância." }
  }
  const audio = form.get("audio")
  if (!(audio instanceof File) || audio.size === 0) {
    return { ok: false, error: "Gravação vazia." }
  }
  const titulo = String(form.get("titulo") || "").trim()
  const duracao = Number(form.get("duracao") || 0)
  const mime = String(form.get("mime") || audio.type || "audio/webm")
  try {
    const bytes = new Uint8Array(await audio.arrayBuffer())
    const key = `reunioes/${crypto.randomUUID()}-${safeName(audio.name || "audio.webm")}`
    await putObject(key, bytes, mime)
    await pgrest("/reunioes", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({
        titulo: titulo || defaultTitle(),
        duracao: Math.round(duracao),
        mime,
        status: "gravada",
        idioma: "pt",
        audio_key: key,
      }),
    })
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "criarReuniaoRest", e, { titulo, duracao, mime })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar a gravação." }
  }
}

async function patch(id: string, body: Record<string, unknown>): Promise<void> {
  await pgrest(`/reunioes?id=eq.${id}`, {
    method: "PATCH",
    headers: { Prefer: "return=minimal" },
    body: JSON.stringify(body),
  })
}

export async function transcreverReuniaoRest(id: string): Promise<ActionResult> {
  if (!transcribeProviderKey()) {
    return { ok: false, error: "Configure a chave do provedor de transcrição no servidor." }
  }
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/reunioes?id=eq.${id}&select=audio_key,mime,idioma&limit=1`,
    )
    const rec = rows[0]
    const key = rec?.audio_key as string | undefined
    if (!rec || !key) return { ok: false, error: "Esta reunião não tem áudio gravado." }

    await patch(id, { status: "transcrevendo" })
    revalidatePath("/reunioes")

    const { getObject } = await import("@/lib/storage/garage")
    const obj = await getObject(key)
    const buffer = await new Response(obj.body).arrayBuffer()
    const blob = new Blob([buffer], { type: (rec.mime as string) || obj.contentType })
    const lang = (rec.idioma as string) || undefined

    const result = await transcribeAudio(blob, key.split("/").pop() || "audio.webm", lang)
    if (!result.ok) {
      logWarn("reunioes", "transcreverReuniaoRest: provider failed", undefined, {
        id,
        detail: result.error,
      })
      await patch(id, { status: "erro" })
      revalidatePath("/reunioes")
      return { ok: false, error: result.error }
    }

    const segments = result.segments.map((s) => ({ ...s, original: s.text }))
    await patch(id, {
      segmentos: segments,
      locutores: {},
      transcricao: segmentosToHtml(segments),
      status: "transcrita",
    })
    revalidatePath("/reunioes")
    revalidatePath(`/reunioes/${id}`)
    return { ok: true, message: "Transcrição concluída." }
  } catch (e) {
    logError("reunioes", "transcreverReuniaoRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha na transcrição." }
  }
}

export async function salvarTranscricaoRest(
  id: string,
  segmentos: Segmento[],
  locutores: Locutores,
): Promise<ActionResult> {
  try {
    await patch(id, {
      segmentos,
      locutores,
      transcricao: segmentosToHtml(segmentos, locutores),
    })
    revalidatePath("/reunioes")
    revalidatePath(`/reunioes/${id}`)
    return { ok: true, message: "Transcrição salva." }
  } catch (e) {
    logError("reunioes", "salvarTranscricaoRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar a transcrição." }
  }
}

export async function renomearReuniaoRest(id: string, titulo: string): Promise<ActionResult> {
  try {
    await patch(id, { titulo: titulo.trim() })
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "renomearReuniaoRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao renomear." }
  }
}

export async function excluirReuniaoRest(id: string): Promise<ActionResult> {
  try {
    const rows = await pgrest<Record<string, unknown>[]>(
      `/reunioes?id=eq.${id}&select=audio_key&limit=1`,
    )
    await pgrest(`/reunioes?id=eq.${id}`, {
      method: "DELETE",
      headers: { Prefer: "return=minimal" },
    })
    const key = rows[0]?.audio_key as string | undefined
    if (key) {
      const { deleteObject } = await import("@/lib/storage/garage")
      await deleteObject(key).catch(() => {})
    }
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "excluirReuniaoRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}

function defaultTitle(): string {
  const now = new Date()
  return `Reunião ${now.toLocaleDateString("pt-BR")} ${now.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  })}`
}
