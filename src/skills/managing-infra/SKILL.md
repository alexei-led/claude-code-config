---
description:
  Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and
  GitHub Actions. Use when making K8s architectural decisions, choosing between Helm
  vs Kustomize, structuring Terraform modules, writing CI/CD workflows, or applying
  security best practices. NOT for cloud CLI commands (see using-cloud-cli) or
  deploy validation and apply workflows (see deploying-infra).
name: managing-infra
---

# Infrastructure Patterns

## Safety: Dry-Run Before Apply

**NEVER** run state-changing commands (`kubectl apply`, `terraform apply`, `helm upgrade --install`) without first presenting the plan/diff to the user.

Always run the read-only equivalent first:

- `terraform plan` before `terraform apply`
- `kubectl diff` before `kubectl apply`
- `helm upgrade --dry-run` before `helm upgrade`

If the user explicitly asks to apply, confirm before executing.

## When to Use What

- **Raw K8s YAML** — Simple deployments, one-off resources
- **Kustomize** — Environment variations, overlays without templating
- **Helm** — Complex apps, third-party charts, heavy templating
- **Terraform** — Cloud resources, infrastructure lifecycle
- **GitHub Actions** — CI/CD, automated testing, releases
- **Makefile** — Build automation, self-documenting targets
- **Dockerfile** — Container builds, multi-stage, multi-arch

## K8s Security Defaults

Every workload: non-root user, read-only filesystem, no privilege escalation, dropped capabilities, network policies.

## GitHub Actions Patterns

- **CI workflow**: Lint, test, compile on PRs (run on both x86 + ARM)
- **Terraform CI**: include `terraform fmt -check`, `terraform init -backend=false`, `terraform validate`, and `terraform plan` for changed stacks where credentials allow
- **Release workflow**: Multi-arch Docker build on tags (native ARM runners)
- Pin actions by SHA, least-privilege permissions

## Terraform Module Structure

For shared VPC, service accounts, and app environments:

- Put shared network primitives and organization-wide IAM in shared/foundation modules.
- Put app-specific service accounts, bindings, and deploy-time config in app/environment modules.
- Keep module inputs/outputs explicit; pass IDs, self-links, emails, and subnet names instead of reaching into sibling state implicitly.
- Choose backend/state boundaries deliberately: shared foundations change slowly; app environments can have separate state for safer rollout and ownership.
- Apply least-privilege IAM per service account and environment.
- Require CI validation for changed Terraform stacks: `terraform fmt -check`, `terraform init -backend=false`, `terraform validate`, and `terraform plan` where credentials allow.

## Failure Cases

- User asks to apply without reviewing a plan: stop, run the read-only equivalent first, present the diff, then require explicit confirmation.
- Terraform plan shows unexpected resource destruction: halt, surface the full destroy list, do not proceed until the user explicitly confirms each affected resource.

## References

- [KUBERNETES.md](references/KUBERNETES.md) - K8s resource patterns
- [TERRAFORM.md](references/TERRAFORM.md) - Terraform module patterns
- [GITHUB-ACTIONS.md](references/GITHUB-ACTIONS.md) - CI/CD workflow patterns
- [MAKEFILE.md](references/MAKEFILE.md) - Build automation patterns
- [DOCKERFILE.md](references/DOCKERFILE.md) - Container build patterns
- [templates/](templates/) - Ready-to-use templates

## Commands

```bash
kubectl apply -k ./              # Apply kustomize
helm upgrade --install NAME .    # Install/upgrade chart
terraform plan && terraform apply
```
