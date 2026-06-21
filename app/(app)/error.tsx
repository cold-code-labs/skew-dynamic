"use client"

import { useEffect, useState } from "react"
import { RotateCw, TriangleAlert } from "lucide-react"

import { Button } from "@/components/ui/button"

// How long to wait before allowing another automatic recovery. Caps auto-retry
// to one attempt per transient burst so a genuinely broken page can't loop.
const AUTO_RECOVER_WINDOW_MS = 10_000
const RECOVER_KEY = "app-error-auto-recover"

// Error boundary for the app shell. Catches render/runtime errors and shows a
// branded fallback instead of a raw stack trace, with a retry. Must be a client
// component (Next requirement).
//
// Many of the errors that land here are *transient transport* errors, not real
// bugs: a server action or RSC refresh whose request was dropped or answered
// with a 5xx by the proxy/tunnel throws into this boundary even though the page
// is fine and the underlying write already succeeded. So we auto-recover once —
// re-render the segment (which re-fetches and almost always succeeds) before
// ever showing the scary fallback. A persistent error throws again within the
// window and falls through to the manual retry UI.
export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  // Decided during the first render so the fallback never flashes when we're
  // about to silently recover.
  const [recovering] = useState(() => {
    try {
      const last = Number(sessionStorage.getItem(RECOVER_KEY) || 0)
      return Date.now() - last > AUTO_RECOVER_WINDOW_MS
    } catch {
      return false
    }
  })

  useEffect(() => {
    // Surface to the server logs for debugging; the user sees the friendly UI.
    console.error(error)
    if (recovering) {
      try {
        sessionStorage.setItem(RECOVER_KEY, String(Date.now()))
      } catch {
        /* sessionStorage unavailable — fall back to the manual UI */
      }
      reset()
    }
  }, [error, reset, recovering])

  // While auto-recovering, render nothing (a blank frame) instead of the error
  // card so the recovery is invisible to the user.
  if (recovering) return null

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-5 p-6 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl bg-destructive/10 text-destructive">
        <TriangleAlert className="size-6" />
      </div>
      <div className="flex flex-col gap-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Algo deu errado</h1>
        <p className="max-w-sm text-sm text-muted-foreground text-pretty">
          Ocorreu um erro ao carregar esta página. Tente novamente.
        </p>
      </div>
      <Button onClick={reset}>
        <RotateCw data-icon="inline-start" />
        Tentar de novo
      </Button>
    </main>
  )
}
