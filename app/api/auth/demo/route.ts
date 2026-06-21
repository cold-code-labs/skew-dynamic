import {
  AUTH_MODE,
  DEMO_LOGIN,
  DEMO_LOGIN_EMAIL,
  DEMO_LOGIN_PASSWORD,
} from "@/config/env"

export const dynamic = "force-dynamic"

// 303 redirect with a relative Location (resolves against the public host —
// see app/api/auth/sign-in/route.ts for why request.url would be wrong).
function seeOther(location: string, setCookie?: string): Response {
  const headers = new Headers({ Location: location })
  if (setCookie) headers.append("Set-Cookie", setCookie)
  return new Response(null, { status: 303, headers })
}

// One-click demo login. Gated by DEMO_LOGIN=true (+ AUTH_MODE=pocketbase) —
// DEV/DEMO ONLY. Signs in as the preconfigured demo user, bypassing the form.
export async function GET() {
  if (AUTH_MODE !== "pocketbase" || !DEMO_LOGIN) {
    return seeOther("/login")
  }
  const { signInWithPassword } = await import("@/lib/auth/pocketbase")
  const setCookie = await signInWithPassword(DEMO_LOGIN_EMAIL, DEMO_LOGIN_PASSWORD)
  if (!setCookie) return seeOther("/login?error=1")
  return seeOther("/dashboard", setCookie)
}
