---
name: deploying-infra
description: Sequential infrastructure deployment — detect infra type (Kubernetes, Terraform, Helm, Kustomize, GitHub Actions, Docker), validate configs, dry-run, show diff, apply only after user confirmation, and verify post-deploy health. Includes safety checks for destructive operations.
---

# Deploy Infrastructure

Validate and deploy infrastructure changes safely. Dry-run is the default. Never apply changes, especially destructive ones, without explicit confirmation. Keep going through each step — do not skip validation or the confirmation gate.

## Step 1: Parse arguments

Check `$ARGUMENTS`:

- `--dry-run` (default if nothing specified) — validate and show diff only, stop before applying
- `--apply` — validate, show diff, confirm with user, then apply
- `[environment]` — target environment name (e.g., `staging`, `production`)

If no arguments are supplied, treat as `--dry-run`.

## Step 2: Detect infrastructure type

Use Glob to find infrastructure files. Do not guess — look at what is actually present.

- `**/*.tf` — Terraform
- `**/Chart.yaml` — Helm chart
- `**/kustomization.yaml` — Kustomize
- `.github/workflows/*.yml` — GitHub Actions
- `**/Dockerfile*`, `**/docker-compose*.yml` — Docker

Read the relevant top-level config files to understand the scope of what will be deployed. If no infrastructure files are found, report it and stop.

## Step 3: Validate configs

Run validation tools for each detected type. Read the output before proceeding — fix any validation errors before continuing.

**Terraform:**

```bash
terraform fmt -check
terraform validate
```

**Helm:**

```bash
helm lint .
helm template . --debug > /dev/null
```

**Kustomize:**

```bash
kustomize build overlays/<environment> | kubectl apply --dry-run=client -f -
```

**Kubernetes (raw manifests):**

```bash
kubectl apply --dry-run=client -f <manifests-dir>/
```

**GitHub Actions:**

```bash
actionlint .github/workflows/*.yml
```

Security checks to apply manually by reading the files:

- No hardcoded secrets, tokens, or credentials anywhere
- No `latest` image tags in K8s or Dockerfile
- GitHub Actions: permissions are minimized (not `write-all`), action versions are pinned to `@vX.Y.Z`
- Terraform: state backend is configured, no destructive changes (`-/+` or `destroy`) without a note
- Kubernetes: security contexts set, resource limits defined, liveness/readiness probes present

If CRITICAL issues are found, report them and stop. Ask the user how to proceed.

## Step 4: Dry-run and show diff

Generate a preview of what would change:

**Terraform:**

```bash
terraform plan -out=tfplan
```

**Helm:**

```bash
helm diff upgrade <release-name> . -f values-<environment>.yaml
```

**Kubernetes / Kustomize:**

```bash
kubectl diff -f <manifests-dir>/
# or
kustomize build overlays/<environment> | kubectl diff -f -
```

Present the diff summary. Explicitly call out:

- Resources to be **created** (count and names)
- Resources to be **modified**
- Resources to be **destroyed or replaced** — flag these prominently

If `--dry-run` was specified, stop here and deliver the validation report.

## Step 5: Confirm before applying

Ask the user in plain prose: "Here is what will change: [summary]. Should I apply these changes to [environment]?"

For production environments, make the confirmation explicit: "This will apply to PRODUCTION. Confirm?"

Do not proceed until you have a clear yes. If the user wants to review something first, do that and ask again.

## Step 6: Apply changes

Log the deployment start, then apply:

```bash
echo "$(date -Iseconds) DEPLOY_START env=<environment>" >> .deploy.log
```

**Terraform:**

```bash
terraform apply tfplan
```

**Helm:**

```bash
helm upgrade --install <release-name> . -f values-<environment>.yaml
```

**Kustomize:**

```bash
kustomize build overlays/<environment> | kubectl apply -f -
```

**Kubernetes (raw manifests):**

```bash
kubectl apply -f <manifests-dir>/ --recursive
```

```bash
echo "$(date -Iseconds) DEPLOY_END status=$?" >> .deploy.log
```

## Step 7: Verify post-deploy health

Check that the deployment is healthy:

```bash
# Kubernetes rollout
kubectl rollout status deployment/<name> --timeout=300s
kubectl get pods -l app=<name>

# Helm
helm status <release-name>

# Terraform
terraform show | head -50
```

If the rollout fails or pods are not healthy, provide the rollback command immediately:

```bash
# Kubernetes
kubectl rollout undo deployment/<name>

# Helm
helm rollback <release-name>

# Terraform (point to last known-good state)
terraform apply -target=<resource>
```

## Output format

```
DEPLOYMENT COMPLETE
===================
Environment: <env>
Type: <terraform|helm|kustomize|k8s|gha>
Mode: <dry-run|applied>

Changes:
- <resource>: <created|modified|destroyed>

Status: HEALTHY | DEGRADED | FAILED

Rollback: <command if applicable>
```

For dry-run mode, replace "DEPLOYMENT COMPLETE" with "VALIDATION COMPLETE" and omit the rollback line.
