import Link from "next/link"
import { Compass } from "lucide-react"

import { Button } from "@/components/ui/button"
import { BRAND } from "@/config/brand"

// Branded 404. Rendered for any unmatched route (outside the app shell).
export default function NotFound() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-5 p-6 text-center">
      <div className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <Compass className="size-6" />
      </div>
      <div className="flex flex-col gap-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Página não encontrada</h1>
        <p className="max-w-sm text-sm text-muted-foreground text-pretty">
          O endereço que você tentou abrir não existe ou foi movido em {BRAND.name}.
        </p>
      </div>
      <Button nativeButton={false} render={<Link href="/dashboard">Voltar ao início</Link>} />
    </main>
  )
}
