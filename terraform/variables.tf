variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "cashflow-app"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "SSH key pair name for EC2 access"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into the instance (use YOUR_IP/32)"
  type        = string
  # no default - forces you to set your IP explicitly in terraform.tfvars
}

variable "docker_image" {
  description = "Docker image URI from ECR"
  type        = string
  default     = ""
}

variable "app_port" {
  description = "Container port exposed by the Flask app"
  type        = number
  default     = 5000
}

variable "db_host" {
  description = "Database host or endpoint"
  type        = string
  default     = "127.0.0.1"
}

variable "db_user" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "cashflow"
}

variable "secret_key" {
  description = "Flask secret key"
  type        = string
  sensitive   = true
}