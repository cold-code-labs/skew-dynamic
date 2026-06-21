"use client"

import { can, type Capability } from "@/config/roles"
import { useAuth } from "@/lib/auth/context"

// Client-side capability check, driven by the signed-in user's role. Use to hide
// actions/modules the user can't perform. The server action still re-checks via
// requireCapability — this is UX, not the security boundary.
export function useCan(): (capability: Capability) => boolean {
  const { user } = useAuth()
  return (capability: Capability) => can(user.role, capability)
}
