variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "common_tags" {
  description = "Common resource tags"
  type        = map(string)
}

variable "bucket_arn" {
  type = string
}

variable "processing_queue_arn" {
  type = string
}

variable "validation_topic_arn" {
  type = string
}

variable "processing_metadata_table_arn" {
  type = string
}

variable "customers_table_arn" {
  type = string
}