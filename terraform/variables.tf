variable "project_name" {
  description = "Short name used as a prefix for every resource (lowercase, no spaces)."
  type        = string
  default     = "secscan"
}

variable "location" {
  description = "Azure region to deploy into."
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Deployment environment tag (dev / staging / prod)."
  type        = string
  default     = "dev"
}

variable "backend_image_tag" {
  description = "Tag of the backend image in ACR to deploy (Jenkins pushes this, e.g. the Git commit SHA or build number)."
  type        = string
  default     = "latest"
}

variable "frontend_image_tag" {
  description = "Tag of the frontend image in ACR to deploy."
  type        = string
  default     = "latest"
}

variable "backend_cpu" {
  description = "vCPU allocated to the backend container app (Container Apps billing is pay-per-use, so keep this small)."
  type        = number
  default     = 0.25
}

variable "backend_memory" {
  description = "Memory allocated to the backend container app."
  type        = string
  default     = "0.5Gi"
}

variable "frontend_cpu" {
  type    = number
  default = 0.25
}

variable "frontend_memory" {
  type    = string
  default = "0.5Gi"
}

variable "min_replicas" {
  description = "Scale-to-zero when idle keeps this at $0 compute cost between demos."
  type        = number
  default     = 0
}

variable "max_replicas" {
  type    = number
  default = 2
}

variable "scanner_hmac_secret" {
  description = "Signing key for the ownership-verification tokens. Set via TF_VAR_scanner_hmac_secret or a CI secret — never committed."
  type        = string
  sensitive   = true
}
