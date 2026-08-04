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

# ====================
# SQS
# ====================

output "processing_queue_url" {
  value = module.sqs.processing_queue_url
}

output "processing_queue_arn" {
  value = module.sqs.processing_queue_arn
}

output "processing_queue_name" {
  value = module.sqs.processing_queue_name
}

output "processing_dlq_url" {
  value = module.sqs.processing_dlq_url
}

output "processing_dlq_arn" {
  value = module.sqs.processing_dlq_arn
}

output "processing_dlq_name" {
  value = module.sqs.processing_dlq_name
}

# ====================
# DynamoDB
# ====================

output "processing_metadata_table_name" {
  value = module.dynamodb.processing_metadata_table_name
}

output "processing_metadata_table_arn" {
  value = module.dynamodb.processing_metadata_table_arn
}

output "customers_table_name" {
  value = module.dynamodb.customers_table_name
}

output "customers_table_arn" {
  value = module.dynamodb.customers_table_arn
}

# ====================
# Validation Lambda
# ====================

output "validation_lambda_arn" {
  value = module.lambda_validator.validation_lambda_arn
}

output "validation_lambda_name" {
  value = module.lambda_validator.validation_lambda_name
}

# ====================
# Processing Lambda
# ====================

output "processing_lambda_arn" {
  value = module.lambda_processor.processing_lambda_arn
}

output "processing_lambda_name" {
  value = module.lambda_processor.processing_lambda_name
}