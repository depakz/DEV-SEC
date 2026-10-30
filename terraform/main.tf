# The whole app (React build + FastAPI) is one Docker web service built from
# the repo-root Dockerfile. Terraform owns the service definition; Jenkins
# triggers each deploy after tests and scans pass (auto_deploy is off so a
# plain `git push` does NOT bypass the pipeline).
resource "render_web_service" "app" {
  name   = var.service_name
  plan   = var.plan
  region = var.region

  runtime_source = {
    docker = {
      repo_url        = var.repo_url
      branch          = var.branch
      auto_deploy     = false
      dockerfile_path = "./Dockerfile"
    }
  }

  health_check_path = "/api/health"
}
