import { cookies } from "next/headers"
import { NextResponse } from "next/server"

import { AUTH_MODE, HAULDR_GOTRUE_URL, HAULDR_JWT_SECRET } from "@/config/env"
import {
  HAULDR_REFRESH_COOKIE,
  HAULDR_SESSION_COOKIE,
  serializeSessionCookie,
} from "@/lib/auth/hauldr"
import { refreshGoTrue, verifyGoTrueToken } from "@/lib/auth/jwt"

export const dynamic = "force-dynamic"

// Hand the browser realtime client a current GoTrue access token (lib/realtime's
// refresh loop calls this ~1 min before expiry). Rotates proactively when the
// token is within 2 min of expiring — so the client always gets a token with real
// runway, keeping a long-lived private channel authorized. Hauldr tier only.
export async function GET() {
  if (AUTH_MODE !== "hauldr") {
    return NextResponse.json({ error: "realtime auth is hauldr-only" }, { status: 404 })
  }

  const jar = await cookies()
  const access = jar.get(HAULDR_SESSION_COOKIE)?.value
  const claims = access ? await verifyGoTrueToken(access, HAULDR_JWT_SECRET) : null
  const now = Math.floor(Date.now() / 1000)

  // Still has comfortable runway — hand it back as-is.
  if (access && claims && (claims.exp ?? 0) - now > 120) {
    return NextResponse.json({ accessToken: access })
  }

  // Expired or close to it — rotate via the refresh token and set the new cookies.
  const refresh = jar.get(HAULDR_REFRESH_COOKIE)?.value
  const rotated = await refreshGoTrue(refresh, HAULDR_GOTRUE_URL)
  if (rotated && (await verifyGoTrueToken(rotated.accessToken, HAULDR_JWT_SECRET))) {
    const res = NextResponse.json({ accessToken: rotated.accessToken })
    res.headers.append("Set-Cookie", serializeSessionCookie(HAULDR_SESSION_COOKIE, rotated.accessToken))
    res.headers.append("Set-Cookie", serializeSessionCookie(HAULDR_REFRESH_COOKIE, rotated.refreshToken))
    return res
  }

  return NextResponse.json({ error: "unauthenticated" }, { status: 401 })
}
