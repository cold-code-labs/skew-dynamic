import { cookies } from "next/headers"

import type { SessionUser } from "./types"

// Name of the demo session cookie. Kept in sync with proxy.ts.
export const STUB_COOKIE_NAME = "template_session"

// Demo identity returned by the one-click stub login. Lets the template run
// with zero backend. Swap AUTH_MODE=logto for real authentication.
const STUB_USER: SessionUser = {
  id: "usr_demo",
  name: "Alex Morgan",
  email: "alex@template.app",
  role: "Administrador",
}

export async function getStubSession(): Promise<SessionUser | null> {
  const store = await cookies()
  return store.get(STUB_COOKIE_NAME) ? STUB_USER : null
}

export async function startStubSession(): Promise<void> {
  const store = await cookies()
  store.set(STUB_COOKIE_NAME, "1", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 7,
  })
}

export async function endStubSession(): Promise<void> {
  const store = await cookies()
  store.delete(STUB_COOKIE_NAME)
}
