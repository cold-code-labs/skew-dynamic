"use client"

import { useTransition } from "react"
import { CreditCard, ExternalLink, Loader2, ShieldCheck } from "lucide-react"

import { PageShell } from "@/components/page-shell"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useToast } from "@/components/ui/toast"
import { abrirPortal } from "@/lib/assinaturas/actions"

export function AssinaturaView({ portalEnabled }: { portalEnabled: boolean }) {
  const { toast } = useToast()
  const [pending, startTransition] = useTransition()

  function gerenciar() {
    startTransition(async () => {
      const res = await abrirPortal()
      if (res.ok) {
        window.location.href = res.url
      } else {
        toast({
          title: "Não foi possível abrir o portal",
          description: res.error,
          variant: "destructive",
        })
      }
    })
  }

  return (
    <PageShell
      title="Assinatura"
      description="Gerencie sua assinatura mensal com a Cold Code Labs no portal seguro da Stripe."
    >
      <Card className="max-w-xl">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <CreditCard className="size-5" />
            </div>
            <div>
              <CardTitle>Portal de cobrança</CardTitle>
              <CardDescription>
                Pagamento, faturas e cancelamento — tudo no Stripe.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground">
            Sua assinatura é processada pela Stripe da Cold Code Labs. No portal
            você pode atualizar o cartão, baixar faturas e gerenciar o plano com
            segurança — a Cold Code Labs não armazena os dados do seu cartão.
          </p>

          <Button onClick={gerenciar} disabled={pending} className="w-fit">
            {pending ? (
              <Loader2 data-icon="inline-start" className="animate-spin" />
            ) : (
              <ExternalLink data-icon="inline-start" />
            )}
            Abrir portal de cobrança
          </Button>

          {!portalEnabled ? (
            <p className="text-xs text-muted-foreground">
              <span className="font-medium text-foreground">Modo demonstração.</span>{" "}
              Configure o Stripe (<code className="text-xs">STRIPE_PORTAL_URL</code>,
              ou <code className="text-xs">STRIPE_SECRET_KEY</code> +{" "}
              <code className="text-xs">STRIPE_CUSTOMER_ID</code>) para habilitar o
              portal nesta instância.
            </p>
          ) : (
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <ShieldCheck className="size-3.5" />
              Você será redirecionado para o ambiente seguro da Stripe.
            </p>
          )}
        </CardContent>
      </Card>
    </PageShell>
  )
}
