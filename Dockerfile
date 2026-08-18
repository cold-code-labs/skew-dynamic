# skew-dynamic — build the Astro site, serve static via nginx
FROM node:22-alpine AS build
WORKDIR /app
COPY site/package.json site/pnpm-lock.yaml* ./site/
WORKDIR /app/site
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate && pnpm install --frozen-lockfile
WORKDIR /app
COPY site ./site
COPY study/docs ./study/docs
WORKDIR /app/site
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/site/dist /usr/share/nginx/html
COPY site/nginx.conf /etc/nginx/conf.d/default.conf
# ── Rodar sem root (Svalinn/semgrep missing-user, CWE-250) ───────────────────
# Verificado no surtr: o container tem net.ipv4.ip_unprivileged_port_start=0
# (default do Docker >= 20.10), entao o nginx BINDA a :80 como uid 101 — nao
# foi preciso trocar de porta nem remapear o Traefik. Testado em nginx:alpine:
# master E workers como `nginx`, GET / -> 200.
RUN chown -R nginx:nginx /var/cache/nginx /usr/share/nginx/html /etc/nginx/conf.d \
 && touch /var/run/nginx.pid && chown nginx:nginx /var/run/nginx.pid
USER nginx

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=4s --start-period=8s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
