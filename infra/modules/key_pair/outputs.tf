output "key_name" {
  description = "Name of the created EC2 key pair"
  value       = aws_key_pair.this.key_name
}

output "private_key_path" {
  description = "Path to generated private key file"
  value       = var.private_key_path
}
