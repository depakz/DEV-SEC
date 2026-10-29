locals {
  # Computed up front, rather than read back from each resource's `ingress`
  # block, specifically to avoid the two container apps needing to depend
  # on each other (backend needs frontend's URL for CORS; frontend needs
  # backend's URL to call it) — Azure Container Apps FQDNs are always
  # "<app-name>.<environment's default_domain>", so both can be derived
  # from just the (statically known) names and the environment, breaking
  # what would otherwise be a dependency cycle.
  backend_name  = "${var.project_name}-${var.environment}-backend"
  frontend_name = "${var.project_name}-${var.environment}-frontend"
  backend_url   = "https://${local.backend_name}.${var.container_env_default_domain}"
  frontend_url  = "https://${local.frontend_name}.${var.container_env_default_domain}"
}

resource "azurerm_container_app" "backend" {
  name                         = local.backend_name
  container_app_environment_id = var.container_env_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  secret {
    name  = "registry-password"
    value = var.acr_password
  }

  secret {
    name  = "hmac-secret"
    value = var.scanner_hmac_secret
  }

  registry {
    server               = var.acr_login_server
    username             = var.acr_username
    password_secret_name = "registry-password"
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "backend"
      image  = "${var.acr_login_server}/backend:${var.backend_image_tag}"
      cpu    = var.backend_cpu
      memory = var.backend_memory

      env {
        name        = "SCANNER_HMAC_SECRET"
        secret_name = "hmac-secret"
      }

      env {
        name  = "ALLOWED_ORIGINS"
        value = local.frontend_url
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}

resource "azurerm_container_app" "frontend" {
  name                         = local.frontend_name
  container_app_environment_id = var.container_env_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  secret {
    name  = "registry-password"
    value = var.acr_password
  }

  registry {
    server               = var.acr_login_server
    username             = var.acr_username
    password_secret_name = "registry-password"
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "frontend"
      image  = "${var.acr_login_server}/frontend:${var.frontend_image_tag}"
      cpu    = var.frontend_cpu
      memory = var.frontend_memory

      env {
        name  = "BACKEND_URL"
        value = local.backend_url
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 80
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}
