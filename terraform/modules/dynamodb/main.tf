# ====================
# Processing Metadata Table
# ====================

resource "aws_dynamodb_table" "tf_processing_metadata" {
  name         = local.processing_metadata_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "file_id"

  attribute {
    name = "file_id"
    type = "S"
  }

  tags = var.common_tags
}

# ====================
# Customer Data Table
# ====================

resource "aws_dynamodb_table" "tf_customers" {
  name         = local.customers_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "customer_id"

  attribute {
    name = "customer_id"
    type = "S"
  }

  tags = var.common_tags
}