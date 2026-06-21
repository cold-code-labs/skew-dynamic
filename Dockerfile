# syntax=docker/dockerfile:1
# "Light" tier image: the Next.js template app + a bundled PocketBase backend in
# a single container. Coolify builds this (build_pack=dockerfile) and runs it as
# a web service on port 3000 — the wildcard `*.coldcodelabs.com` route points
# straight at it. PocketBase runs internally on 127.0.0.1:8090 (data-only); all
# state lives in /pb_data, which MUST be a persistent volume.

FROM node:22-alpine AS base
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable

# ── deps ──────────────────────────────────────────────────────────────────────
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ── build (Next.js standalone) ─────────────────────────────────────────────────
FROM base AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# ── fetch PocketBase binary ────────────────────────────────────────────────────
FROM alpine:3.20 AS pbfetch
ARG PB_VERSION=0.39.3
ARG PB_ARCH=amd64
RUN apk add --no-cache unzip wget ca-certificates
WORKDIR /pb
RUN wget -q "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_${PB_ARCH}.zip" -O /tmp/pb.zip \
 && unzip /tmp/pb.zip -d /pb \
 && rm /tmp/pb.zip

# ── runner (Next.js + PocketBase) ──────────────────────────────────────────────
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
# The app talks to the bundled PocketBase over localhost.
ENV POCKETBASE_URL=http://127.0.0.1:8090

RUN apk add --no-cache ca-certificates wget tini

# Next.js standalone server output.
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static

# PocketBase binary + the app's schema/hooks (replayed onto a fresh /pb_data).
COPY --from=pbfetch /pb/pocketbase /usr/local/bin/pocketbase
COPY pocketbase/pb_migrations /pb/pb_migrations
COPY pocketbase/pb_hooks /pb/pb_hooks
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/pocketbase /usr/local/bin/docker-entrypoint.sh

# Runs as root so PocketBase can write to the /pb_data volume mount.
EXPOSE 3000

# Healthcheck hits the APP's /api/health (PocketBase is internal).
HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1

ENTRYPOINT ["tini", "--", "docker-entrypoint.sh"]
