terraform {
  backend "s3" {
    bucket       = "tf-enterprise-data-processing-platform"
    key          = "enterprise-data-processing-platform/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}