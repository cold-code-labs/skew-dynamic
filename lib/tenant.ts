import { DEFAULT_TENANT_ID, MULTI_TENANT } from "@/config/env"

// ─────────────────────────────────────────────────────────────────────────────
// Tenancy seam. The whole app is multi-tenant-capable but ships single-tenant.
//
// With MULTI_TENANT=false (default) every record belongs to DEFAULT_TENANT_ID,
// the switcher is hidden, and `tenantFilter`/`scopedRecord` are transparent —
// the app runs exactly as if tenancy didn't exist. Flip MULTI_TENANT=true to
// scope by the signed-in user's organization (resolved server-side).
//
// This is intentionally a thin seam: it gives every collection an `organization`
// column and a one-call filter, so turning multi-tenancy on later is wiring,
// not a rewrite.
// ─────────────────────────────────────────────────────────────────────────────

export const ORG_FIELD = "organization"

/** True when org-scoping is active. */
export function isMultiTenant(): boolean {
  return MULTI_TENANT
}

/**
 * Resolve the tenant for the current request. Single-tenant → the default org.
 * Multi-tenant → the user's active org (membership lookup is wired here when the
 * flag goes live; until then it falls back to the default so nothing breaks).
 */
export async function getCurrentTenantId(): Promise<string> {
  if (!MULTI_TENANT) return DEFAULT_TENANT_ID
  // TODO(multi-tenant): resolve from the `members` collection for the signed-in
  // user (and an org switcher cookie). Falls back to default until then.
  return DEFAULT_TENANT_ID
}

/**
 * PocketBase filter fragment that scopes a query to the current tenant, or "" in
 * single-tenant mode. Compose into a collection filter:
 *
 *   const scope = await tenantFilter()
 *   pb.collection("x").getFullList({ filter: scope })
 */
export async function tenantFilter(): Promise<string> {
  if (!MULTI_TENANT) return ""
  const id = await getCurrentTenantId()
  return `${ORG_FIELD} = "${id}"`
}

/** Merge two PocketBase filter fragments with AND, dropping empties. */
export function andFilter(...parts: Array<string | undefined>): string {
  return parts
    .filter((p): p is string => !!p && p.length > 0)
    .map((p) => `(${p})`)
    .join(" && ")
}

/** Stamp the tenant id onto a record payload before a write. */
export async function withTenant<T extends Record<string, unknown>>(
  data: T,
): Promise<T & { organization: string }> {
  return { ...data, organization: await getCurrentTenantId() }
}
