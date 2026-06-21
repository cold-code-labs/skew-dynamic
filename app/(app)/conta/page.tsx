import { Mail, Shield, LogOut } from "lucide-react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { PageShell } from "@/components/page-shell"
import { getSession } from "@/lib/auth/session"
import { redirect } from "next/navigation"

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

export default async function ContaPage() {
  const user = await getSession()
  if (!user) redirect("/login")

  return (
    <PageShell
      title="Minha conta"
      description="Seus dados de acesso e perfil nesta plataforma."
    >
      <Card className="max-w-2xl">
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="size-14 rounded-xl">
              <AvatarImage src={user.avatar} alt={user.name} />
              <AvatarFallback className="rounded-xl text-lg">
                {initials(user.name)}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col gap-1">
              <CardTitle className="text-xl">{user.name}</CardTitle>
              <CardDescription>{user.email}</CardDescription>
            </div>
            <Badge variant="secondary" className="ml-auto">
              {user.role}
            </Badge>
          </div>
        </CardHeader>
        <Separator />
        <CardContent className="flex flex-col gap-4 pt-6">
          <div className="flex items-center gap-3 text-sm">
            <Mail className="size-4 text-muted-foreground" />
            <span className="text-muted-foreground">E-mail</span>
            <span className="ml-auto font-medium">{user.email}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Shield className="size-4 text-muted-foreground" />
            <span className="text-muted-foreground">Papel</span>
            <span className="ml-auto font-medium">{user.role}</span>
          </div>
          <Separator />
          <form action="/api/auth/sign-out" className="flex justify-end">
            <Button type="submit" variant="outline">
              <LogOut className="size-4" />
              Sair da conta
            </Button>
          </form>
        </CardContent>
      </Card>
    </PageShell>
  )
}
