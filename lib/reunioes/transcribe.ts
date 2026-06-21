import {
  ASSEMBLYAI_API_KEY,
  DEEPGRAM_API_KEY,
  DEEPGRAM_MODEL,
  OPENAI_API_KEY,
  OPENAI_BASE_URL,
  OPENAI_TRANSCRIBE_MODEL,
  TRANSCRIBE_PROVIDER,
} from "@/config/env"
import { logWarn } from "@/lib/log"

import type { Segmento } from "./types"

// Server-side transcription. Only imported from the "use server" actions in this
// folder, so the keys stay on the server. Three providers behind one function:
//
//   openai     → Whisper (/v1/audio/transcriptions, verbose_json): timestamped
//                segments, single speaker (no diarization).
//   deepgram   → Deepgram (/v1/listen) with diarization: per-turn speaker + times.
//   assemblyai → AssemblyAI (/v2/transcript) with speaker_labels: best diarization,
//                async upload+poll. Per-turn speaker (A/B/C…) + times.
//
// All return structured `segments` (stable speaker key + start/end seconds + text)
// plus a flat `text` for logging/preview. The caller turns segments into the
// stored HTML and the editable transcript. Whisper accepts files up to 25 MB.

export type TranscribeResult =
  | { ok: true; text: string; segments: Segmento[] }
  | { ok: false; error: string }

/** Group consecutive same-speaker segments into a flat "Locutor X: …" text. */
function segmentsToText(segments: Segmento[]): string {
  const lines: string[] = []
  let last: string | null = null
  for (const s of segments) {
    const text = s.text.trim()
    if (!text) continue
    if (s.speaker !== last) {
      lines.push(`Locutor ${s.speaker}: ${text}`)
      last = s.speaker
    } else {
      lines[lines.length - 1] += ` ${text}`
    }
  }
  return lines.join("\n\n").trim()
}

/** Deepgram numbers speakers 0,1,2…; map to A,B,C… to match AssemblyAI keys. */
function speakerLetter(n: number): string {
  return String.fromCharCode(65 + Math.max(0, n))
}

export async function transcribeAudio(
  audio: Blob,
  filename: string,
  language?: string,
): Promise<TranscribeResult> {
  if (audio.size === 0) {
    return { ok: false, error: "Gravação vazia — nada para transcrever." }
  }
  if (TRANSCRIBE_PROVIDER === "assemblyai") return transcribeAssemblyAI(audio, language)
  if (TRANSCRIBE_PROVIDER === "deepgram") return transcribeDeepgram(audio, language)
  return transcribeOpenAI(audio, filename, language)
}

// ── OpenAI Whisper ───────────────────────────────────────────────────────────
async function transcribeOpenAI(
  audio: Blob,
  filename: string,
  language?: string,
): Promise<TranscribeResult> {
  if (!OPENAI_API_KEY) {
    return { ok: false, error: "Configure OPENAI_API_KEY para transcrever." }
  }
  const form = new FormData()
  form.append("file", audio, filename)
  form.append("model", OPENAI_TRANSCRIBE_MODEL)
  // verbose_json yields per-segment timestamps (whisper-1). Newer models may
  // ignore it and return only `text` — handled by the single-segment fallback.
  form.append("response_format", "verbose_json")
  if (language) form.append("language", language)

  let res: Response
  try {
    res = await fetch(`${OPENAI_BASE_URL}/audio/transcriptions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${OPENAI_API_KEY}` },
      body: form,
    })
  } catch (e) {
    return networkError(e)
  }
  if (!res.ok) {
    const detail = await apiDetail(res)
    logWarn("reunioes", "OpenAI transcription rejected", undefined, { status: res.status, detail })
    return { ok: false, error: `OpenAI recusou a transcrição (${detail}).` }
  }
  try {
    const body = (await res.json()) as {
      text?: string
      segments?: { start?: number; end?: number; text?: string }[]
    }
    const text = (body.text ?? "").trim()
    // Whisper has no diarization → everything is one speaker ("A").
    const segments: Segmento[] = (body.segments ?? [])
      .map((s) => ({
        speaker: "A",
        start: Number(s.start) || 0,
        end: Number(s.end) || 0,
        text: (s.text ?? "").trim(),
      }))
      .filter((s) => s.text)
    if (segments.length > 0) return { ok: true, text: segmentsToText(segments), segments }
    if (!text) return { ok: false, error: "Transcrição vazia retornada." }
    return { ok: true, text, segments: [{ speaker: "A", start: 0, end: 0, text }] }
  } catch {
    return { ok: false, error: "Resposta inválida da API de transcrição." }
  }
}

// ── Deepgram (with speaker diarization) ──────────────────────────────────────
type DeepgramUtterance = { speaker?: number; transcript?: string; start?: number; end?: number }
type DeepgramResponse = {
  results?: {
    utterances?: DeepgramUtterance[]
    channels?: { alternatives?: { transcript?: string }[] }[]
  }
}

async function transcribeDeepgram(
  audio: Blob,
  language?: string,
): Promise<TranscribeResult> {
  if (!DEEPGRAM_API_KEY) {
    return { ok: false, error: "Configure DEEPGRAM_API_KEY para transcrever." }
  }
  const params = new URLSearchParams({
    model: DEEPGRAM_MODEL,
    diarize: "true",
    utterances: "true",
    punctuate: "true",
    smart_format: "true",
  })
  if (language) params.set("language", language)

  let res: Response
  try {
    res = await fetch(`https://api.deepgram.com/v1/listen?${params}`, {
      method: "POST",
      headers: {
        Authorization: `Token ${DEEPGRAM_API_KEY}`,
        "Content-Type": audio.type || "audio/webm",
      },
      body: audio,
    })
  } catch (e) {
    return networkError(e)
  }
  if (!res.ok) {
    const detail = await apiDetail(res)
    logWarn("reunioes", "Deepgram transcription rejected", undefined, { status: res.status, detail })
    return { ok: false, error: `Deepgram recusou a transcrição (${detail}).` }
  }
  try {
    const body = (await res.json()) as DeepgramResponse
    const utterances = body.results?.utterances ?? []
    const segments: Segmento[] = utterances
      .map((u) => ({
        speaker: speakerLetter(u.speaker ?? 0),
        start: Number(u.start) || 0,
        end: Number(u.end) || 0,
        text: (u.transcript ?? "").trim(),
      }))
      .filter((s) => s.text)
    if (segments.length > 0) return { ok: true, text: segmentsToText(segments), segments }
    // No utterances (e.g. single speaker) → fall back to the flat transcript.
    const flat = (body.results?.channels?.[0]?.alternatives?.[0]?.transcript ?? "").trim()
    if (!flat) return { ok: false, error: "Transcrição vazia retornada." }
    return { ok: true, text: flat, segments: [{ speaker: "A", start: 0, end: 0, text: flat }] }
  } catch {
    return { ok: false, error: "Resposta inválida da API de transcrição." }
  }
}

// ── AssemblyAI (best diarization) ────────────────────────────────────────────
// Flow: upload blob → submit transcript job → poll until done → format.
// AssemblyAI is async-only; polling is fast for short clips (<30s ≈ 5–10s wait).

type AssemblyUtterance = { speaker?: string; text?: string; start?: number; end?: number }
type AssemblyResponse = {
  id?: string
  status?: string
  text?: string
  utterances?: AssemblyUtterance[]
  error?: string
}

const ASSEMBLY_BASE = "https://api.assemblyai.com/v2"
const ASSEMBLY_POLL_MS = 2500
const ASSEMBLY_TIMEOUT_MS = 120_000

async function transcribeAssemblyAI(
  audio: Blob,
  language?: string,
): Promise<TranscribeResult> {
  if (!ASSEMBLYAI_API_KEY) {
    return { ok: false, error: "Configure ASSEMBLYAI_API_KEY para transcrever." }
  }
  const headers = { authorization: ASSEMBLYAI_API_KEY }

  // 1. Upload
  let uploadRes: Response
  try {
    uploadRes = await fetch(`${ASSEMBLY_BASE}/upload`, {
      method: "POST",
      headers: { ...headers, "content-type": "application/octet-stream" },
      body: audio,
    })
  } catch (e) {
    return networkError(e)
  }
  if (!uploadRes.ok) {
    const detail = await apiDetail(uploadRes)
    logWarn("reunioes", "AssemblyAI upload rejected", undefined, { status: uploadRes.status, detail })
    return { ok: false, error: `AssemblyAI recusou o upload (${detail}).` }
  }
  const { upload_url } = (await uploadRes.json()) as { upload_url?: string }
  if (!upload_url) return { ok: false, error: "AssemblyAI não retornou URL de upload." }

  // 2. Submit
  const lang = language === "pt" || !language ? "pt" : language
  let submitRes: Response
  try {
    submitRes = await fetch(`${ASSEMBLY_BASE}/transcript`, {
      method: "POST",
      headers: { ...headers, "content-type": "application/json" },
      body: JSON.stringify({ audio_url: upload_url, speaker_labels: true, language_code: lang }),
    })
  } catch (e) {
    return networkError(e)
  }
  if (!submitRes.ok) {
    const detail = await apiDetail(submitRes)
    logWarn("reunioes", "AssemblyAI submit rejected", undefined, { status: submitRes.status, detail })
    return { ok: false, error: `AssemblyAI recusou a transcrição (${detail}).` }
  }
  const { id } = (await submitRes.json()) as AssemblyResponse
  if (!id) return { ok: false, error: "AssemblyAI não retornou ID da transcrição." }

  // 3. Poll
  const deadline = Date.now() + ASSEMBLY_TIMEOUT_MS
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, ASSEMBLY_POLL_MS))
    let pollRes: Response
    try {
      pollRes = await fetch(`${ASSEMBLY_BASE}/transcript/${id}`, { headers })
    } catch (e) {
      return networkError(e)
    }
    if (!pollRes.ok) continue
    const body = (await pollRes.json()) as AssemblyResponse
    if (body.status === "error") {
      logWarn("reunioes", "AssemblyAI transcription error", undefined, { error: body.error })
      return { ok: false, error: `AssemblyAI retornou erro: ${body.error ?? "desconhecido"}.` }
    }
    if (body.status !== "completed") continue

    // 4. Format — AssemblyAI gives speaker (A/B/C…) + start/end in milliseconds.
    const utterances = body.utterances ?? []
    const segments: Segmento[] = utterances
      .map((u) => ({
        speaker: u.speaker ?? "A",
        start: (Number(u.start) || 0) / 1000,
        end: (Number(u.end) || 0) / 1000,
        text: (u.text ?? "").trim(),
      }))
      .filter((s) => s.text)
    if (segments.length > 0) return { ok: true, text: segmentsToText(segments), segments }
    const flat = (body.text ?? "").trim()
    if (!flat) return { ok: false, error: "Transcrição vazia retornada." }
    return { ok: true, text: flat, segments: [{ speaker: "A", start: 0, end: 0, text: flat }] }
  }

  return { ok: false, error: "Tempo limite de transcrição esgotado (AssemblyAI)." }
}

// ── shared helpers ───────────────────────────────────────────────────────────
function networkError(e: unknown): TranscribeResult {
  logWarn("reunioes", "transcription network failure", e, { provider: TRANSCRIBE_PROVIDER })
  return {
    ok: false,
    error: e instanceof Error ? `Falha de rede: ${e.message}` : "Falha de rede.",
  }
}

async function apiDetail(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as {
      error?: { message?: string }
      err_msg?: string
      message?: string
    }
    return body?.error?.message || body?.err_msg || body?.message || `${res.status}`
  } catch {
    return `${res.status}`
  }
}
