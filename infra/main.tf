terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "devops-lab-123456"
    key            = "terraform.tfstate"
    region         = "us-west-1"
    dynamodb_table = "devops-lab-locks-123456"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  ssh_user         = "ec2-user"
  private_key_path = abspath("${path.module}/../ansible/${var.key_name}.pem")
  inventory_path   = abspath("${path.module}/../ansible/inventory.ini")
  inventory_tmpl   = abspath("${path.module}/../ansible/inventory.tmpl")
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "security_group" {
  source = "./modules/security_group"

  project_name     = var.project_name
  vpc_id           = data.aws_vpc.default.id
  allowed_ssh_cidr = var.allowed_ssh_cidr

  tags = {
    Name = "${var.project_name}-sg"
  }
}

module "key_pair" {
  source = "./modules/key_pair"

  key_name         = var.key_name
  private_key_path = local.private_key_path
}

module "web_server" {
  source = "./modules/ec2"

  instance_type               = var.instance_type
  key_name                    = module.key_pair.key_name
  security_group_ids          = [module.security_group.security_group_id]
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true


  tags = {
    Name = "${var.project_name}-web"
  }
}

module "ansible_inventory" {
  source = "./modules/ansible_inventory"

  template_path     = local.inventory_tmpl
  inventory_path    = local.inventory_path
  public_ip         = module.web_server.public_ip
  ssh_user          = local.ssh_user
  private_key_path  = module.key_pair.private_key_path
}


