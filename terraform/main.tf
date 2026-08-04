# ====================
# IAM
# ====================

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment

  bucket_arn                    = module.s3.bucket_arn
  processing_queue_arn          = module.sqs.processing_queue_arn
  validation_topic_arn          = module.sns.validation_topic_arn
  processing_metadata_table_arn = module.dynamodb.processing_metadata_table_arn
  customers_table_arn           = module.dynamodb.customers_table_arn

  common_tags = local.common_tags
}

# ====================
# S3
# ====================

module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
  common_tags  = local.common_tags
}

# ====================
# SNS
# ====================

module "sns" {
  source = "./modules/sns"

  common_tags = local.common_tags
}

# ====================
# SQS
# ====================

module "sqs" {
  source = "./modules/sqs"

  common_tags = local.common_tags
}

# ====================
# DynamoDB
# ====================

module "dynamodb" {
  source = "./modules/dynamodb"

  common_tags = local.common_tags
}

# ====================
# Validation Lambda
# ====================

module "lambda_validator" {
  source = "./modules/lambda-validator"

  validation_lambda_role_arn = module.iam.validation_lambda_role_arn
  bucket_id                  = module.s3.bucket_id
  common_tags                = local.common_tags
}

# ====================
# Processing Lambda
# ====================

module "lambda_processor" {
  source = "./modules/lambda-processor"

  processing_lambda_role_arn = module.iam.processing_lambda_role_arn
  processing_queue_arn       = module.sqs.processing_queue_arn

  common_tags = local.common_tags
}

# ====================
# CloudWatch
# ====================

module "cloudwatch" {
  source = "./modules/cloudwatch"

  validation_lambda_name = module.lambda_validator.validation_lambda_name
  processing_lambda_name = module.lambda_processor.processing_lambda_name

  processing_queue_name = module.sqs.processing_queue_name
  processing_dlq_name   = module.sqs.processing_dlq_name

  validation_topic_arn = module.sns.validation_topic_arn

  common_tags = local.common_tags
}