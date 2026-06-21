import "server-only"

import { AUTH_MODE, HAULDR_REALTIME_URL } from "@/config/env"
import { getAccessToken, getSession } from "@/lib/auth/session"
import { logWarn } from "@/lib/log"

import { HauldrLive, type RealtimeProps } from "./live"

// Server seam for Hauldr Realtime. Realtime is opt-in per instance: it's on only
// in the Hauldr tier with a Realtime endpoint configured (HAULDR_REALTIME_URL).
// When off, the app falls back to refresh-on-action — realtime is a nicety layered
// on top, never the source of truth (data always flows through RLS-guarded PostgREST).
export function realtimeEnabled(): boolean {
  return AUTH_MODE === "hauldr" && !!HAULDR_REALTIME_URL
}

/**
 * Build the client-side realtime config to hand a client component: the public
 * WSS URL, the signed-in user's own access token (so the browser can join the
 * private channel), and their identity for presence. Null when realtime is off
 * or there's no session — the component then just stays static.
 */
export async function realtimeProps(): Promise<RealtimeProps | null> {
  if (!realtimeEnabled()) return null
  const [token, user] = await Promise.all([getAccessToken(), getSession()])
  if (!token || !user) return null
  return { url: HAULDR_REALTIME_URL, accessToken: token, me: { key: user.id, name: user.name } }
}

/**
 * Fire a "changed" ping on a private topic so other viewers refresh. Best-effort:
 * the payload is just a ping (the real data still goes through RLS-guarded
 * PostgREST on refresh), and a realtime hiccup must never fail the mutation.
 */
export async function broadcastChange(topic: string): Promise<void> {
  if (!realtimeEnabled()) return
  try {
    const token = await getAccessToken()
    if (!token) return
    const live = new HauldrLive(HAULDR_REALTIME_URL, token)
    await live.broadcast(topic, "changed", { at: Date.now() }, { private: true })
  } catch (e) {
    logWarn("realtime", `broadcastChange(${topic}) failed`, e)
  }
}
