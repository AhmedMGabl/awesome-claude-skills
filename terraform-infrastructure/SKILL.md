---
name: terraform-infrastructure
description: Terraform infrastructure as code covering providers, modules, state management, workspaces, AWS/GCP/Azure resources, remote backends, and production-ready IaC patterns.
---

# Terraform Infrastructure

This skill should be used when the user needs to provision, manage, or organize cloud infrastructure using Terraform. It covers writing HCL configurations, managing state, building reusable modules, multi-environment setups, and production-ready infrastructure patterns for AWS, GCP, and Azure.

## When to Use This Skill

Use this skill when you need to:

- Write Terraform configurations for cloud resources
- Structure Terraform projects with modules
- Manage state with remote backends (S3, GCS, Terraform Cloud)
- Set up multi-environment infrastructure (dev/staging/prod)
- Provision common services (VPCs, EKS, RDS, S3, etc.)
- Implement CI/CD for infrastructure
- Migrate from manual infrastructure to IaC

## Project Structure

### Standard Layout

```
infrastructure/
├── modules/                    # Reusable modules
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── eks-cluster/
│   └── rds-postgres/
├── environments/               # Per-environment configs
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
├── global/                     # Shared resources (IAM, Route53)
│   └── main.tf
└── .terraform.lock.hcl
```

## Core Terraform Concepts

### Providers and Backend

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.27"
    }
  }

  # Remote state (S3 backend)
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}
```

### Variables and Outputs

```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = contains(["us-east-1", "us-west-2", "eu-west-1"], var.aws_region)
    error_message = "Region must be one of: us-east-1, us-west-2, eu-west-1"
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}

variable "database_config" {
  description = "Database configuration"
  type = object({
    instance_class    = string
    allocated_storage = number
    multi_az          = bool
    backup_retention  = number
  })
  default = {
    instance_class    = "db.t3.medium"
    allocated_storage = 100
    multi_az          = false
    backup_retention  = 7
  }
}

# outputs.tf
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
  sensitive   = false
}

output "db_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}
```

## AWS VPC Module

```hcl
# modules/vpc/main.tf
locals {
  az_count = length(var.availability_zones)
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = "${var.name}-vpc"
  })
}

# Public subnets
resource "aws_subnet" "public" {
  count = local.az_count

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "${var.name}-public-${var.availability_zones[count.index]}"
    "kubernetes.io/role/elb" = "1"  # for EKS load balancers
  })
}

# Private subnets
resource "aws_subnet" "private" {
  count = local.az_count

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + local.az_count)
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.tags, {
    Name = "${var.name}-private-${var.availability_zones[count.index]}"
    "kubernetes.io/role/internal-elb" = "1"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(var.tags, { Name = "${var.name}-igw" })
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? local.az_count : 0
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-nat-eip-${count.index}" })
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? local.az_count : 0
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  tags          = merge(var.tags, { Name = "${var.name}-nat-${count.index}" })
  depends_on    = [aws_internet_gateway.main]
}

# Route tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, { Name = "${var.name}-public-rt" })
}

resource "aws_route_table" "private" {
  count  = local.az_count
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(var.tags, { Name = "${var.name}-private-rt-${count.index}" })
}

resource "aws_route_table_association" "public" {
  count          = local.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = local.az_count
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

## EKS Cluster

```hcl
# modules/eks-cluster/main.tf
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.kubernetes_version
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids              = var.subnet_ids
    security_group_ids      = [aws_security_group.eks_cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.public_access_cidrs
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn
    }
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_cloudwatch_log_group.eks,
  ]

  tags = var.tags
}

# Managed node group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = var.node_instance_types
  capacity_type  = "ON_DEMAND"

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role = "general"
  }

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }

  tags = var.tags
}

# IAM roles
resource "aws_iam_role" "eks_cluster" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}
```

## RDS PostgreSQL

```hcl
# modules/rds-postgres/main.tf
resource "aws_db_subnet_group" "main" {
  name       = "${var.name}-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "rds" {
  name        = "${var.name}-rds-sg"
  description = "Security group for RDS"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  tags = var.tags
}

resource "aws_db_instance" "main" {
  identifier = var.name

  engine         = "postgres"
  engine_version = var.postgres_version
  instance_class = var.instance_class

  db_name  = var.database_name
  username = var.username
  password = random_password.db.result

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = var.kms_key_arn

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  multi_az               = var.multi_az

  backup_retention_period   = var.backup_retention
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:00-Mon:05:00"
  deletion_protection       = var.environment == "prod"
  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = "${var.name}-final-snapshot"

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn          = aws_iam_role.rds_monitoring.arn

  parameter_group_name = aws_db_parameter_group.main.name
  tags                 = var.tags
}

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.name}/db-password"
  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db.result
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}
```

## Multi-Environment Setup

```hcl
# environments/prod/main.tf
locals {
  environment = "prod"
  name_prefix = "myapp-${local.environment}"
}

module "vpc" {
  source = "../../modules/vpc"

  name               = local.name_prefix
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  enable_nat_gateway = true
  tags               = local.common_tags
}

module "eks" {
  source = "../../modules/eks-cluster"

  cluster_name       = "${local.name_prefix}-cluster"
  kubernetes_version = "1.29"
  subnet_ids         = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids

  node_instance_types  = ["m5.xlarge"]
  node_min_size        = 3
  node_desired_size    = 5
  node_max_size        = 20

  tags = local.common_tags
}

module "rds" {
  source = "../../modules/rds-postgres"

  name              = "${local.name_prefix}-db"
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  postgres_version  = "16.2"
  instance_class    = "db.r6g.xlarge"
  allocated_storage = 500
  multi_az          = true
  backup_retention  = 30
  environment       = local.environment

  allowed_security_groups = [module.eks.node_security_group_id]
  tags = local.common_tags
}

locals {
  common_tags = {
    Environment = local.environment
    Project     = "myapp"
    ManagedBy   = "terraform"
  }
}

# environments/prod/terraform.tfvars
# aws_region  = "us-east-1"
# environment = "prod"

# environments/prod/backend.tf
terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

## Terraform Workspaces

```bash
# Create and use workspaces for environments
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

terraform workspace select prod
terraform workspace list

# Use workspace in config
variable "instance_count" {
  default = {
    dev     = 1
    staging = 2
    prod    = 5
  }
}

resource "aws_instance" "web" {
  count = var.instance_count[terraform.workspace]
  # ...
}
```

## Terraform Commands

```bash
# Initialize and validate
terraform init                    # download providers
terraform init -upgrade           # upgrade providers
terraform validate                # validate syntax
terraform fmt -recursive          # format all .tf files

# Planning and applying
terraform plan                    # preview changes
terraform plan -out=plan.tfplan   # save plan
terraform apply plan.tfplan       # apply saved plan
terraform apply -auto-approve     # apply without confirmation (CI/CD only)
terraform apply -target=module.vpc  # apply specific resource

# State management
terraform state list              # list resources
terraform state show aws_vpc.main  # show resource details
terraform state mv source dest    # rename resource
terraform state rm aws_instance.old  # remove from state (doesn't destroy)
terraform import aws_s3_bucket.main my-bucket-name  # import existing

# Destroy
terraform destroy                 # destroy all resources
terraform destroy -target=aws_instance.web  # destroy specific

# Output
terraform output                  # show all outputs
terraform output vpc_id           # show specific output

# Debugging
TF_LOG=DEBUG terraform apply      # verbose logging
terraform console                 # interactive console for expressions
```

## CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']
  pull_request:
    paths: ['infrastructure/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    environment: ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}

    permissions:
      id-token: write
      contents: read
      pull-requests: write

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: us-east-1

    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: 1.7.0

    - name: Terraform Init
      run: terraform init
      working-directory: infrastructure/environments/prod

    - name: Terraform Validate
      run: terraform validate
      working-directory: infrastructure/environments/prod

    - name: Terraform Plan
      id: plan
      run: terraform plan -no-color -out=plan.tfplan
      working-directory: infrastructure/environments/prod

    - name: Comment PR with plan
      uses: actions/github-script@v7
      if: github.event_name == 'pull_request'
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '```\n${{ steps.plan.outputs.stdout }}\n```'
          })

    - name: Terraform Apply
      if: github.ref == 'refs/heads/main'
      run: terraform apply -auto-approve plan.tfplan
      working-directory: infrastructure/environments/prod
```

## Best Practices

**State Management**:
- Always use remote backends (S3 + DynamoDB for locking)
- Never store sensitive values in state — use AWS Secrets Manager
- Separate state per environment

**Security**:
- Use OIDC for CI/CD authentication (no long-lived keys)
- Enable encryption for all resources
- Use `sensitive = true` for output values containing secrets
- Scan with `tfsec` or `checkov` before apply

**Module Design**:
- One module per logical component (vpc, eks, rds)
- Use `description` for all variables and outputs
- Provide sensible defaults where possible
- Use `validation` blocks for inputs

**Drift Detection**:
```bash
terraform plan -detailed-exitcode  # exit 2 = changes detected
```

## Additional Resources

- Terraform docs: https://developer.hashicorp.com/terraform/docs
- AWS provider: https://registry.terraform.io/providers/hashicorp/aws/latest
- Terraform best practices: https://developer.hashicorp.com/terraform/language/style
- tfsec security scanner: https://aquasecurity.github.io/tfsec/
