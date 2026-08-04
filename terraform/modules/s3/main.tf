resource "aws_s3_bucket" "tf_enterprise_data_bucket" {
  bucket = local.bucket_name

  tags = var.common_tags
}

resource "aws_s3_bucket_versioning" "tf_enterprise_data_bucket_versioning" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tf_enterprise_data_bucket_encryption" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tf_enterprise_data_bucket_public_access" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# ====================
# S3 Folder Structure
# ====================

resource "aws_s3_object" "tf_incoming_folder" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id
  key    = "incoming/"
}

resource "aws_s3_object" "tf_processed_folder" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id
  key    = "processed/"
}

resource "aws_s3_object" "tf_failed_folder" {
  bucket = aws_s3_bucket.tf_enterprise_data_bucket.id
  key    = "failed/"
}