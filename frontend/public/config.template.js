// Filled in by docker-entrypoint.sh at container *start* time (envsubst),
// not at build time. This is what lets the same image be deployed to any
// backend URL without rebuilding — Terraform sets BACKEND_URL as this
// container's env var, and it's substituted in here on boot.
window.__RUNTIME_CONFIG__ = {
  API_URL: "${BACKEND_URL}",
};
