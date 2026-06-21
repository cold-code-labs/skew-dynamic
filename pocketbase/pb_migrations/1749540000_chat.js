/// <reference path="../pb_data/types.d.ts" />
//
// Chat module: internal team chat with role-gated channels (Direção, Professores,
// Coordenação, Geral) plus 1:1 direct messages, delivered in real time.
//
// Two collections:
//   • chat_channels  — a conversation. tipo="canal" (group, gated by role +
//                      explicit member overrides) or tipo="dm" (1:1, the two
//                      participants live in `members`).
//   • chat_messages  — a message in a channel (text now; optional file attach).
//
// Access control lives in the TypeScript seams (lib/chat/* + config/roles.ts),
// NOT in PocketBase rules — same approach as chamados/reuniões. The PB rules are
// the simple authenticated gate; the relay subscribes only to the channels the
// app says the user may see. Idempotent + reversible so it's safe on fresh
// installs AND already-deployed instances (their /pb_data migrates on next boot).

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

    const users = app.findCollectionByNameOrId("users")

    // ── 1) chat_channels ────────────────────────────────────────────────────
    let channels = safeFind("chat_channels")
    if (!channels) {
      channels = new Collection({
        type: "base",
        name: "chat_channels",
        listRule: AUTH,
        viewRule: AUTH,
        createRule: AUTH,
        updateRule: AUTH,
        deleteRule: AUTH,
        fields: [
          { name: "nome", type: "text", required: true },
          { name: "descricao", type: "text" },
          { name: "slug", type: "text" },
          { name: "tipo", type: "text" }, // canal | dm
          { name: "allowed_roles", type: "text" }, // CSV de RoleKey; vazio = todos
          {
            name: "members",
            type: "relation",
            required: false,
            maxSelect: 200,
            cascadeDelete: false,
            collectionId: users.id,
          },
          { name: "icone", type: "text" },
          { name: "organization", type: "text" },
          { name: "created", type: "autodate", onCreate: true, onUpdate: false },
          { name: "updated", type: "autodate", onCreate: true, onUpdate: true },
        ],
      })
      app.save(channels)
    }

    // ── 2) chat_messages ────────────────────────────────────────────────────
    if (!safeFind("chat_messages")) {
      const messages = new Collection({
        type: "base",
        name: "chat_messages",
        listRule: AUTH,
        viewRule: AUTH,
        createRule: AUTH,
        updateRule: AUTH,
        deleteRule: AUTH,
        fields: [
          {
            name: "channel",
            type: "relation",
            required: true,
            maxSelect: 1,
            cascadeDelete: true,
            collectionId: channels.id,
          },
          {
            name: "autor",
            type: "relation",
            required: false,
            maxSelect: 1,
            cascadeDelete: false,
            collectionId: users.id,
          },
          { name: "autor_nome", type: "text" },
          { name: "corpo", type: "text" },
          { name: "anexo", type: "file", maxSelect: 1, maxSize: 10485760 },
          { name: "tipo", type: "text" }, // mensagem | evento
          { name: "organization", type: "text" },
          { name: "created", type: "autodate", onCreate: true, onUpdate: false },
        ],
      })
      app.save(messages)
    }

    // ── 3) Seed channels (guarded by slug — re-runs never dupe) ──────────────
    const channelsCol = app.findCollectionByNameOrId("chat_channels")
    function seedCanal(data) {
      try {
        app.findFirstRecordByData("chat_channels", "slug", data.slug)
        return // already exists
      } catch (_) {
        const rec = new Record(channelsCol)
        rec.set("nome", data.nome)
        rec.set("slug", data.slug)
        rec.set("descricao", data.descricao || "")
        rec.set("tipo", "canal")
        rec.set("allowed_roles", data.allowed_roles || "")
        rec.set("icone", data.icone || "")
        app.save(rec)
      }
    }
    seedCanal({
      nome: "Geral",
      slug: "geral",
      descricao: "Canal aberto a toda a escola.",
      allowed_roles: "", // todos os logados
      icone: "Hash",
    })
    seedCanal({
      nome: "Direção",
      slug: "direcao",
      descricao: "Assuntos da direção e administração.",
      allowed_roles: "owner,admin",
      icone: "ShieldCheck",
    })
    seedCanal({
      nome: "Coordenação",
      slug: "coordenacao",
      descricao: "Coordenação pedagógica.",
      allowed_roles: "owner,admin",
      icone: "ClipboardList",
    })
    seedCanal({
      nome: "Professores",
      slug: "professores",
      descricao: "Sala dos professores.",
      allowed_roles: "owner,admin,member",
      icone: "GraduationCap",
    })

    // ── 4) A couple of demo messages in #geral (from the seeded demo user) ───
    try {
      const geral = app.findFirstRecordByData("chat_channels", "slug", "geral")
      const msgCount = app.findRecordsByFilter(
        "chat_messages",
        `channel = "${geral.id}"`,
        "",
        1,
        0,
      )
      if (!msgCount.length) {
        const msgCol = app.findCollectionByNameOrId("chat_messages")
        let autorId = ""
        let autorNome = "Direção"
        try {
          const demo = app.findFirstRecordByData("users", "email", "demo@coldcodelabs.com")
          autorId = demo.id
          autorNome = demo.get("name") || "Direção"
        } catch (_) {}
        const demoMsgs = [
          "Bem-vindos ao chat da escola! 🎒 Use o #geral para avisos gerais.",
          "Direção e Coordenação têm canais próprios; a sala dos professores fica em #professores.",
        ]
        for (const corpo of demoMsgs) {
          const rec = new Record(msgCol)
          rec.set("channel", geral.id)
          rec.set("autor", autorId)
          rec.set("autor_nome", autorNome)
          rec.set("corpo", corpo)
          rec.set("tipo", "mensagem")
          app.save(rec)
        }
      }
    } catch (_) {}
  },
  (app) => {
    for (const name of ["chat_messages", "chat_channels"]) {
      try {
        app.delete(app.findCollectionByNameOrId(name))
      } catch (_) {}
    }
  },
)
