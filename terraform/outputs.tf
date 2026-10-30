output "service_id" {
  description = "Put this in the Jenkins credential 'render-service-id'."
  value       = render_web_service.app.id
}

output "service_url" {
  description = "The deployed Security Posture Scanner."
  value       = render_web_service.app.url
}
