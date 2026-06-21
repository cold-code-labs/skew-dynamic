import { revalidatePath } from "next/cache"

import { pgrest } from "@/lib/data/client"
import { logError } from "@/lib/log"

import type { Member } from "./members"
import type { ActionResult } from "@/lib/resources/types"

// PostgREST path for the Acessos (team/members) module (DATA_MODE=postgrest,
// Hauldr tier). `usuarios` is the display/role list (migration 0004), owner-keyed
// RLS. Unlike the PocketBase path, inviting does NOT create a GoTrue login user
// (that needs the project's service_role, which the app token doesn't carry) —
// it only adds the member row. Real login provisioning is a GoTrue-admin step.

type MemberInput = { nome: string; email: string; papel: string; status: string }

export async function listMembersRest(): Promise<Member[]> {
  const rows = await pgrest<Record<string, unknown>[]>(
    "/usuarios?select=*&order=nome.asc",
  )
  return rows.map((r) => ({
    id: r.id as string,
    nome: (r.nome as string) ?? "",
    email: (r.email as string) ?? "",
    papel: (r.papel as string) || "Membro",
    status: (r.status as string) || "Ativo",
  }))
}

export async function inviteMemberRest(data: MemberInput): Promise<ActionResult> {
  try {
    await pgrest("/usuarios", {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify(data),
    })
    revalidatePath("/acessos")
    return { ok: true, message: "Membro adicionado." }
  } catch (e) {
    logError("acessos", "inviteMemberRest", e, { email: data.email, papel: data.papel })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao convidar." }
  }
}

export async function updateMemberRest(id: string, data: MemberInput): Promise<ActionResult> {
  try {
    await pgrest(`/usuarios?id=eq.${id}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ ...data, updated_at: new Date().toISOString() }),
    })
    revalidatePath("/acessos")
    return { ok: true }
  } catch (e) {
    logError("acessos", "updateMemberRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar." }
  }
}

export async function removeMemberRest(id: string): Promise<ActionResult> {
  try {
    await pgrest(`/usuarios?id=eq.${id}`, {
      method: "DELETE",
      headers: { Prefer: "return=minimal" },
    })
    revalidatePath("/acessos")
    return { ok: true }
  } catch (e) {
    logError("acessos", "removeMemberRest", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}
