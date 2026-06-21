/// <reference path="../pb_data/types.d.ts" />
//
// Initial schema + seed for the bundled "light" backend.
// PocketBase applies pending migrations from this folder automatically on
// `serve`, so a fresh instance comes up with these collections + demo data.

migrate(
  (app) => {
    // ── clientes (backs the Clientes screen) ──────────────────────────────
    const clientes = new Collection({
      type: "base",
      name: "clientes",
      // Any authenticated user can read; writes are superuser-only (admin UI).
      listRule: "@request.auth.id != ''",
      viewRule: "@request.auth.id != ''",
      createRule: null,
      updateRule: null,
      deleteRule: null,
      fields: [
        { name: "nome", type: "text", required: true },
        { name: "contato", type: "text" },
        { name: "plano", type: "text" },
        { name: "status", type: "text" },
      ],
    })
    app.save(clientes)

    // ── usuarios (backs the Usuários screen — a display list, distinct from
    //    the auth `users` collection people log in with) ────────────────────
    const usuarios = new Collection({
      type: "base",
      name: "usuarios",
      listRule: "@request.auth.id != ''",
      viewRule: "@request.auth.id != ''",
      createRule: null,
      updateRule: null,
      deleteRule: null,
      fields: [
        { name: "nome", type: "text", required: true },
        { name: "email", type: "text" },
        { name: "papel", type: "text" },
        { name: "status", type: "text" },
      ],
    })
    app.save(usuarios)

    // ── seed clientes ─────────────────────────────────────────────────────
    const clientesCol = app.findCollectionByNameOrId("clientes")
    const seedClientes = [
      { nome: "Acme Corp", contato: "maria@acme.com", plano: "Enterprise", status: "Ativo" },
      { nome: "Globex", contato: "joao@globex.com", plano: "Pro", status: "Ativo" },
      { nome: "Initech", contato: "ana@initech.com", plano: "Pro", status: "Inativo" },
      { nome: "Umbrella", contato: "carlos@umbrella.com", plano: "Starter", status: "Ativo" },
      { nome: "Soylent", contato: "lucia@soylent.com", plano: "Enterprise", status: "Pendente" },
      { nome: "Hooli", contato: "pedro@hooli.com", plano: "Starter", status: "Ativo" },
    ]
    for (const data of seedClientes) {
      const rec = new Record(clientesCol)
      rec.set("nome", data.nome)
      rec.set("contato", data.contato)
      rec.set("plano", data.plano)
      rec.set("status", data.status)
      app.save(rec)
    }

    // ── seed usuarios ─────────────────────────────────────────────────────
    const usuariosCol = app.findCollectionByNameOrId("usuarios")
    const seedUsuarios = [
      { nome: "Alex Morgan", email: "alex@empresa.com", papel: "Administrador", status: "Ativo" },
      { nome: "Maria Silva", email: "maria@empresa.com", papel: "Editor", status: "Ativo" },
      { nome: "João Pereira", email: "joao@empresa.com", papel: "Visualizador", status: "Ativo" },
      { nome: "Ana Costa", email: "ana@empresa.com", papel: "Editor", status: "Convidado" },
      { nome: "Carlos Souza", email: "carlos@empresa.com", papel: "Visualizador", status: "Inativo" },
    ]
    for (const data of seedUsuarios) {
      const rec = new Record(usuariosCol)
      rec.set("nome", data.nome)
      rec.set("email", data.email)
      rec.set("papel", data.papel)
      rec.set("status", data.status)
      app.save(rec)
    }

    // ── seed a demo login user (auth collection `users`) ──────────────────
    // Override at deploy time via the entrypoint if you want different creds;
    // this guarantees the app has someone to log in as out of the box.
    const usersCol = app.findCollectionByNameOrId("users")
    const demo = new Record(usersCol)
    demo.set("email", "demo@coldcodelabs.com")
    demo.set("name", "Demo CCL")
    demo.set("emailVisibility", true)
    demo.set("verified", true)
    demo.setPassword("snowdemo123")
    app.save(demo)
  },
  (app) => {
    // down — best-effort teardown
    for (const name of ["clientes", "usuarios"]) {
      try {
        app.delete(app.findCollectionByNameOrId(name))
      } catch (_) {}
    }
    try {
      app.delete(app.findFirstRecordByData("users", "email", "demo@coldcodelabs.com"))
    } catch (_) {}
  },
)
