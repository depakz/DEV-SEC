#!/bin/sh
# Runs once when the container starts, before nginx. Substitutes the
# BACKEND_URL env var (set by Terraform/Container Apps) into config.js,
# so the already-built static bundle can find the right API without a
# rebuild.
set -eu

: "${BACKEND_URL:=http://localhost:8000}"

envsubst '${BACKEND_URL}' < /usr/share/nginx/html/config.template.js \
    > /usr/share/nginx/html/config.js

exec "$@"
