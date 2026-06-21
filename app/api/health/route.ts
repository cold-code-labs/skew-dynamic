export const dynamic = "force-dynamic"

// Liveness probe for Coolify / load balancers.
export function GET() {
  return new Response("ok\n", {
    status: 200,
    headers: { "content-type": "text/plain; charset=utf-8" },
  })
}
