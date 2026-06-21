import { StorageView } from "@/components/storage/storage-view"
import { groupByCategory, listDocumentos } from "@/lib/storage/documents"
import { listReunioes } from "@/lib/reunioes/meetings"

const DEFAULT_CATEGORIES = ["Geral", "Contratos", "Propostas", "Financeiro", "Relatórios", "Marca"]

export default async function ArquivosPage() {
  const [docs, recordings] = await Promise.all([listDocumentos(), listReunioes()])
  const groups = groupByCategory(docs).map(([category, docs]) => ({ category, docs }))
  const categories = Array.from(
    new Set([...DEFAULT_CATEGORIES, ...docs.map((d) => d.category)]),
  )
  return <StorageView groups={groups} categories={categories} recordings={recordings} />
}
