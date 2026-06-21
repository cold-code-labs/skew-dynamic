// ─────────────────────────────────────────────────────────────────────────────
// ROLES & CAPABILITIES — the access model for the "Papéis & Acessos" module.
//
// Per-project you usually just rename labels or toggle a cell in the matrix.
// Roles are ordered from most to least privileged. `can()` is the server-side
// gate; the matrix on the Acessos screen renders straight from this.
// ─────────────────────────────────────────────────────────────────────────────

export type RoleKey = "owner" | "admin" | "member" | "viewer"

/** Things a user can be allowed to do. Add your own and gate with `can()`. */
export type Capability =
  | "data.read"
  | "data.write"
  | "data.delete"
  | "files.read"
  | "files.upload"
  | "members.manage"
  | "settings.manage"

export type RoleDef = {
  key: RoleKey
  label: string
  description: string
  capabilities: Capability[]
}

export const ALL_CAPABILITIES: { key: Capability; label: string }[] = [
  { key: "data.read", label: "Ver registros" },
  { key: "data.write", label: "Criar / editar" },
  { key: "data.delete", label: "Excluir" },
  { key: "files.read", label: "Ver arquivos" },
  { key: "files.upload", label: "Enviar arquivos" },
  { key: "members.manage", label: "Gerir equipe" },
  { key: "settings.manage", label: "Configurações" },
]

export const ROLES: RoleDef[] = [
  {
    key: "owner",
    label: "Proprietário",
    description: "Controle total da plataforma.",
    capabilities: ALL_CAPABILITIES.map((c) => c.key),
  },
  {
    key: "admin",
    label: "Administrador",
    description: "Gere dados, arquivos e equipe.",
    capabilities: [
      "data.read",
      "data.write",
      "data.delete",
      "files.read",
      "files.upload",
      "members.manage",
    ],
  },
  {
    key: "member",
    label: "Membro",
    description: "Opera o dia a dia: cria e edita registros.",
    capabilities: ["data.read", "data.write", "files.read", "files.upload"],
  },
  {
    key: "viewer",
    label: "Visualizador",
    description: "Apenas leitura.",
    capabilities: ["data.read", "files.read"],
  },
]

const ROLE_BY_KEY = new Map(ROLES.map((r) => [r.key, r]))
const ROLE_BY_LABEL = new Map(ROLES.map((r) => [r.label.toLowerCase(), r]))

/** Look up a role def, tolerating unknown/legacy labels. */
export function roleByKey(key: string | undefined): RoleDef | undefined {
  return key ? ROLE_BY_KEY.get(key as RoleKey) : undefined
}

/**
 * Resolve a role from whatever the session carries — a key ("admin") or a
 * display label ("Administrador"). The session user's `role` is the PocketBase
 * `papel` (a label) or a Logto role (a key), so accept both.
 */
export function resolveRole(roleOrLabel: string | undefined): RoleDef | undefined {
  if (!roleOrLabel) return undefined
  return ROLE_BY_KEY.get(roleOrLabel as RoleKey) ?? ROLE_BY_LABEL.get(roleOrLabel.toLowerCase())
}

/** Capability check from a role key or label. Unknown → least privilege. */
export function can(roleOrLabel: string | undefined, capability: Capability): boolean {
  const role = resolveRole(roleOrLabel)
  return role ? role.capabilities.includes(capability) : false
}
