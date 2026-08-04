variable "validation_lambda_role_arn" {
  description = "Validation Lambda IAM Role ARN"
  type        = string
}

variable "common_tags" {
  description = "Common resource tags"
  type        = map(string)
}

variable "bucket_id" {
  description = "S3 bucket ID"
  type        = string
}