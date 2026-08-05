# ====================
# Archive Processing Lambda
# ====================

data "archive_file" "tf_processing_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda/processor"
  output_path = "${path.module}/processor.zip"
}

# ====================
# Processing Lambda
# ====================

resource "aws_lambda_function" "tf_processing_lambda" {
  function_name = local.processing_lambda_name

  role    = var.processing_lambda_role_arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.tf_processing_lambda_zip.output_path
  source_code_hash = data.archive_file.tf_processing_lambda_zip.output_base64sha256

  timeout     = 60
  memory_size = 256

  environment {
    variables = {
      DLQ_URL                   = var.processing_dlq_url
      PROCESSING_METADATA_TABLE = var.processing_metadata_table_name
      CUSTOMERS_TABLE           = var.customers_table_name
      BUCKET_NAME               = var.bucket_name
    }
  }

  tags = var.common_tags
}

# ====================
# CloudWatch Log Group
# ====================

resource "aws_cloudwatch_log_group" "tf_processing_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.tf_processing_lambda.function_name}"
  retention_in_days = 14

  tags = var.common_tags
}

# ====================
# SQS Event Source Mapping
# ====================

resource "aws_lambda_event_source_mapping" "tf_processing_queue_trigger" {
  event_source_arn = var.processing_queue_arn
  function_name    = aws_lambda_function.tf_processing_lambda.arn

  batch_size = 10
  enabled    = true
}