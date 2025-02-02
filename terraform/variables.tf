variable "s3_bucket_name" {
  description = "Nome do bucket S3"
  type        = string
}

variable "availability_zone_1" {
  description = "Primeira zona de disponibilidade"
  type        = string
}

variable "availability_zone_2" {
  description = "Segunda zona de disponibilidade"
  type        = string
}

variable "eks_cluster_name" {
  description = "Nome do cluster EKS"
  type        = string
}

variable "rds_allocated_storage" {
  description = "Tamanho do armazenamento do RDS"
  type        = number
}

variable "rds_instance_class" {
  description = "Classe da instância do RDS"
  type        = string
}

variable "rds_username" {
  description = "Usuário do banco de dados RDS"
  type        = string
}

variable "rds_password" {
  description = "Senha do banco de dados RDS"
  type        = string
  sensitive   = true
}
