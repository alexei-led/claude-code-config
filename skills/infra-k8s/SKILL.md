---
name: infra-k8s
description: Infrastructure patterns for Kubernetes, Terraform, Helm, and Kustomize. Use when making architectural decisions about K8s resources, choosing between Helm vs Kustomize, structuring Terraform modules, or applying security best practices.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, LS
---

# Infrastructure Patterns

## When to Use What

| Tool             | Use For                                             |
| ---------------- | --------------------------------------------------- |
| **Raw K8s YAML** | Simple deployments, one-off resources               |
| **Kustomize**    | Environment variations, overlays without templating |
| **Helm**         | Complex apps, third-party charts, heavy templating  |
| **Terraform**    | Cloud resources, infrastructure lifecycle           |

## K8s Best Practices

- Always set `securityContext` (runAsNonRoot, readOnlyRootFilesystem, drop ALL caps)
- Always set resource requests and limits
- Use standard labels: `app.kubernetes.io/name`, `app.kubernetes.io/component`
- Prefer `Deployment` over `Pod` directly
- Use `ConfigMap` for config, `Secret` for sensitive data

## Terraform Patterns

- Let provider generate resource names (`name_prefix` not `name`)
- Use modules for reusable components
- Separate state per environment
- Use `terraform fmt` and `terraform validate` before apply

## Kustomize vs Helm Decision

**Kustomize** when:

- Simple environment differences (replicas, namespaces)
- Want to keep manifests readable
- Patching existing YAML

**Helm** when:

- Complex templating logic needed
- Installing third-party charts
- Need release management (rollback, history)

## Security Defaults

Every workload should have:

- Non-root user
- Read-only filesystem
- No privilege escalation
- Dropped capabilities
- Network policies

Use Context7 or Ref MCP to look up specific syntax and commands.
