---
agent: engineer
allowed-tools:
- Read
- Bash
- Grep
- Glob
- Bash(kubectl *)
context: fork
description: Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and
  GitHub Actions. Use when making K8s architectural decisions, choosing between Helm
  vs Kustomize, structuring Terraform modules, writing CI/CD workflows, or applying
  security best practices. NOT for cloud CLI commands (see using-cloud-cli) or deploy
  validation and apply workflows (see deploying-infra).
name: managing-infra
user-invocable: false
---

# Infrastructure Patterns

## Role-gated action

Detect your capability from your tools, not from prose:

- Write-capable role (engineer): run the read-only dry-run, present the diff, get confirmation, then apply and verify.
- Read-only role (reviewer): a reviewer has no Bash — it cannot run `terraform plan` or `kubectl diff`. Review the manifests/modules in scope from the files and caller-supplied plan output, and emit changes in the Proposed Changes contract under Output. Apply nothing.

## Detect the infra tool and load references

Detect the tool from the files in scope and load the matching reference:

- `*.tf` / `*.tfvars` → [TERRAFORM.md](references/TERRAFORM.md)
- K8s manifests / `kustomization.yaml` → [KUBERNETES.md](references/KUBERNETES.md)
- `Chart.yaml` / `templates/*.yaml` → [HELM.md](references/HELM.md)
- workflow YAML under `.github/workflows/` → [GITHUB-ACTIONS.md](references/GITHUB-ACTIONS.md)
- `Dockerfile` → [DOCKERFILE.md](references/DOCKERFILE.md)
- `Makefile` → [MAKEFILE.md](references/MAKEFILE.md)

Mixed stacks: load each matching reference. Unknown tool: use the core patterns below only.

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

## Output

Engineer (applied after dry-run): report the dry-run/plan diff shown, the confirmation obtained, and the apply result.

Reviewer (reviewed only — emit changes as a proposal, apply nothing):

```text
## Proposed Changes

### Change 1: <brief description>

File: `path/to/manifest`
Action: CREATE | MODIFY | DELETE

Code:
<the manifest/module content>

Rationale: <security/structure issue this addresses>
```

## References

- [KUBERNETES.md](references/KUBERNETES.md) - K8s resource patterns
- [HELM.md](references/HELM.md) - Helm chart structure and templating patterns
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
