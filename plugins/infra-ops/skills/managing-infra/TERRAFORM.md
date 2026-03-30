# Terraform Patterns

## Module Structure

```
modules/
└── service/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── versions.tf
environments/
├── dev/
│   ├── main.tf
│   ├── backend.tf
│   └── terraform.tfvars
└── prod/
    ├── main.tf
    ├── backend.tf
    └── terraform.tfvars
```

## Module Pattern

### modules/service/main.tf

```hcl
resource "google_cloud_run_service" "main" {
  name     = var.name
  location = var.region

  template {
    spec {
      containers {
        image = var.image

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
```

### modules/service/variables.tf

```hcl
variable "name" {
  description = "Service name"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "image" {
  description = "Container image"
  type        = string
}

variable "cpu" {
  description = "CPU limit"
  type        = string
  default     = "1000m"
}

variable "memory" {
  description = "Memory limit"
  type        = string
  default     = "512Mi"
}
```

### modules/service/outputs.tf

```hcl
output "url" {
  description = "Service URL"
  value       = google_cloud_run_service.main.status[0].url
}

output "name" {
  description = "Service name"
  value       = google_cloud_run_service.main.name
}
```

## Environment Usage

### environments/prod/main.tf

```hcl
module "api" {
  source = "../../modules/service"

  name   = "api"
  region = "us-central1"
  image  = "gcr.io/myproject/api:${var.api_version}"
  cpu    = "2000m"
  memory = "1Gi"
}
```

### environments/prod/backend.tf

```hcl
terraform {
  backend "gcs" {
    bucket = "myproject-terraform-state"
    prefix = "prod"
  }
}
```

## Best Practices

### Naming

```hcl
# Let provider generate names
resource "google_storage_bucket" "main" {
  name_prefix = "myapp-data-"
  location    = var.region
}

# Not hardcoded
resource "google_storage_bucket" "bad" {
  name     = "myapp-data-bucket"  # Avoid
  location = var.region
}
```

### Tagging

```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "main" {
  ami           = var.ami
  instance_type = var.instance_type
  tags          = merge(local.common_tags, { Name = "web-server" })
}
```

### Data Sources

```hcl
data "google_project" "current" {}

data "google_compute_zones" "available" {
  region = var.region
}
```

### Sensitive Outputs

```hcl
output "database_password" {
  value     = random_password.db.result
  sensitive = true
}
```

## Commands

```bash
terraform init          # Initialize
terraform plan          # Preview
terraform apply         # Apply
terraform destroy       # Destroy

terraform fmt           # Format
terraform validate      # Validate

terraform state list    # List resources
terraform state show    # Show resource
```
