"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { logError } from "@/lib/log"
import { withTenant } from "@/lib/tenant"
import { resourceByKey } from "@/config/resources"

import { collectionOf, type ActionResult, type ResourceDef } from "./types"

const DEMO_NOTICE: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase (DATA_MODE=pocketbase) para gravar.",
}

// Build a clean payload from the resource's declared fields, coercing numbers.
function payloadFromForm(def: ResourceDef, form: FormData) {
  const data: Record<string, unknown> = {}
  for (const f of def.fields ?? []) {
    const raw = form.get(f.field)
    if (raw === null) continue
    const value = String(raw)
    data[f.field] = f.type === "number" ? Number(value || 0) : value
  }
  return data
}

async function pbCollection(def: ResourceDef) {
  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  return pb.collection(collectionOf(def))
}

export async function createRecord(key: string, form: FormData): Promise<ActionResult> {
  const def = resourceByKey(key)
  if (!def) return { ok: false, error: "Recurso desconhecido." }
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO_NOTICE
  try {
    const col = await pbCollection(def)
    await col.create(await withTenant(payloadFromForm(def, form)))
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "createRecord", e, { key })
    return { ok: false, error: messageOf(e) }
  }
}

export async function updateRecord(
  key: string,
  id: string,
  form: FormData,
): Promise<ActionResult> {
  const def = resourceByKey(key)
  if (!def) return { ok: false, error: "Recurso desconhecido." }
  const denied = await requireCapability("data.write")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO_NOTICE
  try {
    const col = await pbCollection(def)
    await col.update(id, payloadFromForm(def, form))
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "updateRecord", e, { key, id })
    return { ok: false, error: messageOf(e) }
  }
}

export async function deleteRecord(key: string, id: string): Promise<ActionResult> {
  const def = resourceByKey(key)
  if (!def) return { ok: false, error: "Recurso desconhecido." }
  const denied = await requireCapability("data.delete")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO_NOTICE
  try {
    const col = await pbCollection(def)
    await col.delete(id)
    revalidatePath(`/${def.key}`)
    return { ok: true }
  } catch (e) {
    logError("recursos", "deleteRecord", e, { key, id })
    return { ok: false, error: messageOf(e) }
  }
}

function messageOf(e: unknown): string {
  return e instanceof Error ? e.message : "Falha ao gravar."
}
