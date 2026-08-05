# ====================
# SNS Topic
# ====================

resource "aws_sns_topic" "tf_validation_topic" {
  name = local.topic_name

  tags = var.common_tags
}

# ====================
# Email Subscription
# ====================

resource "aws_sns_topic_subscription" "tf_email_subscription" {
  topic_arn = aws_sns_topic.tf_validation_topic.arn
  protocol  = "email"
  endpoint  = var.notification_email
}