output "processing_queue_url" {
  value = aws_sqs_queue.tf_processing_queue.url
}

output "processing_queue_arn" {
  value = aws_sqs_queue.tf_processing_queue.arn
}

output "processing_queue_name" {
  value = aws_sqs_queue.tf_processing_queue.name
}

output "processing_dlq_url" {
  value = aws_sqs_queue.tf_processing_dlq.url
}

output "processing_dlq_arn" {
  value = aws_sqs_queue.tf_processing_dlq.arn
}

output "processing_dlq_name" {
  value = aws_sqs_queue.tf_processing_dlq.name
}