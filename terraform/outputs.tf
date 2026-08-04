# ====================
# IAM
# ====================

output "validation_lambda_role_arn" {
  value = module.iam.validation_lambda_role_arn
}

output "validation_lambda_role_name" {
  value = module.iam.validation_lambda_role_name
}

output "processing_lambda_role_arn" {
  value = module.iam.processing_lambda_role_arn
}

output "processing_lambda_role_name" {
  value = module.iam.processing_lambda_role_name
}

# ====================
# S3
# ====================

output "s3_bucket_id" {
  value = module.s3.bucket_id
}

output "s3_bucket_arn" {
  value = module.s3.bucket_arn
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}

# ====================
# SNS
# ====================

output "validation_topic_arn" {
  value = module.sns.validation_topic_arn
}

output "validation_topic_name" {
  value = module.sns.validation_topic_name
}