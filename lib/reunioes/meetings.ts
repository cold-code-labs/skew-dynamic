import { DATA_MODE } from "@/config/env"
import { logWarn } from "@/lib/log"
import { andFilter, tenantFilter } from "@/lib/tenant"

import {
  normalizeStatus,
  parseLocutores,
  parseSegmentos,
  type Reuniao,
} from "./types"

// Server-side reader for the Reuniões Gravadas module. PocketBase stores the
// recorded audio natively (protected file field); we keep `titulo`, `duracao`,
// `status` and the `transcricao` next to it so the UI renders without reading
// the audio bytes. Mirrors lib/storage/documents.ts (signed file URLs via a
// per-request token). Client-safe types/helpers live in ./types.

const STUB: Reuniao[] = [
  {
    id: "demo-1",
    titulo: "Kickoff Acme — Onboarding",
    status: "transcrita",
    duracao: 372,
    idioma: "pt",
    transcricao:
      "<p><strong>Maria</strong> <span data-ts>[0:03]</span> Bom dia a todos, vamos começar o onboarding da Acme.</p>" +
      "<p><strong>João</strong> <span data-ts>[0:11]</span> Perfeito. A primeira entrega é o portal de acesso, certo?</p>" +
      "<p><strong>Maria</strong> <span data-ts>[0:18]</span> Isso, até o fim do mês. Eu cuido do treinamento da equipe.</p>",
    segmentos: [
      { speaker: "A", start: 3, end: 10, text: "Bom dia a todos, vamos começar o onboarding da Acme." },
      { speaker: "B", start: 11, end: 17, text: "Perfeito. A primeira entrega é o portal de acesso, certo?" },
      { speaker: "A", start: 18, end: 26, text: "Isso, até o fim do mês. Eu cuido do treinamento da equipe." },
    ],
    locutores: { A: "Maria", B: "João" },
    created: "2026-06-09",
  },
  {
    id: "demo-2",
    titulo: "Alinhamento semanal — Produto",
    status: "transcrita",
    duracao: 845,
    idioma: "pt",
    transcricao:
      "<p>Revisão das tarefas da sprint. O módulo de relatórios foi priorizado " +
      "após o feedback da Globex.</p>",
    created: "2026-06-08",
  },
  {
    id: "demo-3",
    titulo: "Call comercial — Umbrella",
    status: "gravada",
    duracao: 198,
    idioma: "pt",
    transcricao: "",
    created: "2026-06-07",
  },
]

export async function listReunioes(): Promise<Reuniao[]> {
  if (DATA_MODE === "postgrest") {
    const { listReunioesRest } = await import("./rest")
    return listReunioesRest()
  }
  if (DATA_MODE !== "pocketbase") return STUB

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("reunioes").getFullList({
    sort: "-created",
    filter: andFilter(await tenantFilter()),
  })
  // The audio field is protected, so its bytes need a short-lived access token.
  let token = ""
  try {
    token = await pb.files.getToken()
  } catch (e) {
    // No token (e.g. unauthenticated) → audio simply won't resolve.
    logWarn("reunioes", "listReunioes: file token unavailable", e)
  }
  return recs.map((r) => mapRecord(r, pb, token))
}

export async function getReuniao(id: string): Promise<Reuniao | null> {
  if (DATA_MODE === "postgrest") {
    const { getReuniaoRest } = await import("./rest")
    return getReuniaoRest(id)
  }
  if (DATA_MODE !== "pocketbase") return STUB.find((r) => r.id === id) ?? null

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  try {
    const r = await pb.collection("reunioes").getOne(id)
    let token = ""
    try {
      token = await pb.files.getToken()
    } catch (e) {
      logWarn("reunioes", "getReuniao: file token unavailable", e, { id })
    }
    return mapRecord(r, pb, token)
  } catch (e) {
    logWarn("reunioes", "getReuniao: record not found", e, { id })
    return null
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapRecord(r: any, pb: any, token: string): Reuniao {
  return {
    id: r.id,
    titulo: (r.titulo as string) ?? "Reunião",
    status: normalizeStatus(r.status),
    duracao: (r.duracao as number) ?? 0,
    mime: (r.mime as string) || undefined,
    idioma: (r.idioma as string) || undefined,
    transcricao: (r.transcricao as string) || "",
    segmentos: parseSegmentos(r.segmentos),
    locutores: parseLocutores(r.locutores),
    created: r.created as string,
    audioUrl: r.audio ? pb.files.getURL(r, r.audio as string, { token }) : undefined,
  }
}
