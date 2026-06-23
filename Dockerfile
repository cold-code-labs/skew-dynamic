# skew-dynamic — build the Astro site, serve static via nginx
FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable
COPY site/package.json site/pnpm-lock.yaml* ./site/
WORKDIR /app/site
RUN pnpm install --no-frozen-lockfile
WORKDIR /app
COPY site ./site
COPY study/docs ./study/docs
WORKDIR /app/site
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/site/dist /usr/share/nginx/html
COPY site/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=4s --start-period=8s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
