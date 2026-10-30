# Architecture — Security Posture Scanner

```
   developer --git push--> GitHub (backend/ frontend/ terraform/ Jenkinsfile)
                               |
                               | webhook / poll SCM
                               v
                   +------------------------+
                   |        Jenkins         |
                   | 1. checkout            |
                   | 2. lint + tests        |
                   | 3. bandit / pip-audit  |
                   | 4. docker build        |
                   | 5. trivy scan          |
                   | 6. terraform validate  |
                   | 7. Render deploy API   |-----> Render web service (Docker)
                   | 8. smoke test          |<----- GET /api/health
                   +------------------------+
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

## Request flow (active port scan)

1. User clicks "Run port scan" for the scanned domain: `POST /api/scan/ports`.
2. The backend resolves the domain, rejects non-public addresses, and probes a short list of well-known TCP ports.

## Why one Docker service on Render

The root `Dockerfile` builds the React app and copies it into the FastAPI
image, which serves both `/api/*` and the static UI from one origin (no CORS,
no second service). Terraform (`terraform/main.tf`) defines that service with
Auto-Deploy off; Jenkins triggers each deploy through Render's API only after
tests and scans pass.
