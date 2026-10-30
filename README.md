# Security Posture Scanner

A stateless web app that checks a domain's TLS certificate, HTTP security
headers, and DNS email hygiene (SPF/DMARC/MX), plus an active port scan.
Built as a DevOps capstone: Terraform defines the Render service, Jenkins
tests/scans/deploys on every change, Docker packages the app.

**No database, no login, no persistence.** Every scan result lives only in
the browser tab that ran it; the "report" is a JSON file you download.

## Repository layout

```
backend/            FastAPI app: checks, scoring + tests
frontend/           React (Vite) UI
Dockerfile          Single image: builds the frontend, FastAPI serves it (used on Render)
terraform/          Render web service definition (render-oss/render provider)
Jenkinsfile         CI/CD: lint/test -> Bandit/pip-audit -> Docker build -> Trivy -> terraform validate -> Render deploy -> smoke test
jenkins/            Dockerfile + compose for a local Jenkins with all required tools
docker-compose.yml  Local dev stack (separate backend/frontend containers)
docs/               Architecture + report template
```

## Run locally

```bash
docker build -t devsec . && docker run -p 8000:8000 devsec   # http://localhost:8000
```

## CI/CD flow

`git push` -> Jenkins (webhook or poll) -> lint, tests, Bandit, pip-audit,
npm audit -> Docker build -> Trivy -> `terraform validate` -> call Render's
deploy API -> wait until live -> `curl /api/health`.

Render's **Auto-Deploy is off** (see `terraform/main.tf`), so a push alone
never deploys: only a green Jenkins run does.

## 1. Provision the Render service with Terraform

```bash
export RENDER_API_KEY=rnd_xxx        # Render > Account Settings > API Keys
export RENDER_OWNER_ID=tea-xxx       # Render workspace id
cd terraform
terraform init
terraform apply
terraform output service_id          # srv-xxxx
terraform output service_url         # https://devsec.onrender.com
```

(If you already created the service in the Render UI, either run
`terraform import render_web_service.app srv-xxxx` or just turn Auto-Deploy off
in its Settings and skip this step.)

## 2. Run Jenkins locally

```bash
docker compose -f jenkins/docker-compose.yml up -d --build
docker logs devsec-jenkins            # initial admin password; UI on http://localhost:8080
```

Add three **Secret text** credentials (Manage Jenkins > Credentials):

| ID | Value |
|---|---|
| `render-api-key` | your Render API key |
| `render-service-id` | `srv-xxxx` from step 1 |
| `render-service-url` | the service URL, no trailing slash |

Create a **Pipeline** job: "Pipeline script from SCM", Git,
`https://github.com/depakz/DEV-SEC.git`, branch `main`, script path `Jenkinsfile`.

## 3. Prove continuous deployment

1. Change something visible (e.g. a heading in `frontend/src/App.jsx`), commit, push.
2. Jenkins picks it up (or click **Build Now**); watch the stage view go green.
3. The "Deploy to Render" stage logs `Triggered Render deploy ...` and `Deploy status: live`.
4. Reload the Render URL and see the change. Screenshot: Jenkins stage view, Render
   Events/Deploys tab (trigger shows as API), and the updated site.

## Troubleshooting

- **Deploy stage 401/404:** wrong `render-api-key` or `render-service-id`.
- **Trivy fails the build:** a HIGH/CRITICAL CVE in the base image; bump the base tag.
- **Smoke test times out:** free instances sleep; the stage retries for ~2 minutes.
