/// <reference path="../pb_data/types.d.ts" />
//
// RBAC wiring: give the auth `users` collection a `papel` (role) field so the
// app can resolve capabilities (config/roles.ts), let authenticated admins
// create members (the invite flow), and promote the seeded demo user so the
// showroom shows every action.

migrate(
  (app) => {
    const users = app.findCollectionByNameOrId("users")
    users.fields.add(new Field({ name: "papel", type: "text" }))
    // Authenticated users may create members (gated in-app by members.manage).
    users.createRule = "@request.auth.id != ''"
    app.save(users)

    try {
      const demo = app.findFirstRecordByData("users", "email", "demo@coldcodelabs.com")
      demo.set("papel", "Proprietário")
      app.save(demo)
    } catch (_) {}
  },
  (app) => {
    try {
      const users = app.findCollectionByNameOrId("users")
      users.createRule = null
      app.save(users)
    } catch (_) {}
  },
)
