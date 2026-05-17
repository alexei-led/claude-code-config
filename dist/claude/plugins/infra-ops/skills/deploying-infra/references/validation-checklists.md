# Pre-flight Validation Checklists (Step 3)

Per infrastructure type. The engineer agent runs these before any apply.
Report READY/BLOCKED per category with `file:line` for issues and severity
CRITICAL / IMPORTANT / SUGGESTION.

## Kubernetes

- `kubectl apply --dry-run=client -f <files>`
- Check: security contexts, resource limits, non-root users
- Check: liveness/readiness probes defined
- Check: no `latest` image tags
- Check: namespace exists or will be created
- Check: secrets/configmaps referenced exist

## Helm

- `helm lint <chart>`
- `helm template --debug`
- `helm diff upgrade` (if helm-diff installed)
- Check: values.yaml has sensible defaults

## Kustomize

- `kustomize build | kubectl apply --dry-run=client -f -`
- Validate overlays for the target environment

## GitHub Actions

- `actionlint` (if available)
- Check: secrets not hardcoded
- Check: permissions minimized (not `write-all`)
- Check: pinned action versions (`@vX.Y.Z` not `@main`)

## Terraform

- `terraform fmt -check`
- `terraform validate`
- `terraform plan -out=tfplan`
- Check: no hardcoded credentials
- Check: state backend configured
- Check: no destructive changes without confirmation
- Check: state lock acquired

## Dockerfile

- Multi-stage builds where appropriate
- Non-root user (`USER` directive)
- Pinned base image tags (not `:latest`)
- No secrets in build args
