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

variable "processing_dlq_url" {
  type = string
}

variable "processing_metadata_table_name" {
  description = "Processing metadata DynamoDB table name"
  type        = string
}

variable "customers_table_name" {
  description = "Customer DynamoDB table name"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}