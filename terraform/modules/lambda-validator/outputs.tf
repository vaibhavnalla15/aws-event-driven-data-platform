output "validation_lambda_arn" {
  value = aws_lambda_function.tf_validation_lambda.arn
}

output "validation_lambda_name" {
  value = aws_lambda_function.tf_validation_lambda.function_name
}