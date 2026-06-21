import { MembersTable } from "@/components/acessos/members-table"
import { RoleMatrix } from "@/components/acessos/role-matrix"
import { PageShell } from "@/components/page-shell"
import { listMembers } from "@/lib/acessos/members"
import { requirePage } from "@/lib/auth/guard"

export default async function AcessosPage() {
  await requirePage("members.manage")
  const members = await listMembers()
  return (
    <PageShell title="Acessos" description="Equipe, papéis e permissões da plataforma.">
      <MembersTable members={members} />
      <RoleMatrix />
    </PageShell>
  )
}
