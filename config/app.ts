// App-level identity. Client-safe (no secrets). Override at deploy time via
// the NEXT_PUBLIC_APP_NAME env var so the same image rebrands per tenant.
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "Template"

export const APP_DESCRIPTION =
  "Template base para MVPs na stack à-la-carte da Cold Code Labs."

export const APP_VERSION = "0.1.0"
