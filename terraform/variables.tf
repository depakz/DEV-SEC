variable "service_name" {
  description = "Name of the Render web service."
  type        = string
  default     = "devsec"
}

variable "repo_url" {
  description = "GitHub repo Render builds from."
  type        = string
  default     = "https://github.com/depakz/DEV-SEC"
}

variable "branch" {
  description = "Git branch to deploy."
  type        = string
  default     = "main"
}

variable "plan" {
  description = "Render instance plan (free, starter, ...)."
  type        = string
  default     = "free"
}

variable "region" {
  description = "Render region."
  type        = string
  default     = "oregon"
}
