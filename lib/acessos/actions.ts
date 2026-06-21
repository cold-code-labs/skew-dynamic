"use server"

import { randomBytes } from "crypto"

import { revalidatePath } from "next/cache"

import { DATA_MODE } from "@/config/env"
import { requireCapability } from "@/lib/auth/guard"
import { logError } from "@/lib/log"
import { withTenant } from "@/lib/tenant"

import type { ActionResult } from "@/lib/resources/types"

const DEMO: ActionResult = {
  ok: false,
  error: "Modo demonstração: conecte o PocketBase para gerir a equipe.",
}

function read(form: FormData) {
  return {
    nome: String(form.get("nome") || ""),
    email: String(form.get("email") || ""),
    papel: String(form.get("papel") || "Membro"),
    status: String(form.get("status") || "Convidado"),
  }
}

async function pb() {
  const { pbServer } = await import("@/lib/auth/pocketbase")
  return pbServer()
}

export async function inviteMember(form: FormData): Promise<ActionResult> {
  const denied = await requireCapability("members.manage")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO
  const data = read(form)
  try {
    const client = await pb()
    // Create a real auth user so the person can actually log in. Without SMTP we
    // can't email them, so we generate a temp password and surface it to the
    // admin to pass along (they change it on first login).
    const tempPassword = randomBytes(9).toString("base64url")
    await client.collection("users").create({
      email: data.email,
      password: tempPassword,
      passwordConfirm: tempPassword,
      name: data.nome,
      papel: data.papel,
      emailVisibility: true,
    })
    // Mirror into the display/members list.
    await client.collection("usuarios").create(await withTenant(data))
    revalidatePath("/acessos")
    return { ok: true, message: `Convite criado. Senha temporária: ${tempPassword}` }
  } catch (e) {
    // Log the email but NEVER the generated password.
    logError("acessos", "inviteMember", e, { email: data.email, papel: data.papel })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao convidar." }
  }
}

export async function updateMember(id: string, form: FormData): Promise<ActionResult> {
  const denied = await requireCapability("members.manage")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const client = await pb()
    await client.collection("usuarios").update(id, read(form))
    revalidatePath("/acessos")
    return { ok: true }
  } catch (e) {
    logError("acessos", "updateMember", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao salvar." }
  }
}

export async function removeMember(id: string): Promise<ActionResult> {
  const denied = await requireCapability("members.manage")
  if (denied) return { ok: false, error: denied }
  if (DATA_MODE !== "pocketbase") return DEMO
  try {
    const client = await pb()
    await client.collection("usuarios").delete(id)
    revalidatePath("/acessos")
    return { ok: true }
  } catch (e) {
    logError("acessos", "removeMember", e, { id })
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao remover." }
  }
}
