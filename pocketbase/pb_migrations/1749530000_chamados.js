/// <reference path="../pb_data/types.d.ts" />
//
// Chamados (service desk): graduate the flat `chamados` collection — created in
// 1749480000_modules.js as a 4-field table for the old "Suporte" resource —
// into a real ticketing collection (description + queue + assignee + autodate),
// and add `chamados_comentarios` for the thread (comments + system events).
//
// Idempotent: only adds fields that are missing and only creates the thread
// collection if absent — so it's safe on fresh installs AND on already-deployed
// instances (e.g. arte-one), whose /pb_data migrates on next boot. The previous
// `chamados` rows are backfilled (queue + description) and the old "Em análise"
// status is normalized to the new workflow's "Em andamento". Auth read+write;
// tighten per project using config/roles.ts.

migrate(
  (app) => {
    const AUTH = "@request.auth.id != ''"

    function safeFind(name) {
      try {
        return app.findCollectionByNameOrId(name)
      } catch (_) {
        return null
      }
    }

    // ── 1) Extend `chamados` with the service-desk fields ───────────────────
    const chamados = app.findCollectionByNameOrId("chamados")
    function ensure(col, name, def) {
      if (!col.fields.getByName(name)) col.fields.add(new Field(def))
    }
    ensure(chamados, "descricao", { name: "descricao", type: "text" })
    ensure(chamados, "departamento", { name: "departamento", type: "text" })
    ensure(chamados, "responsavel", { name: "responsavel", type: "text" })
    ensure(chamados, "created", { name: "created", type: "autodate", onCreate: true, onUpdate: false })
    ensure(chamados, "updated", { name: "updated", type: "autodate", onCreate: true, onUpdate: true })
    app.save(chamados)

    // Backfill the rows seeded by 1749480000: give each a queue + description,
    // and normalize the retired "Em análise" status to "Em andamento".
    const BACKFILL = {
      "Erro ao exportar relatório": {
        departamento: "TI",
        descricao:
          "Ao clicar em exportar PDF no dashboard, a página fica carregando e nada acontece. Acontece em todos os navegadores.",
      },
      "Dúvida sobre faturamento": {
        departamento: "Financeiro",
        descricao: "Gostaria de entender a cobrança da última fatura — há um item que não reconheço.",
      },
      "Solicitação de acesso": {
        departamento: "TI",
        descricao: "Preciso de acesso de leitura ao módulo financeiro para o fechamento do mês.",
      },
      "Lentidão no dashboard": {
        departamento: "TI",
        descricao: "O dashboard demora mais de 10s para carregar nos horários de pico.",
      },
    }
    try {
      const rows = app.findRecordsByFilter("chamados", "id != ''", "", 500, 0)
      for (const r of rows) {
        const patch = BACKFILL[r.get("assunto")]
        if (patch) {
          if (!r.get("departamento")) r.set("departamento", patch.departamento)
          if (!r.get("descricao")) r.set("descricao", patch.descricao)
        } else if (!r.get("departamento")) {
          r.set("departamento", "Geral")
        }
        if (r.get("status") === "Em análise") r.set("status", "Em andamento")
        app.save(r)
      }
    } catch (_) {}

    // A couple of extra demo tickets so the showroom reads like a service desk
    // with more than one queue. Guarded by assunto so a re-run never dupes.
    function seedChamado(data) {
      try {
        app.findFirstRecordByData("chamados", "assunto", data.assunto)
        return // already exists
      } catch (_) {
        const rec = new Record(chamados)
        for (const k of Object.keys(data)) rec.set(k, data[k])
        app.save(rec)
      }
    }
    seedChamado({
      assunto: "Ar-condicionado da sala 3 não liga",
      descricao: "O ar da sala de reuniões 3 parou de funcionar desde ontem. Sala está quente.",
      departamento: "Manutenção",
      prioridade: "Média",
      status: "Em andamento",
      solicitante: "joao@globex.com",
      responsavel: "Carlos Souza",
    })
    seedChamado({
      assunto: "Atualizar dados bancários para folha",
      descricao: "Troquei de banco e preciso atualizar a conta para o pagamento da folha.",
      departamento: "RH",
      prioridade: "Alta",
      status: "Aberto",
      solicitante: "ana@initech.com",
      responsavel: "",
    })

    // ── 2) chamados_comentarios (thread: comments + system events) ──────────
    if (!safeFind("chamados_comentarios")) {
      const comentarios = new Collection({
        type: "base",
        name: "chamados_comentarios",
        listRule: AUTH,
        viewRule: AUTH,
        createRule: AUTH,
        updateRule: AUTH,
        deleteRule: AUTH,
        fields: [
          {
            name: "chamado",
            type: "relation",
            required: true,
            maxSelect: 1,
            cascadeDelete: true,
            collectionId: chamados.id,
          },
          { name: "autor", type: "text" },
          { name: "corpo", type: "text" },
          { name: "tipo", type: "text" }, // comentario | evento
          { name: "organization", type: "text" },
          { name: "created", type: "autodate", onCreate: true, onUpdate: false },
        ],
      })
      app.save(comentarios)

      // Seed a thread on the Manutenção ticket so the detail screen is populated.
      try {
        const col = app.findCollectionByNameOrId("chamados_comentarios")
        const ticket = app.findFirstRecordByData(
          "chamados",
          "assunto",
          "Ar-condicionado da sala 3 não liga",
        )
        const thread = [
          { autor: "Sistema", tipo: "evento", corpo: "Chamado aberto na fila Manutenção." },
          { autor: "Sistema", tipo: "evento", corpo: "Chamado atribuído a Carlos Souza." },
          {
            autor: "Carlos Souza",
            tipo: "comentario",
            corpo: "Já abri um chamado com a empresa de manutenção. Previsão de visita amanhã de manhã.",
          },
        ]
        for (const t of thread) {
          const rec = new Record(col)
          rec.set("chamado", ticket.id)
          rec.set("autor", t.autor)
          rec.set("corpo", t.corpo)
          rec.set("tipo", t.tipo)
          app.save(rec)
        }
      } catch (_) {}
    }
  },
  (app) => {
    try {
      app.delete(app.findCollectionByNameOrId("chamados_comentarios"))
    } catch (_) {}
    try {
      const col = app.findCollectionByNameOrId("chamados")
      col.fields = col.fields.filter(
        (f) => ["descricao", "departamento", "responsavel", "created", "updated"].indexOf(f.name) === -1,
      )
      app.save(col)
    } catch (_) {}
  },
)
