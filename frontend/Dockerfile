"""Multi-stage Dockerfile for DataMind-King frontend.

Targets ≤150MB using node:20-alpine → build → nginx:alpine.
"""

# --- Build stage ---
FROM node:20-alpine AS builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY frontend .
RUN pnpm build

# --- Runtime stage ---
FROM nginx:alpine AS runtime

RUN rm -rf /etc/nginx/conf.d/default.conf
COPY infra/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/frontend/.next /usr/share/nginx/html
COPY --from=builder /app/frontend/public /usr/share/nginx/html/public

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
