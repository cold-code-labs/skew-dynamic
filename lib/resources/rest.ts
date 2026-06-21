import { revalidatePath } from "next/cache"

import { pgrest } from "@/lib/data/client"
import { logError } from "@/lib/log"

import { collectionOf, type ActionResult, type ResourceDef } from "./types"

// PostgREST path for the generic resource engine (DATA_MODE=postgrest, Hauldr
// tier). One table per resource (see migration 0003), owner-keyed RLS. The
// payload is built from the resource's declared fields by the caller; `owner`
// stays server-side (column default = JWT sub).

function messageOf(e: unknown): string {
  return e instanceof Error ? e.message : "Falha ao gravar."
}

export async function createRecordRest(
  def: ResourceDef,
  payload: Record<string, unknown>,
): Promise<ActionResult> {
  try {
    await pgrest(`/${collectionOf(def)}`, {
      method: "POST",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify(payload),
    })
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "createRecordRest", e, { key: def.key })
    return { ok: false, error: messageOf(e) }
  }
}

export async function updateRecordRest(
  def: ResourceDef,
  id: string,
  payload: Record<string, unknown>,
): Promise<ActionResult> {
  try {
    await pgrest(`/${collectionOf(def)}?id=eq.${id}`, {
      method: "PATCH",
      headers: { Prefer: "return=minimal" },
      body: JSON.stringify({ ...payload, updated_at: new Date().toISOString() }),
    })
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "updateRecordRest", e, { key: def.key, id })
    return { ok: false, error: messageOf(e) }
  }
}

export async function deleteRecordRest(
  def: ResourceDef,
  id: string,
): Promise<ActionResult> {
  try {
    await pgrest(`/${collectionOf(def)}?id=eq.${id}`, {
      method: "DELETE",
      headers: { Prefer: "return=minimal" },
    })
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "deleteRecordRest", e, { key: def.key, id })
    return { ok: false, error: messageOf(e) }
  }
}
