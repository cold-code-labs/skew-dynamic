import { redirect } from "next/navigation"
import type { NextRequest } from "next/server"

import { AUTH_MODE } from "@/config/env"

export const dynamic = "force-dynamic"

// Logto OIDC redirect target (AUTH_MODE=logto). Register `${baseUrl}/callback`
// as the redirect URI in the Logto console. In stub mode this route is never
// used, so the @logto/next import stays dynamic (matches sign-in/sign-out).
export async function GET(request: NextRequest) {
  if (AUTH_MODE !== "logto") {
    return new Response("Not found", { status: 404 })
  }
  const { handleSignIn } = await import("@logto/next/server-actions")
  const { logtoConfig } = await import("@/lib/auth/logto")
  await handleSignIn(logtoConfig, request.nextUrl.searchParams)
  redirect("/dashboard")
}
