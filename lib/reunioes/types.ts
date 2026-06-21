// Client-safe types + pure helpers for the Reuniões Gravadas module. Kept apart
// from meetings.ts (which imports the server-only PocketBase client) so client
// components can use these without dragging server code into the browser bundle.

export type ReuniaoStatus = "gravada" | "transcrevendo" | "transcrita" | "erro"

/**
 * One spoken turn in a transcript. `speaker` is a *stable key* (e.g. "A", "B"),
 * not the display name — the name lives in the `locutores` map so renaming a
 * speaker relabels every one of their segments at once. Times are in seconds
 * (floats) from the start of the recording; 0/0 means "unknown" (e.g. segments
 * recovered from a legacy transcript that had no timing).
 */
export type Segmento = {
  speaker: string
  start: number
  end: number
  text: string
  /**
   * The text exactly as the provider transcribed it. Set once at transcription
   * time and never overwritten by manual edits, so the original is always
   * recoverable (the editor shows "editado" + a Restaurar action when `text`
   * diverges from it). Legacy segments without it fall back to their own text.
   */
  original?: string
}

/** speaker key → display name, e.g. { A: "João", B: "Maria" }. */
export type Locutores = Record<string, string>

export type Reuniao = {
  id?: string
  titulo: string
  status: ReuniaoStatus
  duracao: number
  mime?: string
  idioma?: string
  transcricao?: string
  /** Structured, timestamped turns. Empty for legacy/flat transcripts. */
  segmentos?: Segmento[]
  /** Speaker display-name overrides. */
  locutores?: Locutores
  created?: string
  /** Signed audio URL (only present in PocketBase mode with a stored file). */
  audioUrl?: string
}

export const STATUS_LABELS: Record<ReuniaoStatus, string> = {
  gravada: "Gravada",
  transcrevendo: "Transcrevendo…",
  transcrita: "Transcrita",
  erro: "Erro",
}

export function normalizeStatus(value: unknown): ReuniaoStatus {
  return value === "transcrevendo" || value === "transcrita" || value === "erro"
    ? value
    : "gravada"
}

/** Format a duration in seconds as m:ss (or h:mm:ss for long meetings). */
export function formatDuracao(seconds: number): string {
  if (!seconds || seconds < 0) return "0:00"
  const s = Math.floor(seconds % 60)
  const m = Math.floor((seconds / 60) % 60)
  const h = Math.floor(seconds / 3600)
  const mm = m.toString().padStart(2, "0")
  const ss = s.toString().padStart(2, "0")
  return h > 0 ? `${h}:${mm}:${ss}` : `${m}:${ss}`
}

/** Timestamp marker for a transcript line — same shape as a duration. */
export const formatTimestamp = formatDuracao

/** Display name for a speaker key, falling back to "Locutor A". */
export function speakerLabel(speaker: string, locutores?: Locutores): string {
  const custom = locutores?.[speaker]?.trim()
  return custom || `Locutor ${speaker}`
}

/** Distinct speaker keys in first-appearance order. */
export function speakerKeys(segmentos: Segmento[]): string[] {
  const seen: string[] = []
  for (const s of segmentos) if (!seen.includes(s.speaker)) seen.push(s.speaker)
  return seen
}

/** Tolerant parse of the `segmentos` json field (PB may hand back a string). */
export function parseSegmentos(raw: unknown): Segmento[] {
  let value = raw
  if (typeof value === "string") {
    if (!value.trim()) return []
    try {
      value = JSON.parse(value)
    } catch {
      return []
    }
  }
  if (!Array.isArray(value)) return []
  const out: Segmento[] = []
  for (const item of value) {
    if (!item || typeof item !== "object") continue
    const o = item as Record<string, unknown>
    const text = typeof o.text === "string" ? o.text : ""
    if (!text.trim()) continue
    out.push({
      speaker: typeof o.speaker === "string" && o.speaker ? o.speaker : "A",
      start: Number(o.start) || 0,
      end: Number(o.end) || 0,
      text,
      // Default the baseline to the current text for legacy rows (transcribed
      // before originals were kept) — they were never edited, so text IS the
      // original. New transcriptions set this explicitly.
      original: typeof o.original === "string" ? o.original : text,
    })
  }
  return out
}

/** True when a segment's text has been manually changed from the transcription. */
export function isEdited(seg: Segmento): boolean {
  if (seg.original == null) return false
  return seg.original.trim() !== seg.text.trim()
}

/** Tolerant parse of the `locutores` json field. */
export function parseLocutores(raw: unknown): Locutores {
  let value = raw
  if (typeof value === "string") {
    if (!value.trim()) return {}
    try {
      value = JSON.parse(value)
    } catch {
      return {}
    }
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) return {}
  const out: Locutores = {}
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    if (typeof v === "string" && v.trim()) out[k] = v.trim()
  }
  return out
}

/**
 * Render structured turns to the sanitized HTML we store in `transcricao` (used
 * by the list preview and as a graceful fallback wherever segments aren't read).
 * Mirrors the legacy "<p>Locutor A: …</p>" shape, with a timestamp marker.
 */
export function segmentosToHtml(segmentos: Segmento[], locutores?: Locutores): string {
  return segmentos
    .filter((s) => s.text.trim())
    .map((s) => {
      const name = escapeHtml(speakerLabel(s.speaker, locutores))
      const ts = escapeHtml(formatTimestamp(s.start))
      const body = escapeHtml(s.text.trim())
      return `<p><strong>${name}</strong> <span data-ts>[${ts}]</span> ${body}</p>`
    })
    .join("")
}

/**
 * Recover pseudo-segments from a legacy flat/HTML transcript so meetings
 * transcribed before timestamps existed are still editable. Lines shaped like
 * "Locutor A: text" keep their speaker; everything else falls to one speaker.
 * No timing is available, so start/end stay 0.
 */
export function htmlToSegmentos(html: string): Segmento[] {
  if (!html || !html.trim()) return []
  // Split on paragraph/break boundaries, then strip remaining tags per line.
  const blocks = html
    .replace(/<\s*br\s*\/?>/gi, "\n")
    .split(/<\/p>|<p[^>]*>|\n{2,}/i)
    .map((b) => stripTags(b).trim())
    .filter(Boolean)
  const out: Segmento[] = []
  for (const block of blocks) {
    const m = block.match(/^Locutor\s+([^:]{1,40}?):\s*([\s\S]*)$/)
    if (m) {
      out.push({ speaker: m[1].trim(), start: 0, end: 0, text: m[2].trim() })
    } else {
      out.push({ speaker: "A", start: 0, end: 0, text: block })
    }
  }
  return out.filter((s) => s.text.trim())
}

function stripTags(s: string): string {
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}
