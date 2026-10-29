variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "container_env_id" {
  type = string
}

variable "container_env_default_domain" {
  description = "The Container Apps Environment's default domain, used to predict each app's FQDN before it's created (avoids a dependency cycle between backend and frontend)."
  type        = string
}

variable "acr_login_server" {
  type = string
}

variable "acr_username" {
  type = string
}

variable "acr_password" {
  type      = string
  sensitive = true
}

variable "backend_image_tag" {
  type = string
}

variable "frontend_image_tag" {
  type = string
}

variable "backend_cpu" {
  type = number
}

variable "backend_memory" {
  type = string
}

variable "frontend_cpu" {
  type = number
}

variable "frontend_memory" {
  type = string
}

variable "min_replicas" {
  type = number
}

variable "max_replicas" {
  type = number
}

variable "scanner_hmac_secret" {
  type      = string
  sensitive = true
}
