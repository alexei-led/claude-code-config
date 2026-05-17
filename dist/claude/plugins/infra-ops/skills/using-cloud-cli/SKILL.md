---
allowed-tools:
- Read
- Bash
- Grep
- Glob
context: fork
description: Cloud CLI patterns for GCP and AWS. Use when running bq queries, gcloud
  commands, aws commands, or making decisions about cloud services. Covers BigQuery
  cost optimization and operational best practices. NOT for Terraform or Kubernetes
  architectural decisions (see managing-infra).
name: using-cloud-cli
user-invocable: false
---

# Cloud CLI Patterns

Credentials may be pre-configured. Verify identity before touching resources. Use `--help` or Context7 for syntax.

## Safety and Identity

Before destructive commands (`delete`, `destroy`, `rm`, `terminate`, IAM changes, bucket/object deletion):

Do not present executable delete commands as the next action until identity and candidate resources have been shown and the user has explicitly confirmed the exact resources. A safe answer may show inventory/dry-run commands first, then say deletion commands come only after confirmation.

1. Confirm the active cloud target:
   - AWS: `aws sts get-caller-identity` plus explicit `--profile` and `--region` when relevant.
   - GCP: `gcloud config get-value account` and `gcloud config get-value project`, or pass explicit `--project`.
2. Inventory candidate resources with non-destructive list/describe commands.
3. Present the exact command, account/profile, project, region/zone, and resources affected.
4. Require explicit user confirmation before execution. Do not rely on `--quiet`, default profiles, or implicit projects for destructive work.

## BigQuery

```bash
# Always estimate cost first
bq query --dry_run --use_legacy_sql=false 'SELECT ...'

# Run query
bq query --use_legacy_sql=false --format=json 'SELECT ...'

# List tables
bq ls project:dataset

# Get table schema
bq show --schema --format=json project:dataset.table
```

**Cost awareness**: Charged per bytes scanned. Use `--dry_run`, partition tables, specify columns.

## GCP (gcloud)

```bash
# List resources
gcloud compute instances list --format=json

# Describe resource
gcloud compute instances describe INSTANCE --zone=ZONE --format=json

# Create with explicit project
gcloud compute instances create NAME --project=PROJECT --zone=ZONE

# Destructive: confirm active account/project first, then ask the user
gcloud config get-value account
gcloud config get-value project
gcloud compute instances delete NAME --project=PROJECT --zone=ZONE
```

## AWS

```bash
# List resources
aws ec2 describe-instances --output json

# With JMESPath filtering
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId' --output text

# Explicit region
aws s3 ls s3://bucket --region us-west-2

# Dry run where available
aws ec2 run-instances --dry-run ...
```

## Error Handling & Recovery

Auth failures, rate limiting, common error patterns, and a retry-with-backoff
template are vendor-specific. For GCP, read `references/GCP.md` `## Error
Handling`. For AWS, read `references/AWS.md` `## Error Handling`.

## References

- [GCP.md](references/GCP.md) - GCP service patterns and common commands
- [AWS.md](references/AWS.md) - AWS service patterns and common commands
- [scripts/](scripts/) - Helper scripts for common operations
