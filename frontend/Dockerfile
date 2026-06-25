# syntax=docker/dockerfile:1

# ---- Dependencies ----
# Installs node_modules in isolation so this layer is cached unless
# package.json / package-lock.json change.
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# ---- Builder ----
# Builds the Next.js app. API_HOST is NOT needed at build time anymore —
# it's read server-side at runtime by the API routes in app/api/**, since
# the browser no longer talks to the backend directly.
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# ---- Runner ----
# Minimal runtime image. Uses Next.js "standalone" output, which contains
# only the files needed to run the app (no full node_modules, no source).
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
