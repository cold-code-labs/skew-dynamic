import { FUNCTIONS_URL } from "@/config/env"
import { getAccessToken } from "@/lib/auth/session"

// Thin caller for edge-runtime (Deno) functions. Optional — only used when
// FUNCTIONS_URL is set. Server-side only.
//
//   const result = await invokeFunction("create-client", { name: "Acme" })
export async function invokeFunction<T = unknown>(
  name: string,
  body?: unknown,
  init: RequestInit = {},
): Promise<T> {
  if (!FUNCTIONS_URL) {
    throw new Error("FUNCTIONS_URL is not set")
  }

  const token = await getAccessToken()

  const res = await fetch(`${FUNCTIONS_URL}/${name}`, {
    method: "POST",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  })

  if (!res.ok) {
    throw new Error(`Function ${name} failed (${res.status}): ${await res.text()}`)
  }

  return (await res.json()) as T
}
