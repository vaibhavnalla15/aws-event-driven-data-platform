output "validation_topic_arn" {
  value = aws_sns_topic.tf_validation_topic.arn
}

output "validation_topic_name" {
  value = aws_sns_topic.tf_validation_topic.name
}