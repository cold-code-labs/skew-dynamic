import type { LogtoNextConfig } from "@logto/next"

import { APP_BASE_URL } from "@/config/env"

// Logto server-side config. Only consumed when AUTH_MODE=logto.
//
// In the Logto console, for this application register:
//   - Redirect URI:           `${baseUrl}/callback`
//   - Post sign-out URI:      `${baseUrl}/login`
// cookieSecret MUST be at least 32 characters (used to encrypt the session
// cookie) — generate one with `openssl rand -base64 32`.
export const logtoConfig: LogtoNextConfig = {
  endpoint: process.env.LOGTO_ENDPOINT ?? "",
  appId: process.env.LOGTO_APP_ID ?? "",
  appSecret: process.env.LOGTO_APP_SECRET ?? "",
  baseUrl: process.env.LOGTO_BASE_URL ?? APP_BASE_URL,
  cookieSecret:
    process.env.LOGTO_COOKIE_SECRET ?? "insecure_dev_cookie_secret_change_me_32chars",
  cookieSecure: process.env.NODE_ENV === "production",
  scopes: ["email", "profile", "roles"],
}
