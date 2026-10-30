// Thin wrapper around the backend API. Nothing here persists anything —
// no localStorage, no cookies, no IndexedDB. Each function is a one-shot
// request/response pair.

// Checked in this order: runtime config injected by the container at
// startup (production), then a build-time env var (local `vite build`),
// then a plain localhost fallback (local `vite dev`).
const BASE_URL =
  (typeof window !== "undefined" && window.__RUNTIME_CONFIG__?.API_URL) ||
  (import.meta.env.VITE_API_URL ?? "http://localhost:8000");

async function postJSON(path, body) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request to ${path} failed (${response.status})`);
  }
  return data;
}

export const scanPassive = (domain) => postJSON("/api/scan/passive", { domain });
export const scanPorts = (domain) => postJSON("/api/scan/ports", { domain });
