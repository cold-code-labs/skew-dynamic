import { redirect } from "next/navigation"
import { type NextRequest } from "next/server"

import { AUTH_MODE } from "@/config/env"
import { startStubSession } from "@/lib/auth/stub"

export const dynamic = "force-dynamic"

// 303 redirect with a RELATIVE Location. The browser resolves it against the
// public address bar (e.g. snowfall.coldcodelabs.com) — using request.url here
// would bake in the container's internal origin (0.0.0.0:3000) behind Traefik.
function seeOther(location: string, setCookie?: string | string[]): Response {
  const headers = new Headers({ Location: location })
  for (const c of [setCookie ?? []].flat()) headers.append("Set-Cookie", c)
  return new Response(null, { status: 303, headers })
}

// Starts a login.
//   logto      → signIn() redirects to Logto's hosted sign-in (returns to /callback)
//   stub       → set the demo cookie and land on /dashboard
//   pocketbase → credentials form posts here (see POST); GET just bounces to login
export async function GET() {
  if (AUTH_MODE === "logto") {
    const { signIn } = await import("@logto/next/server-actions")
    const { logtoConfig } = await import("@/lib/auth/logto")
    await signIn(logtoConfig)
  } else if (AUTH_MODE === "stub") {
    await startStubSession()
  } else {
    redirect("/login")
  }
  redirect("/dashboard")
}

// Email/password sign-in for AUTH_MODE=pocketbase | hauldr. The form posts here.
export async function POST(request: NextRequest) {
  if (AUTH_MODE !== "pocketbase" && AUTH_MODE !== "hauldr") {
    return seeOther("/login")
  }

  const form = await request.formData()
  const email = String(form.get("email") ?? "")
  const password = String(form.get("password") ?? "")

  const { signInWithPassword } =
    AUTH_MODE === "hauldr"
      ? await import("@/lib/auth/hauldr")
      : await import("@/lib/auth/pocketbase")

  const setCookie = await signInWithPassword(email, password)
  if (!setCookie) {
    return seeOther("/login?error=1")
  }

  return seeOther("/dashboard", setCookie)
}
