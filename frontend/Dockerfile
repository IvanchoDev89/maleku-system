# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --only=production || npm install --prefer-offline

# Copy source code
COPY . .

# Build the application
RUN npm run build


# Stage 2: Production
FROM node:20-alpine AS production

WORKDIR /app

# Security: Create non-root user
RUN addgroup -g 1001 nodegroup && \
    adduser -S -u 1001 -G nodegroup nodeuser

# Create directories
RUN mkdir -p /app/.output /app/node_modules /app/public

# Copy built artifacts
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Static files (if any)
COPY public ./public

# Security: Set ownership
RUN chown -R nodeuser:nodegroup /app

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/v1/health || exit 1

# Switch to non-root user
USER nodeuser

# Run the application
CMD ["node", ".output/server/index.mjs"]
