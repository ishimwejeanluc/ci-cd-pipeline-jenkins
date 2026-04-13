output "inventory_path" {
  description = "Path to generated inventory file"
  value       = local_file.this.filename
}
