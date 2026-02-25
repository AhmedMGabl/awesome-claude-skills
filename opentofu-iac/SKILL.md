---
name: opentofu-iac
description: >
  OpenTofu infrastructure-as-code patterns covering provider configuration, state encryption,
  variable validation, module development, testing, and migration from Terraform.
  This skill should be used when generating or reviewing OpenTofu configurations,
  writing reusable modules, setting up state encryption, defining variable validation rules,
  creating tests with `tofu test`, or migrating existing Terraform codebases to OpenTofu.
---

# OpenTofu Infrastructure as Code

## When to Use

- Generating OpenTofu provider configurations, resources, data sources, or output blocks
- Creating reusable modules with input validation and documentation
- Configuring state encryption with built-in key providers
- Writing `tofu test` files for module validation
- Migrating Terraform configurations to OpenTofu
- Using `moved` blocks to refactor resource addresses without destroying infrastructure

## Examples

### 1. Provider and Backend Configuration

```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket         = "my-tofu-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tofu-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = { ManagedBy = "opentofu", Environment = var.environment }
  }
}
```

### 2. State Encryption

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "my_passphrase" {
      passphrase = var.state_passphrase
    }
    method "aes_gcm" "state_encryption" {
      keys = key_provider.pbkdf2.my_passphrase
    }
    state { method = method.aes_gcm.state_encryption, enforced = true }
    plan  { method = method.aes_gcm.state_encryption, enforced = true }
  }
}
```

### 3. Variable Validation with Custom Conditions

```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "cidr_block" {
  type = string
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR notation (e.g., 10.0.0.0/16)."
  }
  validation {
    condition     = tonumber(split("/", var.cidr_block)[1]) <= 24
    error_message = "CIDR prefix must be /24 or larger."
  }
}
```

### 4. Module with Moved Blocks

```hcl
resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "${var.name}-vpc" }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]
  tags = { Name = "${var.name}-public-${count.index}" }
}

moved {
  from = aws_subnet.main
  to   = aws_subnet.public
}

output "vpc_id" { value = aws_vpc.this.id }
output "public_subnet_ids" { value = aws_subnet.public[*].id }
```

### 5. Testing with `tofu test`

```hcl
# tests/vpc.tftest.hcl
variables {
  name                = "test"
  cidr_block          = "10.0.0.0/16"
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  availability_zones  = ["us-east-1a", "us-east-1b"]
}

run "vpc_creation" {
  command = plan
  assert {
    condition     = aws_vpc.this.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block did not match expected value"
  }
}

run "integration" {
  command = apply
  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID output must not be empty"
  }
}
```

### 6. Migration from Terraform

```bash
# Install OpenTofu and initialize
brew install opentofu
tofu init
tofu validate
tofu plan  # Should show no changes if migration is clean

# Update lock file for multiple platforms
tofu providers lock \
  -platform=linux_amd64 \
  -platform=darwin_arm64
```

Key migration notes:

- OpenTofu reads the same `.tf` files and `.terraform.lock.hcl`
- State files are fully compatible; no conversion required
- Replace `terraform` with `tofu` in all CLI invocations
- State encryption is an OpenTofu-only feature unavailable in Terraform
