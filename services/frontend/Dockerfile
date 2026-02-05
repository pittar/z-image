# Use the official Red Hat UBI 9 Nginx image
# This is pre-hardened and secure for OpenShift
FROM registry.access.redhat.com/ubi9/nginx-124:latest

# In UBI Nginx, the default web root is /opt/app-root/src
# We simply copy our single HTML file there.
COPY index.html /opt/app-root/src/index.html

# Expose port 8080 (Standard for UBI non-root containers)
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
