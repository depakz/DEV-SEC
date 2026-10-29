output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "acr_login_server" {
  description = "Push images here from Jenkins: docker push <this>/backend:<tag>"
  value       = module.registry.login_server
}

output "backend_url" {
  value = module.container_apps.backend_url
}

output "frontend_url" {
  description = "Open this in a browser — the deployed Security Posture Scanner."
  value       = module.container_apps.frontend_url
}
