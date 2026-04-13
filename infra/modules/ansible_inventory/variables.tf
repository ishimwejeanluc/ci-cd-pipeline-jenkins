variable "template_path" {
  description = "Absolute path to the inventory template"
  type        = string
}

variable "inventory_path" {
  description = "Absolute path where generated inventory will be written"
  type        = string
}

variable "public_ip" {
  description = "Public IP address of target host"
  type        = string
}

variable "ssh_user" {
  description = "SSH user used by Ansible"
  type        = string
}

variable "private_key_path" {
  description = "Absolute path to SSH private key file"
  type        = string
}
