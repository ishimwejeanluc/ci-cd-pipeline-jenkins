variable "key_name" {
  description = "Name of the EC2 key pair to create"
  type        = string
  default = "devops-lab"
}

variable "private_key_path" {
  description = "Absolute path where the generated private key will be saved"
  type        = string
}
