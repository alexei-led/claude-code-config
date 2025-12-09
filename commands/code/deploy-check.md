---
allowed-tools: Task, Bash, Read, Grep, Glob, LS, mcp__perplexity-ask__perplexity_ask
description: Validate K8s/CI configs via deployment-specialist agent
---

# Deployment Validation

Validate infrastructure configs before deployment.

## Step 1: Detect Infrastructure Files

```bash
# Find infrastructure files
find . -name "*.yaml" -o -name "*.yml" | grep -E "(k8s|kubernetes|deploy|helm|kustomize|workflow|action)" | head -20
find . -name "Dockerfile*" -o -name "docker-compose*.yml" | head -10
find . -name "*.tf" | head -10
```

## Step 2: Activate infra-k8s Skill

Use the `infra-k8s` skill for infrastructure patterns guidance.

## Step 3: Run Parallel Validations

Spawn agents IN PARALLEL for each category found:

### Kubernetes Manifests

```bash
# Validate YAML syntax
kubectl apply --dry-run=client -f <manifest> 2>&1

# Check with kubeconform if available
kubeconform -strict <manifest>
```

Review for:

- Security contexts (runAsNonRoot, readOnlyRootFilesystem)
- Resource limits and requests
- Pod disruption budgets
- Network policies

### Helm Charts

```bash
helm lint <chart-path>
helm template <chart-path> | kubeconform -strict
```

### Kustomize

```bash
kustomize build <path> | kubectl apply --dry-run=client -f -
```

### GitHub Actions

```bash
actionlint .github/workflows/*.yml
```

Review for:

- Secrets handling (no hardcoded values)
- Permission scoping
- Dependency pinning

### Terraform

```bash
terraform fmt -check -recursive
terraform validate
tflint --recursive
```

### Dockerfiles

Review for:

- Multi-stage builds
- Non-root user
- Specific image tags (not :latest)
- .dockerignore presence

## Step 4: Security Checklist

Use Perplexity to research latest best practices if uncertain:

| Check                     | Pass/Fail |
| ------------------------- | --------- |
| No secrets in configs     |           |
| Security contexts set     |           |
| Resource limits defined   |           |
| Images pinned to versions |           |
| RBAC properly scoped      |           |

## Step 5: Report

```
DEPLOYMENT CHECK
================
Kubernetes: [PASS/FAIL] - details
Helm: [PASS/FAIL] - details
CI/CD: [PASS/FAIL] - details
Terraform: [PASS/FAIL] - details
Security: [PASS/FAIL] - details

Critical Issues: [list]
Recommendations: [list]
```

**Execute validation now.**
