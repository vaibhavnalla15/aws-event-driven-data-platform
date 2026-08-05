variable "common_tags" {
  description = "Common resource tags"
  type        = map(string)
}

variable "notification_email" {
  description = "Email address to receive SNS notifications"
  type        = string
}