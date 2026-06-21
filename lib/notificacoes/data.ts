import { DATA_MODE } from "@/config/env"

export type Notificacao = {
  id?: string
  titulo: string
  mensagem: string
  tipo: string // info | sucesso | alerta
  lida: boolean
  data: string
}

// Stub feed (mirrors the migration seed) so the screen works with zero backend.
const STUB: Notificacao[] = [
  { titulo: "Novo cliente cadastrado", mensagem: "Acme Corp foi adicionada à plataforma.", tipo: "sucesso", lida: false, data: "2026-06-09" },
  { titulo: "Pagamento atrasado", mensagem: "A mensalidade da Initech está vencida.", tipo: "alerta", lida: false, data: "2026-06-08" },
  { titulo: "Projeto concluído", mensagem: "Relatórios Hooli foi marcado como concluído.", tipo: "info", lida: true, data: "2026-06-07" },
  { titulo: "Novo chamado de suporte", mensagem: "Erro ao exportar relatório (prioridade alta).", tipo: "alerta", lida: false, data: "2026-06-06" },
  { titulo: "Backup concluído", mensagem: "O backup diário foi finalizado com sucesso.", tipo: "info", lida: true, data: "2026-06-05" },
]

/** All notifications, newest first. Mode-agnostic (stub | pocketbase). */
export async function listNotificacoes(): Promise<Notificacao[]> {
  if (DATA_MODE !== "pocketbase") return STUB

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("notificacoes").getFullList({ sort: "-data" })
  return recs.map((r) => ({
    id: r.id,
    titulo: r.titulo as string,
    mensagem: (r.mensagem as string) ?? "",
    tipo: (r.tipo as string) ?? "info",
    lida: Boolean(r.lida),
    data: (r.data as string) ?? "",
  }))
}
