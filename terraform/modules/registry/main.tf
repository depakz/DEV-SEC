resource "random_string" "acr_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_container_registry" "acr" {
  # ACR names must be globally unique and alphanumeric only.
  name                = "${replace(var.project_name, "-", "")}${var.environment}acr${random_string.acr_suffix.result}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true # simplest auth path for a student project; a
  # real org would use a managed identity + AcrPull role instead of the
  # admin account.
}
