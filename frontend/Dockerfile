# Builder Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
# Initial install including dev dependencies
RUN npm ci

# Copy all files
COPY . .
# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Build the application
RUN npm run build

# Runner Stage
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create a non-root user for security (best practice)
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built assets
# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder /app/public ./public

# Set permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy necessary files for start
# Standalone build (preferred for Docker) is usually in .next/standalone
# But standard build needs package.json etc.
# Note: Next.js by default doesn't output standalone unless configured in next.config.js
# For simplicity, we use standard 'npm start' which requires node_modules (production only)

# Installing only production deps
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json
RUN npm ci --only=production

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
