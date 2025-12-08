---
name: cloud-cli
description: Cloud CLI patterns for GCP and AWS. Use when running bq queries, gcloud or aws commands. Covers BigQuery cost optimization, when to use which GCP/AWS service, and operational best practices. Assumes pre-configured credentials.
allowed-tools: Read, Bash, Grep, Glob, LS
---

# Cloud CLI Patterns

Credentials are pre-configured. Use `--help` or Context7 for syntax.

## BigQuery Best Practices

- Always use `--dry_run` first to estimate costs
- Prefer partitioned/clustered tables for large datasets
- Use `LIMIT` during development
- Avoid `SELECT *` - specify columns
- Use `--format=json` or `--format=csv` for scripting

## GCP Patterns

- Use `--project` explicitly in scripts
- Prefer `--format=json` for parsing output
- Use `--quiet` to suppress prompts in automation
- Check IAM permissions before debugging "access denied"

## AWS Patterns

- Use `--output json` for scripting
- Use `--query` for JMESPath filtering
- Prefer `--region` explicitly in scripts
- Use `--dry-run` where available (EC2, etc.)

## Cost Awareness

**BigQuery**: Charged per bytes scanned - partition tables, avoid SELECT \*
**GCS/S3**: Egress costs add up - keep processing in same region
**Compute**: Spot/preemptible for fault-tolerant workloads

## When to Use What

| Need           | GCP                   | AWS              |
| -------------- | --------------------- | ---------------- |
| Object storage | GCS                   | S3               |
| Data warehouse | BigQuery              | Athena/Redshift  |
| Serverless     | Cloud Run / Functions | Lambda / Fargate |
| K8s            | GKE                   | EKS              |
| IAM            | Service accounts      | IAM roles        |
