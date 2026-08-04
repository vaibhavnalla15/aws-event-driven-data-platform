# ====================
# IAM
# ====================

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  common_tags  = local.common_tags
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