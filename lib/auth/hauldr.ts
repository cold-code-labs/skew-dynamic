import { cookies } from "next/headers"

import {
  HAULDR_DEFAULT_ROLE,
  HAULDR_GOTRUE_URL,
  HAULDR_JWT_SECRET,
} from "@/config/env"
import { logError } from "@/lib/log"

import { verifyGoTrueToken, type GoTrueClaims } from "./jwt"
import type { SessionUser } from "./types"

// Hauldr auth adapter (AUTH_MODE=hauldr). Signs in email/password against the
// project's GoTrue and keeps the access + refresh tokens in httpOnly cookies.
// The access token is an HS256 JWT verified LOCALLY (lib/auth/jwt.ts) against the
// project's GoTrue secret — no round-trip per request — and forwarded to
// PostgREST so the data-API enforces per-user RLS from its claims. The
// middleware rotates the pair via the refresh token, so a session stays alive
// without a hard re-login (see middleware.ts).

export const HAULDR_SESSION_COOKIE = "hauldr_session"
export const HAULDR_REFRESH_COOKIE = "hauldr_refresh"

// Cookie lifetime in the browser (the inactivity window). The access token
// itself is short-lived; the middleware silently rotates it on each visit.
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30 // 30 days

/** Serialize one httpOnly session cookie as a Set-Cookie header value. */
export function serializeSessionCookie(name: string, value: string): string {
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : ""
  return `${name}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${COOKIE_MAX_AGE}${secure}`
}

/** A Set-Cookie that immediately expires a session cookie. */
function expireCookie(name: string): string {
  return `${name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`
}

type TokenResponse = {
  access_token?: string
  refresh_token?: string
}

/**
 * Authenticate with email/password against GoTrue. Returns the `Set-Cookie`
 * strings (access + refresh) to attach to the response on success, or null on
 * bad credentials / misconfiguration.
 */
export async function signInWithPassword(
  email: string,
  password: string,
): Promise<string[] | null> {
  if (!HAULDR_GOTRUE_URL) {
    logError("hauldr", "signInWithPassword: HAULDR_GOTRUE_URL is not set")
    return null
  }
  try {
    const res = await fetch(`${HAULDR_GOTRUE_URL}/token?grant_type=password`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    })
    if (!res.ok) return null
    const data = (await res.json()) as TokenResponse
    if (!data.access_token || !data.refresh_token) return null
    return [
      serializeSessionCookie(HAULDR_SESSION_COOKIE, data.access_token),
      serializeSessionCookie(HAULDR_REFRESH_COOKIE, data.refresh_token),
    ]
  } catch (e) {
    logError("hauldr", "signInWithPassword failed", e)
    return null
  }
}

/** Set-Cookie strings that clear the session (used by sign-out). */
export function signOutCookies(): string[] {
  return [expireCookie(HAULDR_SESSION_COOKIE), expireCookie(HAULDR_REFRESH_COOKIE)]
}

/** Resolve an app role from GoTrue custom claims, else the configured default. */
function resolveRole(claims: GoTrueClaims): string {
  const meta = { ...(claims.app_metadata ?? {}), ...(claims.user_metadata ?? {}) }
  const fromMeta = meta.papel ?? meta.role
  return typeof fromMeta === "string" && fromMeta ? fromMeta : HAULDR_DEFAULT_ROLE
}

/** Resolve the current Hauldr user from the verified access token, or null. */
export async function getHauldrSession(): Promise<SessionUser | null> {
  const token = (await cookies()).get(HAULDR_SESSION_COOKIE)?.value
  const claims = await verifyGoTrueToken(token, HAULDR_JWT_SECRET)
  if (!claims) return null

  const meta = { ...(claims.app_metadata ?? {}), ...(claims.user_metadata ?? {}) }
  const name =
    (typeof meta.name === "string" && meta.name) ||
    claims.email?.split("@")[0] ||
    claims.email ||
    "Usuário"

  return {
    id: claims.sub,
    name,
    email: claims.email ?? "",
    role: resolveRole(claims),
  }
}

/**
 * The signed-in user's GoTrue access token, forwarded by the data client to
 * PostgREST for per-user RLS. Returns undefined when the token is missing,
 * tampered, or expired — never a token PostgREST would reject anyway.
 */
export async function getHauldrAccessToken(): Promise<string | undefined> {
  const token = (await cookies()).get(HAULDR_SESSION_COOKIE)?.value
  if (!token) return undefined
  const claims = await verifyGoTrueToken(token, HAULDR_JWT_SECRET)
  return claims ? token : undefined
}
