# --- deps stage ---
FROM node:20.16-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci --include=dev; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i; \
    elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    else npm install --production=false; fi

# --- build stage ---
FROM node:20.16-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN npm run build || (echo '--- NPM LOGS ---' && ls -la /root/.npm/_logs || true && exit 1)

# --- run stage ---
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
