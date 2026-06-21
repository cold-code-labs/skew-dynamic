import {
  Activity,
  ArrowUpRight,
  DollarSign,
  type LucideIcon,
  Users,
} from "lucide-react"

import { CountBarsCard, DonutCard, RevenueCard } from "@/components/dashboard/charts"
import { PageShell } from "@/components/page-shell"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { getDashboardCharts } from "@/lib/dashboard/charts"
import { getDashboardStats, getRecentActivity } from "@/lib/data/dashboard"

const STAT_ICONS: Record<string, LucideIcon> = {
  revenue: DollarSign,
  clients: Users,
  sessions: Activity,
  conversion: ArrowUpRight,
}

export default async function DashboardPage() {
  const [stats, activity, charts] = await Promise.all([
    getDashboardStats(),
    getRecentActivity(),
    getDashboardCharts(),
  ])

  return (
    <PageShell title="Dashboard" description="Visão geral da sua plataforma.">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = STAT_ICONS[stat.key] ?? Activity
          return (
            <Card key={stat.key}>
              <CardHeader className="flex flex-row items-center justify-between gap-2 pb-2">
                <CardDescription>{stat.label}</CardDescription>
                <Icon className="size-4 text-muted-foreground" />
              </CardHeader>
              <CardContent className="flex flex-col gap-1">
                <span className="text-2xl font-semibold">{stat.value}</span>
                <Badge variant="secondary" className="w-fit">
                  {stat.delta}
                </Badge>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <RevenueCard data={charts.receitaMensal} />
        <DonutCard
          title="Clientes por status"
          description="Distribuição da base."
          data={charts.clientesPorStatus}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <CountBarsCard
          title="Projetos por fase"
          description="Onde estão as entregas."
          data={charts.projetosPorFase}
        />
        <CountBarsCard
          title="Chamados por prioridade"
          description="Fila de chamados."
          data={charts.chamadosPorPrioridade}
        />

        <Card>
          <CardHeader>
            <CardTitle>Atividade recente</CardTitle>
            <CardDescription>Últimas ações na plataforma.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {activity.map((item, i) => (
              <div key={i} className="flex flex-col gap-0.5">
                <p className="text-sm">
                  <span className="font-medium">{item.who}</span> {item.what}
                </p>
                <span className="text-xs text-muted-foreground">{item.when}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </PageShell>
  )
}
