// ─────────────────────────────────────────────────────────────────────────────
// BRAND — the single file you touch to reskin a new instance.
//
// Per-project, the only things you usually change are right here:
//   • name / tagline  → what shows in the sidebar + <title>
//   • logo            → initials text OR an image dropped in /public
//   • theme           → one of the presets in app/globals.css (color identity)
//
// All of it is client-safe (no secrets). `name` can also be overridden at
// deploy time via NEXT_PUBLIC_APP_NAME without editing this file.
// ─────────────────────────────────────────────────────────────────────────────

import type { CSSProperties } from "react"

import { APP_NAME } from "@/config/app"

/** Color presets defined in app/globals.css (`[data-theme="…"]`). */
export type ThemePreset =
  | "neutral"
  | "indigo"
  | "emerald"
  | "violet"
  | "amber"
  | "rose"

export const BRAND = {
  /** Display name. Falls back to APP_NAME (NEXT_PUBLIC_APP_NAME env or "Template"). */
  name: APP_NAME,

  /** Short line under the name in the sidebar header. */
  tagline: "Plataforma interna",

  /**
   * Logo. Leave `image` empty to use the lettermark (initials of `name` inside
   * a rounded square). Drop a file in /public and point `image` at it (e.g.
   * "/logo.svg") to use a real logo instead.
   */
  logo: {
    image: (process.env.NEXT_PUBLIC_BRAND_LOGO || "/logo.png") as string,
    /** Override the auto-derived initials if you want (e.g. "CCL"). */
    initials: "" as string,
  },

  /**
   * Color identity. Swap this single value to repaint the whole app — every
   * component reads from the design tokens this preset overrides. Can also be
   * set at deploy time via NEXT_PUBLIC_THEME.
   */
  theme: (process.env.NEXT_PUBLIC_THEME as ThemePreset) || "indigo",
} as const

/** Initials shown in the lettermark when no logo image is set. */
export function brandInitials(): string {
  if (BRAND.logo.initials) return BRAND.logo.initials
  return (
    BRAND.name
      .split(" ")
      .map((w) => w[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "AP"
  )
}

// ── Per-instance brand color ────────────────────────────────────────────────
// An exact color (NEXT_PUBLIC_BRAND_COLOR, set per Vessel by Ice Breaker) wins
// over the data-theme preset: it's applied as inline CSS custom properties on
// <html> in app/layout.tsx, and inline declarations beat any stylesheet rule,
// so it repaints --primary in both light and dark mode. Unset → presets apply
// as before.

function hexToRgb(hex: string): [number, number, number] | null {
  let h = hex.trim().replace(/^#/, "")
  if (/^[0-9a-fA-F]{3}$/.test(h)) {
    h = h
      .split("")
      .map((c) => c + c)
      .join("")
  }
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ]
}

/** Readable foreground (near-white or near-black) for a given background hex. */
function readableForeground(rgb: [number, number, number]): string {
  const [r, g, b] = rgb.map((v) => {
    const s = v / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  })
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
  return luminance > 0.45 ? "oklch(0.205 0 0)" : "oklch(0.985 0 0)"
}

/**
 * CSS custom properties to drop on <html> so an exact brand color repaints the
 * accent tokens. Returns undefined when NEXT_PUBLIC_BRAND_COLOR is unset or not
 * a valid hex — the data-theme preset then applies untouched.
 */
export function brandColorVars(): CSSProperties | undefined {
  const color = process.env.NEXT_PUBLIC_BRAND_COLOR
  if (!color) return undefined
  const rgb = hexToRgb(color)
  if (!rgb) return undefined
  const fg = readableForeground(rgb)
  return {
    "--primary": color,
    "--primary-foreground": fg,
    "--ring": color,
    "--sidebar-primary": color,
    "--sidebar-primary-foreground": fg,
    "--sidebar-ring": color,
  } as CSSProperties
}
