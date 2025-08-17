---
allowed-tools: Task, Read, LS, Grep, Glob, Bash, mcp__perplexity-ask__perplexity_ask
description: Validate K8s/CI configs via deployment-specialist agent
---

Deployment-specialist validates: K8s manifests, GitHub Actions, security contexts, resource limits, helm/kustomize.

Checks:
- Manifest syntax and security settings
- CI/CD pipeline configurations
- Best practices compliance
- IaC validation

Example:
```
/deploy-check
```
