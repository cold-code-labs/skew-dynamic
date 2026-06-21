/** @type {import('next').NextConfig} */

// Security headers (parity with a typical nginx/vercel.json baseline). A strict
// script-src CSP needs per-request nonces with Next's streaming renderer, so it
// is intentionally left out of the template — add it behind a nonce middleware
// when the app's script surface is known.
const securityHeaders = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    // `microphone=(self)` lets the Reuniões Gravadas recorder use getUserMedia
    // on this origin (it is blocked entirely by `microphone=()`). Camera and
    // geolocation stay off — widen them only when a feature needs them.
    key: "Permissions-Policy",
    value: "camera=(), microphone=(self), geolocation=()",
  },
]

const nextConfig = {
  // Self-contained server build for Docker/Coolify (emits .next/standalone).
  output: "standalone",
  // No next/image optimizer in the container (keeps the image sharp-free).
  images: { unoptimized: true },
  // Server Actions default to a 1MB body cap; recorded-meeting audio (and large
  // file uploads) need more. 32MB sits above the 25MB OpenAI Whisper limit.
  experimental: { serverActions: { bodySizeLimit: "32mb" } },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }]
  },
}

export default nextConfig
