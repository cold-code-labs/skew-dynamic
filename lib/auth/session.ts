import { cache } from "react"

import { AUTH_MODE } from "@/config/env"

import { getStubSession } from "./stub"
import type { SessionUser } from "./types"

// Standard OIDC claims we read from Logto. Kept loose so the code compiles
// regardless of which scopes are configured on the Logto application.
type LooseClaims = {
  sub: string
  name?: string | null
  username?: string | null
  email?: string | null
  picture?: string | null
  roles?: string[] | null
}

/**
 * Resolve the current request's user, server-side, from whichever auth backend
 * is active. Returns null when unauthenticated. This is the single seam the
 * rest of the app uses — pages/layouts never touch Logto or cookies directly.
 *
 * Wrapped in React.cache() so the result is memoized per request: the app shell
 * layout, route guards, and pages all call getSession() on the same navigation,
 * and in pocketbase mode each call would otherwise fire a fresh authRefresh()
 * round-trip to PocketBase. cache() collapses them to a single round-trip.
 */
export const getSession = cache(async function getSession(): Promise<SessionUser | null> {
  if (AUTH_MODE === "logto") {
    const { getLogtoContext } = await import("@logto/next/server-actions")
    const { logtoConfig } = await import("./logto")
    const { isAuthenticated, claims } = await getLogtoContext(logtoConfig)
    if (!isAuthenticated || !claims) return null

    const c = claims as unknown as LooseClaims
    const roles = Array.isArray(c.roles)
      ? c.roles.filter((r): r is string => typeof r === "string")
      : []

    return {
      id: c.sub,
      name: c.name ?? c.username ?? c.email ?? "Usuário",
      email: c.email ?? "",
      role: roles[0] ?? "user",
      avatar: c.picture ?? undefined,
    }
  }

  if (AUTH_MODE === "pocketbase") {
    const { getPocketbaseSession } = await import("./pocketbase")
    return getPocketbaseSession()
  }

  if (AUTH_MODE === "hauldr") {
    const { getHauldrSession } = await import("./hauldr")
    return getHauldrSession()
  }

  return getStubSession()
})

/**
 * Bearer token for the data-API / functions, forwarded by lib/data/client.ts.
 * A server-side DATA_API_TOKEN (if set) takes precedence there; this is the
 * per-user path: in hauldr mode it returns the signed-in user's GoTrue access
 * token so PostgREST enforces RLS from the JWT claims. Other modes have no
 * per-user token (the service token, or stub data, covers them).
 */
export async function getAccessToken(): Promise<string | undefined> {
  if (AUTH_MODE === "hauldr") {
    const { getHauldrAccessToken } = await import("./hauldr")
    return getHauldrAccessToken()
  }
  return undefined
}
