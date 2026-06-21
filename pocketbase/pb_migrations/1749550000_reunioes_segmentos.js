/// <reference path="../pb_data/types.d.ts" />
//
// Give `reunioes` a structured, timestamped transcript. Until now the transcript
// lived only as flat HTML in `transcricao` (the diarized "Locutor A: …" lines
// the providers return were flattened on the way in, losing the per-turn timing).
// Two json fields hold the editable representation:
//
//   segmentos — array of { speaker, start, end, text } (start/end in seconds).
//   locutores — speaker key → display name, e.g. { "A": "João" }, so renaming a
//               speaker relabels all of their turns at once.
//
// `transcricao` stays as the rendered HTML (list preview + graceful fallback).
// Idempotent: only adds a missing field, so it's a no-op on fresh installs and
// the upgrade path for instances that already provisioned `reunioes`.

migrate(
  (app) => {
    const col = app.findCollectionByNameOrId("reunioes")
    if (!col.fields.getByName("segmentos")) {
      col.fields.add(new Field({ name: "segmentos", type: "json", maxSize: 5000000 }))
    }
    if (!col.fields.getByName("locutores")) {
      col.fields.add(new Field({ name: "locutores", type: "json", maxSize: 100000 }))
    }
    app.save(col)
  },
  (app) => {
    try {
      const col = app.findCollectionByNameOrId("reunioes")
      col.fields = col.fields.filter(
        (f) => f.name !== "segmentos" && f.name !== "locutores",
      )
      app.save(col)
    } catch (_) {}
  },
)
