# ----------------------------------------------------------------------------
# Stage 1: Builder (Node.js 20 on UBI 9)
# ----------------------------------------------------------------------------
FROM registry.access.redhat.com/ubi9/nodejs-20:latest AS builder

# Switch to root to ensure we have write permissions for the build setup
# (The UBI Node image drops to a default user, but root is safer for the build phase)
USER 0
WORKDIR /opt/app-root/src

# 1. Copy package files first to leverage Docker caching
COPY package.json package-lock.json ./

# 2. Install Dependencies
# We use 'npm ci' (Clean Install). It respects the lockfile.
# Importantly, we do NOT set NODE_ENV=production here, 
# so 'devDependencies' (like Vite) are installed.
RUN npm ci

# 3. Copy the rest of the source code
COPY . .

# 4. Build the application
# This runs "vite build" and generates the 'dist' folder
RUN npm run build

# ----------------------------------------------------------------------------
# Stage 2: Runtime (Nginx 1.24 on UBI 9)
# ----------------------------------------------------------------------------
FROM registry.access.redhat.com/ubi9/nginx-124:latest

# 5. Copy the static build output from Stage 1
# UBI Nginx expects files in /opt/app-root/src
COPY --from=builder /opt/app-root/src/dist /opt/app-root/src

# 6. Copy our custom Nginx configuration
# UBI Nginx loads configs from /opt/app-root/etc/nginx.d/
COPY nginx.conf /opt/app-root/etc/nginx.d/default.conf

# 7. Expose port 8080 (Standard for non-root UBI containers)
EXPOSE 8080

# 8. Start Nginx
CMD ["nginx", "-g", "daemon off;"]
