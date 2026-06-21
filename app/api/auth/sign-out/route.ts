import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AUTH_MODE } from "@/config/env"
import { endStubSession } from "@/lib/auth/stub"

export const dynamic = "force-dynamic"

// Ends the session.
//   logto      → hands off to Logto's end-session endpoint (redirects back)
//   pocketbase → clear the pb_auth cookie
//   stub       → clear the demo cookie
export async function GET() {
  if (AUTH_MODE === "logto") {
    const { signOut } = await import("@logto/next/server-actions")
    const { logtoConfig } = await import("@/lib/auth/logto")
    await signOut(logtoConfig)
  } else if (AUTH_MODE === "pocketbase") {
    const { PB_COOKIE_NAME } = await import("@/lib/auth/pocketbase")
    const store = await cookies()
    store.delete(PB_COOKIE_NAME)
  } else if (AUTH_MODE === "hauldr") {
    const { HAULDR_SESSION_COOKIE, HAULDR_REFRESH_COOKIE } = await import(
      "@/lib/auth/hauldr"
    )
    const store = await cookies()
    store.delete(HAULDR_SESSION_COOKIE)
    store.delete(HAULDR_REFRESH_COOKIE)
  } else {
    await endStubSession()
  }
  redirect("/login")
}
