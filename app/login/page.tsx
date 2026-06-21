import { ArrowRight } from "lucide-react"
import { redirect } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { APP_NAME } from "@/config/app"
import { BRAND, brandInitials } from "@/config/brand"
import { AUTH_MODE, DEMO_LOGIN } from "@/config/env"
import { getSession } from "@/lib/auth/session"

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>
}) {
  const user = await getSession()
  if (user) redirect("/dashboard")

  const { error } = await searchParams

  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-10 px-6 py-12">
      <div className="flex flex-col items-center gap-3 text-center">
        {BRAND.logo.image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={BRAND.logo.image}
            alt={APP_NAME}
            className="size-12 rounded-xl object-contain"
          />
        ) : (
          <div className="flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <span className="text-lg font-semibold">{brandInitials()}</span>
          </div>
        )}
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">{APP_NAME}</h1>
          <p className="text-sm text-muted-foreground">
            Base para prototipação rápida de MVPs.
          </p>
        </div>
      </div>

      <div className="flex w-full max-w-sm flex-col gap-4 rounded-xl border bg-card p-6">
        <div className="flex flex-col gap-1 text-center">
          <h2 className="text-lg font-medium">Bem-vindo de volta</h2>
          <p className="text-sm text-muted-foreground text-pretty">
            Entre para acessar a plataforma.
          </p>
        </div>

        {AUTH_MODE === "pocketbase" || AUTH_MODE === "hauldr" ? (
          <div className="flex flex-col gap-4">
            {DEMO_LOGIN ? (
              <>
                <form action="/api/auth/demo">
                  <Button size="lg" className="w-full" type="submit">
                    Entrar como demo (1 clique)
                    <ArrowRight data-icon="inline-end" />
                  </Button>
                </form>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="h-px flex-1 bg-border" />
                  ou entre com suas credenciais
                  <span className="h-px flex-1 bg-border" />
                </div>
              </>
            ) : null}
            <form method="post" action="/api/auth/sign-in" className="flex flex-col gap-3">
              <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="voce@empresa.com"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
              />
            </div>
            {error ? (
              <p className="text-center text-xs text-destructive">
                E-mail ou senha inválidos.
              </p>
            ) : null}
            <Button size="lg" className="w-full" type="submit">
              Entrar
              <ArrowRight data-icon="inline-end" />
            </Button>
            </form>
          </div>
        ) : (
          <>
            <form action="/api/auth/sign-in">
              <Button size="lg" className="w-full" type="submit">
                Entrar com um clique
                <ArrowRight data-icon="inline-end" />
              </Button>
            </form>
            {AUTH_MODE === "stub" ? (
              <p className="text-center text-xs text-muted-foreground text-balance">
                Modo demo (AUTH_MODE=stub). Defina AUTH_MODE=logto ou
                AUTH_MODE=pocketbase para autenticação real.
              </p>
            ) : null}
          </>
        )}
      </div>
    </main>
  )
}
