data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com"
      ]
    }

    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role" "validation_lambda_role" {
  name               = local.validation_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = var.common_tags
}

resource "aws_iam_role" "processing_lambda_role" {
  name               = local.processing_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = var.common_tags
}