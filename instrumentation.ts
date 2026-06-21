// Next.js instrumentation hook — runs once per server process at startup.
// We use it to print the boot config summary (see lib/startup.ts) so a freshly
// deployed instance's logs immediately show which features are wired vs in demo
// mode. Guarded to the Node.js runtime: the Edge runtime has no place for it and
// config/env reads process.env which isn't available there at register time.
export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME !== "nodejs") return
  const { logStartupSummary } = await import("@/lib/startup")
  logStartupSummary()
}
