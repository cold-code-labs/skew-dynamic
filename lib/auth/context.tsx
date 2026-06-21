"use client"

import { createContext, useContext, type ReactNode } from "react"

import type { SessionUser } from "./types"

type AuthValue = {
  user: SessionUser
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

// Client-side auth context. Seeded by the (app) server layout with the user
// resolved via getSession() — so the client never re-fetches or trusts
// localStorage. `logout` just navigates to the server sign-out route handler.
export function AuthProvider({
  user,
  children,
}: {
  user: SessionUser
  children: ReactNode
}) {
  const logout = () => {
    window.location.assign("/api/auth/sign-out")
  }

  return (
    <AuthContext.Provider value={{ user, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider")
  return ctx
}
