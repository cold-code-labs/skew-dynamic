"use server"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { logError } from "@/lib/log"
import { getCurrentTenantId } from "@/lib/tenant"

import type { ActionResult } from "@/lib/resources/types"

const DEMO: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase para enviar arquivos.",
}

export async function uploadDocumento(form: FormData): Promise<ActionResult> {
  const denied = await requireCapability("files.upload")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { uploadDocumentoRest } = await import("./rest")
    return uploadDocumentoRest(form)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  const file = form.get("file")
  if (!(file instanceof File) || file.size === 0) {
    return { ok: false, error: "Selecione um arquivo." }
  }
  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    const data = new FormData()
    data.append("name", String(form.get("name") || file.name))
    data.append("category", String(form.get("category") || "Geral"))
    data.append("size", String(file.size))
    data.append("organization", await getCurrentTenantId())
    data.append("file", file)
    await pb.collection("documentos").create(data)
    revalidatePath("/arquivos")
    return { ok: true }
  } catch (e) {
    logError("arquivos", "uploadDocumento", e)
    return { ok: false, error: e instanceof Error ? e.message : "Falha no upload." }
  }
}

export async function deleteDocumento(id: string): Promise<ActionResult> {
  const denied = await requireCapability("files.upload")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE === "postgrest") {
    const { deleteDocumentoRest } = await import("./rest")
    return deleteDocumentoRest(id)
  }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const { pbServer } = await import("@/lib/auth/pocketbase")
    const pb = await pbServer()
    await pb.collection("documentos").delete(id)
    revalidatePath("/arquivos")
    return { ok: true }
  } catch (e) {
    logError("arquivos", "deleteDocumento", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}
