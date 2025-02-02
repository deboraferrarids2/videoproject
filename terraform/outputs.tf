output "eks_cluster_name" {
  description = "Nome do cluster EKS"
  value       = aws_eks_cluster.eks_cluster.name
}

output "s3_bucket_name" {
  description = "Nome do bucket S3"
  value       = aws_s3_bucket.app_bucket.id
}

output "rds_endpoint" {
  description = "Endpoint do banco de dados RDS"
  value       = aws_db_instance.rds.endpoint
  sensitive   = true
}
