"use client"

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { MonthPoint, Slice } from "@/lib/dashboard/charts"

// Theme-aware palette: shades of the brand --primary, so charts repaint with the
// active preset (config/brand.ts) automatically.
const PALETTE = [
  "var(--primary)",
  "color-mix(in oklch, var(--primary) 70%, var(--muted))",
  "color-mix(in oklch, var(--primary) 45%, var(--muted))",
  "color-mix(in oklch, var(--primary) 28%, var(--muted))",
  "var(--muted-foreground)",
]

const tooltipStyle = {
  background: "var(--popover)",
  border: "1px solid var(--border)",
  borderRadius: "0.5rem",
  fontSize: "0.75rem",
  color: "var(--popover-foreground)",
}

function BRL(n: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(n)
}

export function RevenueCard({ data }: { data: MonthPoint[] }) {
  return (
    <Card className="lg:col-span-2">
      <CardHeader>
        <CardTitle>Receita por mês</CardTitle>
        <CardDescription>Soma dos lançamentos por vencimento.</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data} margin={{ left: 8, right: 8 }}>
            <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} stroke="var(--muted-foreground)" />
            <YAxis tickFormatter={(v) => BRL(Number(v))} tickLine={false} axisLine={false} width={64} fontSize={11} stroke="var(--muted-foreground)" />
            <Tooltip cursor={{ fill: "var(--muted)" }} contentStyle={tooltipStyle} formatter={(v) => [BRL(Number(v)), "Receita"]} />
            <Bar dataKey="total" fill="var(--primary)" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function DonutCard({ title, description, data }: { title: string; description?: string; data: Slice[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Tooltip contentStyle={tooltipStyle} />
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2} stroke="var(--card)">
              {data.map((_, i) => (
                <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-2 flex flex-wrap justify-center gap-x-4 gap-y-1">
          {data.map((s, i) => (
            <div key={s.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="size-2.5 rounded-full" style={{ background: PALETTE[i % PALETTE.length] }} />
              {s.name} ({s.value})
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function CountBarsCard({ title, description, data }: { title: string; description?: string; data: Slice[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 8 }}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={96} fontSize={12} stroke="var(--muted-foreground)" />
            <Tooltip cursor={{ fill: "var(--muted)" }} contentStyle={tooltipStyle} />
            <Bar dataKey="value" fill="var(--primary)" radius={[0, 6, 6, 0]} barSize={22} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
