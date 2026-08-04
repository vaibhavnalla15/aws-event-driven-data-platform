variable "validation_lambda_name" {
  type = string
}

variable "processing_lambda_name" {
  type = string
}

variable "processing_queue_name" {
  type = string
}

variable "processing_dlq_name" {
  type = string
}

variable "validation_topic_arn" {
  type = string
}

variable "common_tags" {
  type = map(string)
}