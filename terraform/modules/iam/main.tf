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

# ====================
# Validation Lambda Policy
# ====================

data "aws_iam_policy_document" "tf_validation_lambda_policy_document" {

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${var.bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      var.processing_queue_arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sns:Publish"
    ]

    resources = [
      var.validation_topic_arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]

    resources = [
      var.processing_metadata_table_arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }
}

resource "aws_iam_policy" "tf_validation_lambda_policy" {
  name   = "tf-validation-lambda-policy"
  policy = data.aws_iam_policy_document.tf_validation_lambda_policy_document.json

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "tf_validation_lambda_policy_attachment" {
  role       = aws_iam_role.validation_lambda_role.name
  policy_arn = aws_iam_policy.tf_validation_lambda_policy.arn
}

# ====================
# Processing Lambda Policy
# ====================

data "aws_iam_policy_document" "tf_processing_lambda_policy_document" {

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${var.bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ChangeMessageVisibility"
    ]

    resources = [
      var.processing_queue_arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]

    resources = [
      var.processing_metadata_table_arn,
      var.customers_table_arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }
}

resource "aws_iam_policy" "tf_processing_lambda_policy" {
  name   = "tf-processing-lambda-policy"
  policy = data.aws_iam_policy_document.tf_processing_lambda_policy_document.json

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "tf_processing_lambda_policy_attachment" {
  role       = aws_iam_role.processing_lambda_role.name
  policy_arn = aws_iam_policy.tf_processing_lambda_policy.arn
}