import { SidebarTrigger } from "@/components/ui/sidebar"

export function PageShell({
  title,
  description,
  actions,
  children,
}: {
  title: string
  description?: string
  actions?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <main className="flex min-w-0 flex-1 flex-col gap-6 p-4 md:p-6">
      <div className="flex items-start gap-3">
        <SidebarTrigger className="mt-1 md:hidden" />
        <div className="flex flex-1 flex-wrap items-start justify-between gap-3">
          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-semibold tracking-tight text-balance">
              {title}
            </h1>
            {description ? (
              <p className="text-sm text-muted-foreground text-pretty">
                {description}
              </p>
            ) : null}
          </div>
          {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
        </div>
      </div>
      {children}
    </main>
  )
}
