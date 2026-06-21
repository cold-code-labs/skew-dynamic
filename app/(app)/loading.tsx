import { Skeleton } from "@/components/ui/skeleton"

// Instant navigation feedback for every (app) route that lacks its own
// loading.tsx. Without a loading boundary the App Router keeps the previous page
// on screen while the next route's dynamic RSC streams in (the shell reads the
// auth cookie, so these routes can't be prefetched) — so a sidebar click feels
// "frozen" until the server responds. This skeleton paints the instant a link is
// clicked, mirroring the PageShell layout so navigation feels immediate.
export default function AppLoading() {
  return (
    <main className="flex flex-1 flex-col gap-6 p-4 md:p-6">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-7 w-48" />
        <Skeleton className="h-4 w-72" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-xl" />
        ))}
      </div>
      <div className="flex flex-col gap-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    </main>
  )
}
