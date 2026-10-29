# Security Posture Scanner — DevOps Project Report

*(Convert this file to PDF once filled in — e.g. `pandoc report_template.md -o report.pdf`,
or paste into Word/Google Docs and export as PDF.)*

**Name:**
**Student ID:**
**Date:**

---

## 1. Objective

To design and build a stateless, web-based Security Posture Scanner — a tool
that checks a domain's TLS certificate, HTTP security headers, and DNS email
hygiene (SPF/DMARC/MX), with an ownership-verification flow that gates an
active port scan — and to deploy it on Microsoft Azure through a fully
automated Terraform + Jenkins + Docker pipeline triggered by `git push`.

## 2. Tools Used

| Tool | Purpose |
|---|---|
| Terraform | Infrastructure as Code — Resource Group, ACR, Container Apps Environment, Container Apps |
| Microsoft Azure | Hosts the Container Registry and the running backend/frontend containers |
| Jenkins | CI/CD orchestration — lint, test, security scan, build, push, deploy, verify |
| Docker | Packages the backend (FastAPI) and frontend (React/nginx) as images |
| GitHub | Version control + webhook/poll trigger source |
| FastAPI (Python) | Backend API — all checks, scoring, verification |
| React + Vite | Frontend single-page app |
| pytest / Vitest | Automated tests for backend and frontend |
| Bandit / pip-audit / Trivy | DevSecOps scans — static code, dependency, and container image |

## 3. Architecture Diagram

*(Insert the exported image here. Source/ASCII version: `docs/architecture.md`.)*

## 4. Infrastructure Provisioning (Terraform)

Briefly describe what each resource does in your own words, then paste the
relevant snippet.

### 4.1 Resource Group & Container Registry

```hcl
<!-- paste from terraform/main.tf and terraform/modules/registry/main.tf -->
```

### 4.2 Container Apps Environment (Log Analytics)

```hcl
<!-- paste from terraform/main.tf -->
```

### 4.3 Backend & Frontend Container Apps

```hcl
<!-- paste from terraform/modules/container_apps/main.tf -->
```

### 4.4 `terraform apply` result

*(Insert screenshot: terminal output ending in "Apply complete!" plus the
printed `frontend_url` / `backend_url` outputs.)*

## 5. Application Design

### 5.1 Stateless scanning

Explain, in your own words, why the app keeps no database and how the
frontend assembles the downloadable JSON report entirely client-side.

### 5.2 Ownership verification (for the port scan)

Explain the token design from `backend/app/verify.py`: how a signed,
time-limited token lets the server re-check a domain-ownership claim with
zero stored state, and why the signature alone isn't the proof of
ownership — the live DNS/file lookup is.

```python
<!-- paste the relevant parts of backend/app/verify.py -->
```

*(Insert screenshot: the frontend's verification panel showing the DNS TXT
record / well-known file instructions, then the "verified" state.)*

## 6. CI/CD Pipeline (Jenkins)

### 6.1 Pipeline stages

Describe each stage of the `Jenkinsfile` in your own words: Checkout,
Backend lint/test, Backend security scan (Bandit + pip-audit), Frontend
test/build, Docker build, Trivy image scan, push to ACR, Terraform apply,
Verify.

```groovy
<!-- paste the Jenkinsfile, or the most relevant stages -->
```

### 6.2 Triggering mechanism

State which trigger you used (GitHub webhook or Jenkins Poll SCM) and why.

### 6.3 Jenkins build success

*(Insert screenshot: the pipeline's stage view with all stages green.)*

### 6.4 DevSecOps scan output

*(Insert screenshot or paste output: Bandit report, pip-audit result, and
Trivy image scan summary.)*

## 7. Deployment Verification

### 7.1 Web application running on Azure

*(Insert screenshot: browser open at the `frontend_url` Terraform output,
showing a live scan result for a real domain.)*

### 7.2 Continuous deployment proof

*(Insert two screenshots: the app before a code change, and the app after
pushing the change and letting the pipeline redeploy automatically.)*

## 8. Observations

- What worked as expected?
- What had to be debugged, and how was it resolved?
- How long did the full pipeline take, end to end, from `git push` to the
  live app updating?

## 9. Conclusion

Summarize what the project demonstrated: a stateless, privacy-respecting
security tool, with ownership-gated active scanning, deployed through a
fully automated, repeatable DevSecOps pipeline triggered by nothing more
than a `git push`.

## Appendix: Source Code Repository

GitHub link: `https://github.com/<your-username>/<your-repo>`
