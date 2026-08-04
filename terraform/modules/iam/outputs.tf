output "validation_lambda_role_arn" {
  value = aws_iam_role.validation_lambda_role.arn
}

output "validation_lambda_role_name" {
  value = aws_iam_role.validation_lambda_role.name
}

output "processing_lambda_role_arn" {
  value = aws_iam_role.processing_lambda_role.arn
}

output "processing_lambda_role_name" {
  value = aws_iam_role.processing_lambda_role.name
}