// Shared, backend-agnostic shape of the authenticated user. Both the stub and
// Logto adapters resolve a session into this type.
export type SessionUser = {
  id: string
  name: string
  email: string
  role: string
  avatar?: string
}
