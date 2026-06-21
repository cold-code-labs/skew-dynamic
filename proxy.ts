import { NextResponse, type NextRequest } from "next/server"

import { refreshGoTrue, verifyGoTrueToken } from "@/lib/auth/jwt"

// Next.js "proxy" (formerly middleware). Keep these cookie names in sync with
// the auth adapters — can't import them here: this runs on the edge runtime and
// must stay dependency-light (jwt.ts is the one exception: it's Web Crypto +
// fetch only, edge-safe by design).
const STUB_COOKIE = "template_session"
const PB_COOKIE = "pb_auth"
const HAULDR_SESSION_COOKIE = "hauldr_session"
const HAULDR_REFRESH_COOKIE = "hauldr_refresh"

function resolveAuthMode(): "logto" | "pocketbase" | "hauldr" | "stub" {
  const env = process.env.AUTH_MODE
  if (env === "logto") return "logto"
  if (env === "pocketbase") return "pocketbase"
  if (env === "hauldr") return "hauldr"
  return "stub"
}

// GoTrue base URL, resolved by APP_ENV exactly as config/env.ts does (internal
// in prod / public *_REMOTE in dev) — inlined to keep the edge bundle light.
function gotrueUrl(): string {
  const appEnv = (process.env.APP_ENV ?? "").trim().toLowerCase() === "prd" ? "prd" : "dev"
  const internal = process.env.HAULDR_GOTRUE_URL ?? ""
  const remote = process.env.HAULDR_GOTRUE_URL_REMOTE ?? ""
  return appEnv === "dev" && remote ? remote : internal
}

// AUTH_MODE=hauldr — verify the GoTrue access token; on expiry rotate it via the
// refresh token (silent, no re-login); bounce to /login only when neither works.
async function proxyHauldr(request: NextRequest): Promise<NextResponse> {
  const secret = process.env.HAULDR_JWT_SECRET ?? ""
  const accessToken = request.cookies.get(HAULDR_SESSION_COOKIE)?.value
  if (secret && (await verifyGoTrueToken(accessToken, secret))) {
    return NextResponse.next()
  }

  const refreshToken = request.cookies.get(HAULDR_REFRESH_COOKIE)?.value
  const rotated = await refreshGoTrue(refreshToken, gotrueUrl())
  if (rotated && (await verifyGoTrueToken(rotated.accessToken, secret))) {
    request.cookies.set(HAULDR_SESSION_COOKIE, rotated.accessToken)
    request.cookies.set(HAULDR_REFRESH_COOKIE, rotated.refreshToken)
    const response = NextResponse.next({ request })
    const opts = {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax" as const,
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    }
    response.cookies.set(HAULDR_SESSION_COOKIE, rotated.accessToken, opts)
    response.cookies.set(HAULDR_REFRESH_COOKIE, rotated.refreshToken, opts)
    return response
  }

  const url = request.nextUrl.clone()
  url.pathname = "/login"
  const response = NextResponse.redirect(url)
  response.cookies.delete(HAULDR_SESSION_COOKIE)
  response.cookies.delete(HAULDR_REFRESH_COOKIE)
  return response
}

export async function proxy(request: NextRequest): Promise<NextResponse> {
  // Cookie-presence gate so unauthenticated users get bounced to /login before
  // the page renders. For stub and pocketbase this is a cheap pre-check; the
  // authoritative check still lives in app/(app)/layout.tsx via getSession().
  // In logto mode the edge runtime can't resolve the session, so we pass through.
  // In hauldr mode the token IS verifiable on the edge, so we verify + rotate.
  const authMode = resolveAuthMode()

  if (authMode === "hauldr") return proxyHauldr(request)

  const cookieName =
    authMode === "pocketbase" ? PB_COOKIE : authMode === "stub" ? STUB_COOKIE : null

  if (cookieName && !request.cookies.get(cookieName)) {
    const url = request.nextUrl.clone()
    url.pathname = "/login"
    return NextResponse.redirect(url)
  }
  return NextResponse.next()
}

// Only run on the authenticated app routes.
export const config = {
  matcher: [
    "/dashboard/:path*",
    "/calendario/:path*",
    "/notificacoes/:path*",
    "/busca/:path*",
    "/clientes/:path*",
    "/financeiro/:path*",
    "/projetos/:path*",
    "/chamados/:path*",
    "/tarefas/:path*",
    "/arquivos/:path*",
    "/conta/:path*",
    "/acessos/:path*",
  ],
}
