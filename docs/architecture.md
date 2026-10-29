# Architecture — Security Posture Scanner

```
                     GitHub repo (backend/ + frontend/ + terraform/ + Jenkinsfile)
                               |
                               | push / webhook (or Jenkins Poll SCM every 2 min)
                               v
                    +----------------------+
                    |       Jenkins        |
                    | 1. Checkout          |
                    | 2. Backend: lint+test|
                    | 3. Backend: Bandit,  |
                    |    pip-audit         |
                    | 4. Frontend: test+build
                    | 5. docker build (x2) |
                    | 6. Trivy image scan  |
                    | 7. push to ACR       |
                    | 8. terraform apply   |----------------+
                    | 9. Verify (curl)     |                |
                    +----------------------+                |
                                                              v
                                         +----------------------------------------+
                                         |            Microsoft Azure             |
                                         |  Resource Group                        |
                                         |   +-- Azure Container Registry (ACR)   |
                                         |   +-- Log Analytics Workspace          |
                                         |   +-- Container Apps Environment       |
                                         |        +-- backend  (FastAPI, :8000)   |
                                         |        +-- frontend (React/nginx, :80) |
                                         +----------------------------------------+
                                                              ^
                                                              | HTTPS
                                                         End user / browser
```

## Request flow (passive scan)

1. User opens the frontend (static React app served by nginx) and types a domain.
2. The browser calls `POST /api/scan/passive` on the backend.
3. The backend validates the domain (syntax + resolves to a public IP only —
   see `backend/app/domain_utils.py`), then runs the TLS, header and DNS
   checks concurrently and returns a scored JSON result.
4. The frontend renders the result and assembles a downloadable JSON report
   client-side. **Nothing is written to a database anywhere in this flow** —
   the service is stateless by design.

## Request flow (active port scan, gated)

1. User requests a verification token: `POST /api/verify/start`.
2. The backend mints a signed, time-limited token bound to that domain
   (see `backend/app/verify.py`) and returns it along with two ways to
   publish it (a DNS TXT record, or a file under `/.well-known/`).
3. User publishes the token somewhere only the domain's real owner could.
4. User calls `POST /api/verify/check` — the backend re-derives and checks
   the signature, then does a *live* DNS/HTTP lookup to confirm the token
   is actually published.
5. Only if that succeeds does `POST /api/scan/ports` run — and it
   re-verifies from scratch every single time, since nothing is cached.

## Why Terraform provisions Container Apps, not a VM

Both the backend and frontend are already packaged as Docker images (see
`backend/Dockerfile`, `frontend/Dockerfile`). Azure Container Apps runs
those images directly, scales to zero when idle (near-$0 between demos),
and needs no OS patching, SSH keys, or systemd units — Jenkins only ever
pushes a new image tag and re-applies Terraform with it.

For the project report, redraw the ASCII diagram above as a boxes-and-arrows
diagram (draw.io, Lucidchart, or PowerPoint), export it as an image, and
drop it into the report in place of this version.
