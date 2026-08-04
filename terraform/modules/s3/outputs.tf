output "bucket_id" {
  value = aws_s3_bucket.tf_enterprise_data_bucket.id
}

output "bucket_arn" {
  value = aws_s3_bucket.tf_enterprise_data_bucket.arn
}

output "bucket_name" {
  value = aws_s3_bucket.tf_enterprise_data_bucket.bucket
}