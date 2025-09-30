variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"  # Using us-east-1 as it typically has better free tier eligibility
}

variable "key_pair_name" {
  description = "Name of the AWS key pair to use for SSH access"
  type        = string
}
