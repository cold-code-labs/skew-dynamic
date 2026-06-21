// Edge-safe HS256 verification (Web Crypto only — no node:crypto, no
// next/headers) so the SAME verify runs in the middleware (edge runtime) and in
// server components. A Hauldr GoTrue access token is an HS256 JWT; this checks
// its signature against the project secret and its expiry, returning the claims.

export type GoTrueClaims = {
  sub: string
  email?: string
  /** PostgREST switch-role claim — always "authenticated" for a signed-in user. */
  role?: string
  exp?: number
  /** GoTrue custom claim buckets where an app role may live. */
  user_metadata?: Record<string, unknown>
  app_metadata?: Record<string, unknown>
}

function base64UrlToBytes(s: string): Uint8Array {
  const norm = s.replace(/-/g, "+").replace(/_/g, "/")
  const pad = norm.length % 4 === 0 ? 0 : 4 - (norm.length % 4)
  const bin = atob(norm + "=".repeat(pad))
  const out = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i)
  return out
}

async function verifyHs256(token: string, secret: string): Promise<boolean> {
  const [h, p, sig] = token.split(".")
  if (!h || !p || !sig) return false
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  )
  return crypto.subtle.verify(
    "HMAC",
    key,
    base64UrlToBytes(sig),
    new TextEncoder().encode(`${h}.${p}`),
  )
}

/**
 * Verify a GoTrue token's signature + expiry against the project secret. Returns
 * the claims on success, or null on any tampering / expiry / malformed input.
 * Fails closed: a token with no valid `exp` is rejected.
 */
export async function verifyGoTrueToken(
  token: string | undefined,
  secret: string,
): Promise<GoTrueClaims | null> {
  if (!token || !secret) return null
  const parts = token.split(".")
  if (parts.length !== 3) return null
  let ok = false
  try {
    ok = await verifyHs256(token, secret)
  } catch {
    return null
  }
  if (!ok) return null
  try {
    const claims = JSON.parse(
      new TextDecoder().decode(base64UrlToBytes(parts[1])),
    ) as GoTrueClaims
    if (typeof claims.exp !== "number" || !Number.isFinite(claims.exp)) return null
    if (claims.exp * 1000 < Date.now()) return null
    return claims
  } catch {
    return null
  }
}

/** Exchange a GoTrue refresh token for a fresh access+refresh pair (rotates). */
export async function refreshGoTrue(
  refreshToken: string | undefined,
  gotrueUrl: string,
): Promise<{ accessToken: string; refreshToken: string } | null> {
  if (!refreshToken || !gotrueUrl) return null
  try {
    const res = await fetch(`${gotrueUrl}/token?grant_type=refresh_token`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    })
    if (!res.ok) return null
    const data = (await res.json()) as {
      access_token?: string
      refresh_token?: string
    }
    if (!data.access_token || !data.refresh_token) return null
    return { accessToken: data.access_token, refreshToken: data.refresh_token }
  } catch {
    return null
  }
}
