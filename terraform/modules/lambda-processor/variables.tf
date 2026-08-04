variable "processing_lambda_role_arn" {
  description = "IAM Role ARN for Processing Lambda"
  type        = string
}

variable "processing_queue_arn" {
  description = "SQS Processing Queue ARN"
  type        = string
}

variable "common_tags" {
  description = "Common resource tags"
  type        = map(string)
}