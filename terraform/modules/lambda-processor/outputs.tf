output "processing_lambda_arn" {
  value = aws_lambda_function.tf_processing_lambda.arn
}

output "processing_lambda_name" {
  value = aws_lambda_function.tf_processing_lambda.function_name
}