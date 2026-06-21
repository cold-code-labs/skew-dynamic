/// <reference path="../pb_data/types.d.ts" />
//
// Reuniões Gravadas: a collection that stores browser-recorded meeting audio
// plus its Whisper transcription. The `audio` file field is protected (bytes
// need a short-lived access token, like documentos) — see lib/reunioes. Runs
// after the earlier module migrations, so fresh deploys and already-provisioned
// instances (their /pb_data migrates on next boot) come up with it. Auth
// read+write; tighten per project.

migrate(
  (app) => {
    const AUTH = "@request.auth.id != ''"

    const reunioes = new Collection({
      type: "base",
      name: "reunioes",
      listRule: AUTH,
      viewRule: AUTH,
      createRule: AUTH,
      updateRule: AUTH,
      deleteRule: AUTH,
      fields: [
        { name: "titulo", type: "text", required: true },
        // The recorded audio. Protected: bytes require a per-request token
        // (generated server-side for the signed-in user), so a recording is not
        // reachable by a bare public URL. 32MB cap (above Whisper's 25MB limit).
        { name: "audio", type: "file", maxSelect: 1, maxSize: 33554432, protected: true },
        { name: "mime", type: "text" }, // e.g. audio/webm;codecs=opus
        { name: "duracao", type: "number" }, // seconds
        // gravada | transcrevendo | transcrita | erro
        { name: "status", type: "text" },
        { name: "transcricao", type: "editor" },
        { name: "idioma", type: "text" }, // optional ISO hint, e.g. "pt"
        { name: "organization", type: "text" },
      ],
    })
    app.save(reunioes)

    // Seed a couple of demo meetings (no binary audio) so the screen looks
    // populated out of the box — recording produces the real audio rows.
    const col = app.findCollectionByNameOrId("reunioes")
    const rows = [
      {
        titulo: "Kickoff Acme — Onboarding",
        duracao: 372,
        status: "transcrita",
        idioma: "pt",
        transcricao:
          "<p>Maria abriu a reunião apresentando o escopo do onboarding da Acme. " +
          "Ficou definido que a primeira entrega será o portal de acesso até o fim do mês. " +
          "João assume a integração de dados; Ana cuida do treinamento da equipe do cliente.</p>",
      },
      {
        titulo: "Alinhamento semanal — Produto",
        duracao: 845,
        status: "transcrita",
        idioma: "pt",
        transcricao:
          "<p>Revisão das tarefas da sprint. O módulo de relatórios foi priorizado " +
          "após o feedback da Globex. Carlos levantou o risco do prazo da migração; " +
          "decidido adiar a feature de exportação para a próxima sprint.</p>",
      },
      {
        titulo: "Call comercial — Umbrella",
        duracao: 198,
        status: "gravada",
        idioma: "pt",
        transcricao: "",
      },
    ]
    for (const data of rows) {
      const rec = new Record(col)
      for (const k of Object.keys(data)) rec.set(k, data[k])
      app.save(rec)
    }
  },
  (app) => {
    try {
      app.delete(app.findCollectionByNameOrId("reunioes"))
    } catch (_) {}
  },
)
