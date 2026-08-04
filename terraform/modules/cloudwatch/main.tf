# ====================
# CloudWatch Dashboard
# ====================

resource "aws_cloudwatch_dashboard" "tf_enterprise_dashboard" {
  dashboard_name = local.dashboard_name

  dashboard_body = jsonencode({
    widgets = [

      # ====================
      # Validation Lambda Invocations
      # ====================

      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "Validation Lambda - Invocations"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Sum"
          period = 300

          metrics = [
            [
              "AWS/Lambda",
              "Invocations",
              "FunctionName",
              var.validation_lambda_name
            ]
          ]
        }
      },

      # ====================
      # Validation Lambda Errors
      # ====================

      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "Validation Lambda - Errors"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Sum"
          period = 300

          metrics = [
            [
              "AWS/Lambda",
              "Errors",
              "FunctionName",
              var.validation_lambda_name
            ]
          ]
        }
      },

      # ====================
      # Processing Lambda Invocations
      # ====================

      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          title  = "Processing Lambda - Invocations"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Sum"
          period = 300

          metrics = [
            [
              "AWS/Lambda",
              "Invocations",
              "FunctionName",
              var.processing_lambda_name
            ]
          ]
        }
      },

      # ====================
      # Processing Lambda Errors
      # ====================

      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          title  = "Processing Lambda - Errors"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Sum"
          period = 300

          metrics = [
            [
              "AWS/Lambda",
              "Errors",
              "FunctionName",
              var.processing_lambda_name
            ]
          ]
        }
      },

      # ====================
      # Processing Queue
      # ====================

      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6

        properties = {
          title  = "Processing Queue Messages"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Average"
          period = 300

          metrics = [
            [
              "AWS/SQS",
              "ApproximateNumberOfMessagesVisible",
              "QueueName",
              var.processing_queue_name
            ]
          ]
        }
      },

      # ====================
      # Dead Letter Queue
      # ====================

      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6

        properties = {
          title  = "Dead Letter Queue Messages"
          view   = "timeSeries"
          region = "us-east-1"
          stat   = "Average"
          period = 300

          metrics = [
            [
              "AWS/SQS",
              "ApproximateNumberOfMessagesVisible",
              "QueueName",
              var.processing_dlq_name
            ]
          ]
        }
      }
    ]
  })
}

# ====================
# Validation Lambda Error Alarm
# ====================

resource "aws_cloudwatch_metric_alarm" "tf_validation_lambda_errors" {
  alarm_name          = "tf-validation-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1

  dimensions = {
    FunctionName = var.validation_lambda_name
  }

  alarm_actions = [
    var.validation_topic_arn
  ]
}

# ====================
# Processing Lambda Error Alarm
# ====================

resource "aws_cloudwatch_metric_alarm" "tf_processing_lambda_errors" {
  alarm_name          = "tf-processing-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1

  dimensions = {
    FunctionName = var.processing_lambda_name
  }

  alarm_actions = [
    var.validation_topic_arn
  ]
}

# ====================
# Processing Queue Backlog Alarm
# ====================

resource "aws_cloudwatch_metric_alarm" "tf_processing_queue_backlog" {
  alarm_name          = "tf-processing-queue-backlog"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 10

  dimensions = {
    QueueName = var.processing_queue_name
  }

  alarm_actions = [
    var.validation_topic_arn
  ]
}

# ====================
# Dead Letter Queue Alarm
# ====================

resource "aws_cloudwatch_metric_alarm" "tf_processing_dlq_messages" {
  alarm_name          = "tf-processing-dlq-messages"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 1

  dimensions = {
    QueueName = var.processing_dlq_name
  }

  alarm_actions = [
    var.validation_topic_arn
  ]
}