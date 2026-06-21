/// <reference path="../pb_data/types.d.ts" />
//
// Showroom modules: collections + demo seed for Financeiro (lancamentos),
// Projetos, Suporte (chamados), Storage (documentos) and the tenancy scaffold
// (organizations). Runs after the init migration on a fresh instance, so a new
// deploy comes up fully populated. Write rules allow any authenticated user —
// tighten per project using the roles model (config/roles.ts).

migrate(
  (app) => {
    const AUTH = "@request.auth.id != ''"

    // ── helper: a base collection with auth read + write ──────────────────
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

    // ── Financeiro ────────────────────────────────────────────────────────
    makeCollection("lancamentos", [
      { name: "descricao", type: "text", required: true },
      { name: "categoria", type: "text" },
      { name: "valor", type: "number" },
      { name: "status", type: "text" },
      { name: "vencimento", type: "text" },
    ])
    seed("lancamentos", [
      { descricao: "Mensalidade Acme", categoria: "Assinatura", valor: 4900, status: "Pago", vencimento: "2026-06-05" },
      { descricao: "Setup Globex", categoria: "Serviço", valor: 12000, status: "Pendente", vencimento: "2026-06-18" },
      { descricao: "Mensalidade Initech", categoria: "Assinatura", valor: 1900, status: "Atrasado", vencimento: "2026-05-28" },
      { descricao: "Consultoria Umbrella", categoria: "Serviço", valor: 8500, status: "Pago", vencimento: "2026-06-02" },
      { descricao: "Reembolso Hooli", categoria: "Reembolso", valor: 320, status: "Pendente", vencimento: "2026-06-20" },
    ])

    // ── Projetos ──────────────────────────────────────────────────────────
    makeCollection("projetos", [
      { name: "nome", type: "text", required: true },
      { name: "responsavel", type: "text" },
      { name: "fase", type: "text" },
      { name: "prazo", type: "text" },
    ])
    seed("projetos", [
      { nome: "Onboarding Acme", responsavel: "Maria Silva", fase: "Em andamento", prazo: "2026-06-30" },
      { nome: "Migração Globex", responsavel: "João Pereira", fase: "Planejamento", prazo: "2026-07-15" },
      { nome: "Portal Umbrella", responsavel: "Ana Costa", fase: "Em andamento", prazo: "2026-06-22" },
      { nome: "Relatórios Hooli", responsavel: "Carlos Souza", fase: "Concluído", prazo: "2026-05-20" },
    ])

    // ── Suporte (chamados) ────────────────────────────────────────────────
    makeCollection("chamados", [
      { name: "assunto", type: "text", required: true },
      { name: "solicitante", type: "text" },
      { name: "prioridade", type: "text" },
      { name: "status", type: "text" },
    ])
    seed("chamados", [
      { assunto: "Erro ao exportar relatório", solicitante: "maria@acme.com", prioridade: "Alta", status: "Aberto" },
      { assunto: "Dúvida sobre faturamento", solicitante: "joao@globex.com", prioridade: "Média", status: "Em análise" },
      { assunto: "Solicitação de acesso", solicitante: "ana@initech.com", prioridade: "Baixa", status: "Resolvido" },
      { assunto: "Lentidão no dashboard", solicitante: "carlos@umbrella.com", prioridade: "Alta", status: "Em análise" },
    ])

    // ── Storage (documentos) — native file field ──────────────────────────
    const documentos = new Collection({
      type: "base",
      name: "documentos",
      listRule: AUTH,
      viewRule: AUTH,
      createRule: AUTH,
      updateRule: AUTH,
      deleteRule: AUTH,
      fields: [
        { name: "name", type: "text", required: true },
        { name: "category", type: "text" },
        { name: "size", type: "number" },
        // protected = file bytes require a short-lived access token (generated
        // server-side for authenticated users), so documents aren't reachable
        // by a bare public URL. See lib/storage/documents.ts.
        { name: "file", type: "file", maxSelect: 1, maxSize: 52428800, protected: true },
        { name: "organization", type: "text" },
      ],
    })
    app.save(documentos)
    // Seed metadata rows (no binary) so the screen looks populated out of the box.
    seed("documentos", [
      { name: "Contrato Acme.pdf", category: "Contratos", size: 248000 },
      { name: "Proposta Globex.pdf", category: "Propostas", size: 132500 },
      { name: "Relatório Q2.xlsx", category: "Relatórios", size: 56900 },
    ])

    // ── Tenancy scaffold: organizations (single default org) ──────────────
    const orgs = new Collection({
      type: "base",
      name: "organizations",
      listRule: AUTH,
      viewRule: AUTH,
      createRule: null,
      updateRule: null,
      deleteRule: null,
      fields: [
        { name: "name", type: "text", required: true },
        { name: "slug", type: "text" },
      ],
    })
    app.save(orgs)
    const orgRec = new Record(app.findCollectionByNameOrId("organizations"))
    orgRec.set("name", "Workspace")
    orgRec.set("slug", "default")
    app.save(orgRec)

    // ── Relax write rules on the init collections so authenticated users can
    //    create/edit/delete from the UI (init shipped them superuser-only) ──
    for (const name of ["clientes", "usuarios"]) {
      try {
        const col = app.findCollectionByNameOrId(name)
        col.createRule = AUTH
        col.updateRule = AUTH
        col.deleteRule = AUTH
        app.save(col)
      } catch (_) {}
    }

    // ── Align seeded member roles with the roles model (config/roles.ts) ──
    try {
      const remap = { "alex@empresa.com": "Proprietário", "maria@empresa.com": "Administrador", "ana@empresa.com": "Membro" }
      for (const email of Object.keys(remap)) {
        try {
          const rec = app.findFirstRecordByData("usuarios", "email", email)
          rec.set("papel", remap[email])
          app.save(rec)
        } catch (_) {}
      }
    } catch (_) {}
  },
  (app) => {
    for (const name of ["lancamentos", "projetos", "chamados", "documentos", "organizations"]) {
      try {
        app.delete(app.findCollectionByNameOrId(name))
      } catch (_) {}
    }
  },
)
