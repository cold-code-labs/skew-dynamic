/// <reference path="../pb_data/types.d.ts" />
//
// Turn ON file protection for the documentos.file field on instances that were
// created before it was protected by default (fresh installs already get it via
// 1749480000). Protected files require a `?token=` to download — the app
// generates one per request for the logged-in user (lib/storage/documents.ts).

migrate(
  (app) => {
    const col = app.findCollectionByNameOrId("documentos")
    const field = col.fields.getByName("file")
    if (field) {
      field.protected = true
      app.save(col)
    }
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("documentos")
      const field = col.fields.getByName("file")
      if (field) {
        field.protected = false
        app.save(col)
      }
    } catch (_) {}
  },
)
