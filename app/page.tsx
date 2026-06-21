"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

// Root returns a 200 (not a 307) so readiness probes that hit "/" succeed
// immediately — the Claude Code Preview / CI probe treats a 307 as "not ready".
// A real browser is forwarded into the app right away; the proxy then bounces
// unauthenticated users to /login (the public demo-login screen).
export default function Home() {
  const router = useRouter()
  useEffect(() => {
    router.replace("/dashboard")
  }, [router])

  return (
    <main className="flex min-h-svh items-center justify-center">
      <p className="text-sm text-muted-foreground">Carregando…</p>
    </main>
  )
}
