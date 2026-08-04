# ====================
# Processing Dead Letter Queue
# ====================

resource "aws_sqs_queue" "tf_processing_dlq" {
  name = local.processing_dlq_name

  message_retention_seconds = 1209600

  tags = var.common_tags
}

# ====================
# Processing Queue
# ====================

resource "aws_sqs_queue" "tf_processing_queue" {
  name = local.processing_queue_name

  visibility_timeout_seconds = 300

  message_retention_seconds = 345600

  receive_wait_time_seconds = 20

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tf_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = var.common_tags
}