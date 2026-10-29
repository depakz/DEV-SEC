# Security Posture Scanner

A stateless web app that checks a domain's TLS certificate, HTTP security
headers, and DNS email hygiene (SPF/DMARC/MX) — plus a gated active port
scan that only runs after you prove you own the domain. Built as a DevOps
capstone: Terraform provisions Azure, Jenkins builds/tests/scans/deploys on
every push, Docker packages both halves of the app.

**No database, no login, no persistence.** Every scan result lives only in
the browser tab that ran it; the "report" is a JSON file you download, not
something stored on the server.

## Repository layout

```
backend/            FastAPI app: checks, scoring + tests
frontend/            React (Vite) single-page app + tests
terraform/           Azure Container Registry + Container Apps Environment + 2 Container Apps
Jenkinsfile          CI/CD: lint/test -> Bandit/pip-audit -> Docker build -> Trivy scan -> push ACR -> terraform apply -> smoke test
docker-compose.yml   Local dev/demo stack (not used for the Azure deploy)
scripts/deploy.sh    One-time setup of the Terraform remote-state storage account
docs/                Architecture notes + the project report template
```

## Run it locally

```bash
docker compose up --build
# frontend: http://localhost:8081   backend: http://localhost:8010
```

Or without Docker:

```bash
# backend
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, talks to the backend on :8000
```

## Run the tests

```bash
cd backend && . .venv/bin/activate && pytest -q      # 36 tests
cd frontend && npm test                               # vitest
```

## Prerequisites for the Azure deployment

- An Azure subscription (Azure for Students works) + the Azure CLI, `az login` done once locally
- Terraform >= 1.5
- Docker, to build the two images
- A Jenkins instance with the Git, Pipeline, Docker and Credentials plugins
- An Azure Service Principal for Terraform/Jenkins:
  `az ad sp create-for-rbac --role Contributor --scopes /subscriptions/<sub-id>`

## 1. Bootstrap Terraform's remote state (one-time)

```bash
cd scripts
./deploy.sh eastus
# follow the printed instructions to fill in terraform/providers.tf's backend block
```

## 2. Provision + deploy manually (first run, before Jenkins exists)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit project_name/location as needed
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

**Screenshot this for the report**: the end of `terraform apply` showing
`Apply complete!` and the printed `frontend_url` / `backend_url` outputs.

Build and push the images once by hand so the Container Apps have
something to pull on the very first apply (afterwards Jenkins does this):

```bash
ACR=$(terraform output -raw acr_login_server)
az acr login --name "${ACR%%.*}"
docker build -t "$ACR/backend:latest" ../backend
docker build -t "$ACR/frontend:latest" --build-arg VITE_API_URL="https://$(terraform output -raw backend_url | sed 's#https://##')" ../frontend
docker push "$ACR/backend:latest"
docker push "$ACR/frontend:latest"
terraform apply -auto-approve   # picks up the now-existing images
```

## 3. Push this repo to GitHub

```bash
git init
git add .
git commit -m "Security Posture Scanner: FastAPI + React + Terraform + Jenkins"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 4. Set up Jenkins

1. Install plugins: Git, Pipeline, Docker Pipeline, Credentials Binding.
2. Add credentials (Manage Jenkins → Credentials):
   - `azure-sp` — Username/Password: the Service Principal's `appId` / `password`
   - `azure-subscription-id`, `azure-tenant-id` — Secret text
   - `acr-credentials` — Username/Password: `az acr credential show --name <acr>`
   - `acr-login-server` — Secret text: the ACR login server hostname
3. New Item → Pipeline → "Pipeline script from SCM" → Git → your repo URL →
   Script Path: `Jenkinsfile`.
4. Trigger: GitHub webhook to `<jenkins-url>/github-webhook/`, or rely on
   the `pollSCM('H/2 * * * *')` fallback already in the Jenkinsfile.
5. Click **Build Now** once to confirm the full pipeline runs end to end.

**Screenshot this for the report**: the Jenkins stage view, all green, and
the console output tail showing the deployed `frontend_url`.

## 5. Confirm continuous deployment

Make a small change (e.g. a label in `frontend/src/App.jsx`), commit, push.
Within the poll interval (≤2 min) or webhook delay, Jenkins should rebuild,
re-scan, and redeploy automatically.

## 6. Tear down (avoid ongoing Azure charges)

```bash
cd terraform
terraform destroy
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `terraform apply` fails creating the Container App | The images don't exist in ACR yet — do the manual build+push in step 2 first |
| ACR name already taken | `project_name` collided; change it or rerun (a random suffix is appended) |
| `pip-audit`/`bandit`/`trivy` fail the build | A real finding — fix the dependency/code/image, don't suppress it |

## What each deliverable maps to

| Deliverable | Where it comes from |
|---|---|
| Architecture diagram | `docs/architecture.md` (redraw as an image for the report) |
| Terraform code snippets | `terraform/*.tf`, `terraform/modules/**/*.tf` |
| Jenkinsfile / pipeline config | `Jenkinsfile` |
| Screenshots | Captured while following steps 1–5 above |
| Report | `docs/report_template.md` |
