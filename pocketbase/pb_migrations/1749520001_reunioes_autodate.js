/// <reference path="../pb_data/types.d.ts" />
//
// Give `reunioes` proper `created`/`updated` autodate fields. JSVM-created base
// collections do NOT get them automatically (PocketBase added them as opt-in
// autodate fields), so the previous migration's collection had neither — and a
// query with `sort=-created` (the meetings reader sorts newest-first) returned
// a 400. Idempotent: only adds a field that's missing, so it's a no-op on fresh
// installs (where this could later be folded into the create) and the fix for
// instances that already applied 1749520000 (e.g. the first test deploy).

migrate(
  (app) => {
    const col = app.findCollectionByNameOrId("reunioes")
    if (!col.fields.getByName("created")) {
      col.fields.add(
        new Field({ name: "created", type: "autodate", onCreate: true, onUpdate: false }),
      )
    }
    if (!col.fields.getByName("updated")) {
      col.fields.add(
        new Field({ name: "updated", type: "autodate", onCreate: true, onUpdate: true }),
      )
    }
    app.save(col)
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("reunioes")
      const keep = col.fields.filter((f) => f.name !== "created" && f.name !== "updated")
      col.fields = keep
      app.save(col)
    } catch (_) {}
  },
)
