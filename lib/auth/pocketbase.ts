import { cookies } from "next/headers"
import PocketBase from "pocketbase"

import {
  PB_CF_ACCESS_CLIENT_ID,
  PB_CF_ACCESS_CLIENT_SECRET,
  POCKETBASE_URL,
} from "@/config/env"

import type { SessionUser } from "./types"

// PocketBase auth adapter (AUTH_MODE=pocketbase). PocketBase is the bundled
// backend in the "light" tier; auth is plain email/password against its `users`
// auth collection. The token is kept in the SDK's standard `pb_auth` httpOnly
// cookie — the rest of the app reads the user only through getSession().
export const PB_COOKIE_NAME = "pb_auth"

/**
 * The single PocketBase construction seam. Attaches the Cloudflare Access
 * service-token headers to every request when PB_CF_ACCESS_CLIENT_ID/SECRET are
 * set — needed when POCKETBASE_URL points at a PB behind Cloudflare Access (a
 * local checkout → live `data-<sub>` URL). With them unset (bundled localhost,
 * the normal case) this is a plain client with no added headers.
 */
function newPocketBase(): PocketBase {
  const pb = new PocketBase(POCKETBASE_URL)
  if (PB_CF_ACCESS_CLIENT_ID && PB_CF_ACCESS_CLIENT_SECRET) {
    pb.beforeSend = (url, options) => {
      options.headers = {
        ...options.headers,
        "CF-Access-Client-Id": PB_CF_ACCESS_CLIENT_ID,
        "CF-Access-Client-Secret": PB_CF_ACCESS_CLIENT_SECRET,
      }
      return { url, options }
    }
  }
  return pb
}

const isProd = process.env.NODE_ENV === "production"

const cookieOpts = {
  httpOnly: true,
  secure: isProd,
  sameSite: "lax" as const,
  path: "/",
}

/**
 * A per-request PocketBase client, authenticated from the incoming request's
 * `pb_auth` cookie. Always create a fresh instance per request (never share a
 * module-level client across requests) — auth state is request-scoped.
 */
export async function pbServer(): Promise<PocketBase> {
  const pb = newPocketBase()
  // Disable the SDK's auto-cancellation: it aborts concurrent same-path
  // requests on a shared client (e.g. the dashboard's parallel counts). This is
  // a fresh per-request server client, so there's nothing to dedupe.
  pb.autoCancellation(false)
  const store = await cookies()
  // The SDK extracts the `pb_auth` entry from the full cookie header.
  pb.authStore.loadFromCookie(store.toString())
  return pb
}

/** Resolve the current PocketBase user, or null when unauthenticated. */
export async function getPocketbaseSession(): Promise<SessionUser | null> {
  const pb = await pbServer()
  if (!pb.authStore.isValid) return null
  const cookieRec = pb.authStore.record
  if (!cookieRec) return null

  // SECURITY — never trust the cookie alone. `authStore.isValid` only decodes
  // the JWT `exp` locally; it does NOT verify the signature, and the whole
  // pb_auth cookie (token + the embedded user record) is attacker-controllable
  // (httpOnly stops JS, not the user's own devtools/curl). A forged cookie with
  // a future exp + an arbitrary record (e.g. papel:"Proprietário") would pass
  // isValid. So we MUST round-trip to PocketBase: authRefresh() makes the server
  // validate the token's signature and that the user still exists, returning the
  // live record. On any failure (forged / expired / revoked / deleted user) we
  // treat the request as unauthenticated — we do NOT fall back to the unverified
  // snapshot. This also keeps `papel` live (role changes apply without relogin).
  try {
    await pb.collection(cookieRec.collectionName || "users").authRefresh()
  } catch {
    return null
  }
  const rec = pb.authStore.record
  if (!rec) return null

  return {
    id: rec.id,
    name: (rec.name as string) || (rec.email as string) || "Usuário",
    email: (rec.email as string) ?? "",
    role: (rec.papel as string) || "Membro",
    avatar: rec.avatar
      ? pb.files.getURL(rec, rec.avatar as string)
      : undefined,
  }
}

/**
 * Authenticate with email/password. Returns a `Set-Cookie` string to attach to
 * the response on success, or null on bad credentials.
 */
export async function signInWithPassword(
  email: string,
  password: string,
): Promise<string | null> {
  const pb = newPocketBase()
  try {
    await pb.collection("users").authWithPassword(email, password)
  } catch {
    return null
  }
  return pb.authStore.exportToCookie(cookieOpts, PB_COOKIE_NAME)
}
