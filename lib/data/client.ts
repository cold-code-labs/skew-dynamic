import { DATA_API_TOKEN, DATA_API_URL } from "@/config/env"
import { getAccessToken } from "@/lib/auth/session"
import { logError } from "@/lib/log"

// Thin PostgREST client. Server-side only — forwards a bearer token (service
// token by default, or the user's access token) so the data-API can enforce
// RLS from the JWT claims. No supabase-js: just typed fetch against PostgREST.
//
//   const rows = await pgrest<Cliente[]>("/clientes?select=*&order=nome.asc")
export async function pgrest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  if (!DATA_API_URL) {
    throw new Error("DATA_API_URL is not set (DATA_MODE=postgrest requires it)")
  }

  const token = DATA_API_TOKEN || (await getAccessToken())

  const res = await fetch(`${DATA_API_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
    cache: "no-store",
  })

  if (!res.ok) {
    const body = await res.text()
    logError("postgrest", `${init.method ?? "GET"} ${path}`, undefined, {
      status: res.status,
      body: body.slice(0, 300),
    })
    throw new Error(`PostgREST ${res.status} on ${path}: ${body}`)
  }

  return (await res.json()) as T
}
