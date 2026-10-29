# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------
resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location

  tags = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Container Registry (Jenkins pushes images here; Container Apps pull from it)
# -----------------------------------------------------------------------------
module "registry" {
  source              = "./modules/registry"
  project_name        = var.project_name
  environment         = var.environment
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

# -----------------------------------------------------------------------------
# Log Analytics — required by Container Apps Environment, also gives us
# a place to query container stdout/stderr without SSH-ing anywhere.
# -----------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "${var.project_name}-${var.environment}-logs"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "${var.project_name}-${var.environment}-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
}

# -----------------------------------------------------------------------------
# Backend + Frontend Container Apps
# -----------------------------------------------------------------------------
module "container_apps" {
  source = "./modules/container_apps"

  project_name                 = var.project_name
  environment                  = var.environment
  resource_group_name          = azurerm_resource_group.rg.name
  container_env_id             = azurerm_container_app_environment.env.id
  container_env_default_domain = azurerm_container_app_environment.env.default_domain

  acr_login_server = module.registry.login_server
  acr_username     = module.registry.admin_username
  acr_password     = module.registry.admin_password

  backend_image_tag  = var.backend_image_tag
  frontend_image_tag = var.frontend_image_tag
  backend_cpu        = var.backend_cpu
  backend_memory     = var.backend_memory
  frontend_cpu       = var.frontend_cpu
  frontend_memory    = var.frontend_memory
  min_replicas       = var.min_replicas
  max_replicas       = var.max_replicas

  scanner_hmac_secret = var.scanner_hmac_secret
}
