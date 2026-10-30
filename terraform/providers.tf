terraform {
  required_version = ">= 1.5.0"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }
}

provider "render" {
  # Auth comes from the environment (never committed):
  #   RENDER_API_KEY   - Render dashboard > Account Settings > API Keys
  #   RENDER_OWNER_ID  - the workspace id (starts with tea- or usr-)
}
