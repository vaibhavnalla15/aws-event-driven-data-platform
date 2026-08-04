output "processing_metadata_table_name" {
  value = aws_dynamodb_table.tf_processing_metadata.name
}

output "processing_metadata_table_arn" {
  value = aws_dynamodb_table.tf_processing_metadata.arn
}

output "customers_table_name" {
  value = aws_dynamodb_table.tf_customers.name
}

output "customers_table_arn" {
  value = aws_dynamodb_table.tf_customers.arn
}