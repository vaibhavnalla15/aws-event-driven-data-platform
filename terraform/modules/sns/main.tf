# ====================
# SNS Topic
# ====================

resource "aws_sns_topic" "tf_validation_topic" {
  name = local.topic_name

  tags = var.common_tags
}