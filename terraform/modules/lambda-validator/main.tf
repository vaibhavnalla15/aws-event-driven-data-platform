# ====================
# Archive Validation Lambda
# ====================

data "archive_file" "tf_validation_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda/validator"
  output_path = "${path.module}/validator.zip"
}

# ====================
# Validation Lambda
# ====================

resource "aws_lambda_function" "tf_validation_lambda" {
  function_name = local.validation_lambda_name

  role    = var.validation_lambda_role_arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.tf_validation_lambda_zip.output_path
  source_code_hash = data.archive_file.tf_validation_lambda_zip.output_base64sha256

  timeout     = 60
  memory_size = 256

  tags = var.common_tags
}

# ====================
# Lambda Permission
# ====================

resource "aws_lambda_permission" "tf_allow_s3_invoke_validation_lambda" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tf_validation_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.bucket_id
}

# ====================
# S3 Event Notification
# ====================

resource "aws_s3_bucket_notification" "tf_validation_lambda_trigger" {
  bucket = var.bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.tf_validation_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
  }

  depends_on = [
    aws_lambda_permission.tf_allow_s3_invoke_validation_lambda
  ]
}

# ====================
# CloudWatch Log Group
# ====================

resource "aws_cloudwatch_log_group" "tf_validation_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.tf_validation_lambda.function_name}"
  retention_in_days = 14

  tags = var.common_tags
}
