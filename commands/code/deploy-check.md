---
context: fork
allowed-tools:
  - Task
  - Bash
  - Grep
  - Glob
  - mcp__perplexity-ask__perplexity_ask
description: Validate K8s/CI configs via infra-engineer agent
---

# Deployment Validation

Validate Kubernetes, Terraform, Helm, GitHub Actions, and Docker configs.

## Step 1: Detect Infrastructure Files

Use Glob to find infrastructure files (quick scan, no deep reads):

- `**/*.yaml`, `**/*.yml` filtered for k8s/helm/kustomize keywords
- `.github/workflows/*.yml`
- `**/*.tf`
- `**/Dockerfile*`, `**/docker-compose*.yml`

## Step 2: Spawn Validation Agent

Based on detected file types, spawn **infra-engineer** agent with validation prompt:

```
Task(subagent_type="infra-engineer", prompt="
"Validate {detected_types} infrastructure in this repository.

Run these validations:
{include only relevant sections based on detected files}

- K8s: kubectl apply --dry-run=client, check security contexts/resource limits
- Helm: helm lint, helm template validation
- GitHub Actions: actionlint, check secrets/permissions
- Terraform: terraform fmt -check, validate, tflint
- Dockerfile: multi-stage, non-root, pinned tags

Output: PASS/FAIL per category with file:line issues."
```

## Step 3: Research if Needed

For uncertain findings, use Perplexity for current best practices.

## Step 4: Present Summary

```
DEPLOYMENT CHECK
================
{Category}: [PASS/FAIL] - details

Critical Issues: [list]
Recommendations: [list]
```

**Execute validation now.**
