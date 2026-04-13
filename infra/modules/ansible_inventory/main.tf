resource "local_file" "this" {
  filename = var.inventory_path
  content = templatefile(var.template_path, {
    public_ip        = var.public_ip
    ssh_user         = var.ssh_user
    private_key_path = var.private_key_path
  })
}
