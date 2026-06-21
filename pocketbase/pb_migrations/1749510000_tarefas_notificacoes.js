/// <reference path="../pb_data/types.d.ts" />
//
// New showroom modules: Tarefas (a CRUD resource) and Notificações (a seeded
// feed). Runs after the earlier module migrations, so fresh deploys — and
// already-provisioned instances (their /pb_data is migrated on next boot) —
// come up with both collections populated. Auth read+write; tighten per project.

migrate(
  (app) => {
    const AUTH = "@request.auth.id != ''"

    function makeCollection(name, fields) {
      const col = new Collection({
        type: "base",
        name: name,
        listRule: AUTH,
        viewRule: AUTH,
        createRule: AUTH,
        updateRule: AUTH,
        deleteRule: AUTH,
        fields: fields.concat([{ name: "organization", type: "text" }]),
      })
      app.save(col)
      return app.findCollectionByNameOrId(name)
    }

    function seed(name, rows) {
      const col = app.findCollectionByNameOrId(name)
      for (const data of rows) {
        const rec = new Record(col)
        for (const k of Object.keys(data)) rec.set(k, data[k])
        app.save(rec)
      }
    }

    // ── Tarefas ───────────────────────────────────────────────────────────
    makeCollection("tarefas", [
      { name: "titulo", type: "text", required: true },
      { name: "responsavel", type: "text" },
      { name: "prioridade", type: "text" },
      { name: "status", type: "text" },
      { name: "prazo", type: "text" },
    ])
    seed("tarefas", [
      { titulo: "Revisar contrato Acme", responsavel: "Maria Silva", prioridade: "Alta", status: "Em progresso", prazo: "2026-06-12" },
      { titulo: "Preparar relatório mensal", responsavel: "João Pereira", prioridade: "Média", status: "A fazer", prazo: "2026-06-18" },
      { titulo: "Onboarding novo cliente", responsavel: "Ana Costa", prioridade: "Alta", status: "A fazer", prazo: "2026-06-10" },
      { titulo: "Atualizar documentação", responsavel: "Carlos Souza", prioridade: "Baixa", status: "Concluída", prazo: "2026-06-05" },
      { titulo: "Follow-up proposta Globex", responsavel: "Maria Silva", prioridade: "Média", status: "Em progresso", prazo: "2026-06-22" },
    ])

    // ── Notificações ──────────────────────────────────────────────────────
    makeCollection("notificacoes", [
      { name: "titulo", type: "text", required: true },
      { name: "mensagem", type: "text" },
      { name: "tipo", type: "text" }, // info | sucesso | alerta
      { name: "lida", type: "bool" },
      { name: "data", type: "text" },
    ])
    seed("notificacoes", [
      { titulo: "Novo cliente cadastrado", mensagem: "Acme Corp foi adicionada à plataforma.", tipo: "sucesso", lida: false, data: "2026-06-09" },
      { titulo: "Pagamento atrasado", mensagem: "A mensalidade da Initech está vencida.", tipo: "alerta", lida: false, data: "2026-06-08" },
      { titulo: "Projeto concluído", mensagem: "Relatórios Hooli foi marcado como concluído.", tipo: "info", lida: true, data: "2026-06-07" },
      { titulo: "Novo chamado de suporte", mensagem: "Erro ao exportar relatório (prioridade alta).", tipo: "alerta", lida: false, data: "2026-06-06" },
      { titulo: "Backup concluído", mensagem: "O backup diário foi finalizado com sucesso.", tipo: "info", lida: true, data: "2026-06-05" },
    ])
  },
  (app) => {
    for (const name of ["tarefas", "notificacoes"]) {
      try {
        app.delete(app.findCollectionByNameOrId(name))
      } catch (_) {}
    }
  },
)
