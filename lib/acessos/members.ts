import { DATA_MODE } from "@/config/env"
import { andFilter, tenantFilter } from "@/lib/tenant"

// Members of the workspace — backs the "Acessos" screen. Distinct from the auth
// `users` collection people log in with: this is the display/role list the admin
// manages. Stored in the `usuarios` PocketBase collection.
export type Member = {
  id?: string
  nome: string
  email: string
  papel: string
  status: string
}

const STUB: Member[] = [
  { nome: "Alex Morgan", email: "alex@empresa.com", papel: "Proprietário", status: "Ativo" },
  { nome: "Maria Silva", email: "maria@empresa.com", papel: "Administrador", status: "Ativo" },
  { nome: "João Pereira", email: "joao@empresa.com", papel: "Membro", status: "Ativo" },
  { nome: "Ana Costa", email: "ana@empresa.com", papel: "Membro", status: "Convidado" },
  { nome: "Carlos Souza", email: "carlos@empresa.com", papel: "Visualizador", status: "Inativo" },
]

export async function listMembers(): Promise<Member[]> {
  if (DATA_MODE !== "pocketbase") return STUB

  const { pbServer } = await import("@/lib/auth/pocketbase")
  const pb = await pbServer()
  const recs = await pb.collection("usuarios").getFullList({
    sort: "nome",
    filter: andFilter(await tenantFilter()),
  })
  return recs.map((r) => ({
    id: r.id,
    nome: (r.nome as string) ?? "",
    email: (r.email as string) ?? "",
    papel: (r.papel as string) || "Membro",
    status: (r.status as string) || "Ativo",
  }))
}
