---
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Bash(kubectl *)
description:
  Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and
  GitHub Actions. Use when making K8s architectural decisions, choosing between Helm
  vs Kustomize, structuring Terraform modules, writing CI/CD workflows, or applying
  security best practices.
name: managing-infra
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Infrastructure Patterns

## Safety: Dry-Run Before Apply

**NEVER** run state-changing commands (`kubectl apply`, `terraform apply`, `helm upgrade --install`) without first presenting the plan/diff to the user.

Always run the read-only equivalent first:

- `terraform plan` before `terraform apply`
- `kubectl diff` before `kubectl apply`
- `helm upgrade --dry-run` before `helm upgrade`

If the user explicitly asks to apply, confirm before executing.

## When to Use What

| Tool               | Use For                                             |
| ------------------ | --------------------------------------------------- |
| **Raw K8s YAML**   | Simple deployments, one-off resources               |
| **Kustomize**      | Environment variations, overlays without templating |
| **Helm**           | Complex apps, third-party charts, heavy templating  |
| **Terraform**      | Cloud resources, infrastructure lifecycle           |
| **GitHub Actions** | CI/CD, automated testing, releases                  |
| **Makefile**       | Build automation, self-documenting targets          |
| **Dockerfile**     | Container builds, multi-stage, multi-arch           |

## Quick Decisions

**Kustomize** when: Simple env differences, readable manifests, patching YAML
**Helm** when: Complex templating, third-party charts, release management

## K8s Security Defaults

Every workload: non-root user, read-only filesystem, no privilege escalation, dropped capabilities, network policies.

## GitHub Actions Patterns

- **CI workflow**: Lint, test, compile on PRs (run on both x86 + ARM)
- **Release workflow**: Multi-arch Docker build on tags (native ARM runners)
- Pin actions by SHA, least-privilege permissions

## References

- [KUBERNETES.md](KUBERNETES.md) - K8s resource patterns
- [TERRAFORM.md](TERRAFORM.md) - Terraform module patterns
- [GITHUB-ACTIONS.md](GITHUB-ACTIONS.md) - CI/CD workflow patterns
- [MAKEFILE.md](MAKEFILE.md) - Build automation patterns
- [DOCKERFILE.md](DOCKERFILE.md) - Container build patterns
- [templates/](templates/) - Ready-to-use templates

## Commands

```bash
kubectl apply -k ./              # Apply kustomize
helm upgrade --install NAME .    # Install/upgrade chart
terraform plan && terraform apply
```
