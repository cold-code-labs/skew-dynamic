"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE, transcribeProviderKey } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { logError, logWarn } from "@/lib/log"
import { getCurrentTenantId } from "@/lib/tenant"

import { transcribeAudio } from "./transcribe"
import {
  parseLocutores,
  parseSegmentos,
  segmentosToHtml,
  type Locutores,
  type Segmento,
} from "./types"

import type { ActionResult } from "@/lib/resources/types"

const DEMO: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase para gravar reuniões.",
}

// Create a meeting from a browser recording. The client posts the audio Blob
// plus title/duration/mime as multipart form-data (server actions are bumped to
// 32MB in next.config). Mirrors lib/storage/actions.ts#uploadDocumento.
export async function criarReuniao(form: FormData): Promise<ActionResult> {
  const denied = await requireCapability("files.upload")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { criarReuniaoRest } = await import("./rest")
    return criarReuniaoRest(form)
  }
  if (DATA_MODE !== "pocketbase") return DEMO

  const audio = form.get("audio")
  if (!(audio instanceof File) || audio.size === 0) {
    return { ok: false, error: "Gravação vazia." }
  }
  const titulo = String(form.get("titulo") || "").trim()
  const duracao = Number(form.get("duracao") || 0)
  const mime = String(form.get("mime") || audio.type || "audio/webm")

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const data = new FormData()
    data.append("titulo", titulo || defaultTitle())
    data.append("duracao", String(Math.round(duracao)))
    data.append("mime", mime)
    data.append("status", "gravada")
    data.append("idioma", "pt")
    data.append("organization", await getCurrentTenantId())
    data.append("audio", audio)
    await pb.collection("reunioes").create(data)
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "criarReuniao", e, { titulo, duracao, mime })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar a gravação." }
  }
}

// Transcribe a stored meeting with OpenAI Whisper: download the protected audio
// (per-request token), send it to the API, save the text back on the record.
export async function transcreverReuniao(id: string): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { transcreverReuniaoRest } = await import("./rest")
    return transcreverReuniaoRest(id)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  if (!transcribeProviderKey()) {
    return { ok: false, error: "Configure a chave do provedor de transcrição no servidor." }
  }

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const rec = await pb.collection("reunioes").getOne(id)
    const filename = rec.audio as string
    if (!filename) {
      return { ok: false, error: "Esta reunião não tem áudio gravado." }
    }

    // Mark in-progress so the list reflects the running job.
    await pb.collection("reunioes").update(id, { status: "transcrevendo" })
    revalidatePath("/reunioes")

    // Download the protected audio bytes with a short-lived token.
    const token = await pb.files.getToken()
    const url = pb.files.getURL(rec, filename, { token })
    const audioRes = await fetch(url)
    if (!audioRes.ok) {
      logWarn("reunioes", "transcreverReuniao: audio fetch failed", undefined, {
        id,
        status: audioRes.status,
      })
      await pb.collection("reunioes").update(id, { status: "erro" })
      revalidatePath("/reunioes")
      return { ok: false, error: "Não foi possível ler o áudio armazenado." }
    }
    const blob = await audioRes.blob()
    const lang = (rec.idioma as string) || undefined

    const result = await transcribeAudio(blob, filename, lang)
    if (!result.ok) {
      logWarn("reunioes", "transcreverReuniao: provider failed", undefined, {
        id,
        detail: result.error,
      })
      await pb.collection("reunioes").update(id, { status: "erro" })
      revalidatePath("/reunioes")
      return { ok: false, error: result.error }
    }

    // Store the structured turns (with timing) and a fresh HTML render. Capture
    // each turn's text as its `original` baseline so later manual edits can be
    // compared and reverted. New transcriptions start with default speaker names.
    const segments = result.segments.map((s) => ({ ...s, original: s.text }))
    await pb.collection("reunioes").update(id, {
      segmentos: segments,
      locutores: {},
      transcricao: segmentosToHtml(segments),
      status: "transcrita",
    })
    revalidatePath("/reunioes")
    revalidatePath(`/reunioes/${id}`)
    return { ok: true, message: "Transcrição concluída." }
  } catch (e) {
    logError("reunioes", "transcreverReuniao", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha na transcrição." }
  }
}

// Persist manual edits from the transcript editor (/reunioes/[id]): corrected
// segment text, speaker reassignment, and speaker display names. The HTML render
// is recomputed server-side so the list preview and fallback stay in sync — the
// client never sends HTML. Audio and timing are untouched.
export async function salvarTranscricao(
  id: string,
  input: { segmentos: Segmento[]; locutores: Locutores },
): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }

  // Re-parse defensively: this crosses the network from the browser.
  const segmentos = parseSegmentos(input?.segmentos)
  const locutores = parseLocutores(input?.locutores)
  if (segmentos.length === 0) {
    return { ok: false, error: "Transcrição vazia — nada para salvar." }
  }

  if (DATA_MODE === "postgrest") {
    const { salvarTranscricaoRest } = await import("./rest")
    return salvarTranscricaoRest(id, segmentos, locutores)
  }
  if (DATA_MODE !== "pocketbase") return DEMO

  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    await pb.collection("reunioes").update(id, {
      segmentos,
      locutores,
      transcricao: segmentosToHtml(segmentos, locutores),
    })
    revalidatePath("/reunioes")
    revalidatePath(`/reunioes/${id}`)
    return { ok: true, message: "Transcrição salva." }
  } catch (e) {
    logError("reunioes", "salvarTranscricao", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar a transcrição." }
  }
}

export async function renomearReuniao(id: string, titulo: string): Promise<ActionResult> {
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  const clean = titulo.trim()
  if (!clean) return { ok: false, error: "Informe um título." }
  if (DATA_MODE === "postgrest") {
    const { renomearReuniaoRest } = await import("./rest")
    return renomearReuniaoRest(id, clean)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    await pb.collection("reunioes").update(id, { titulo: clean })
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "renomearReuniao", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao renomear." }
  }
}

export async function excluirReuniao(id: string): Promise<ActionResult> {
  const denied = await requireCapability("data.delete")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { excluirReuniaoRest } = await import("./rest")
    return excluirReuniaoRest(id)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    await pb.collection("reunioes").delete(id)
    revalidatePath("/reunioes")
    return { ok: true }
  } catch (e) {
    logError("reunioes", "excluirReuniao", e, { id })
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
