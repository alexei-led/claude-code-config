---
name: deploying-infra
description: Validate and deploy Kubernetes, Terraform, Helm, Kustomize, GitHub Actions, and Docker configs. Use when user says "deploy", "deploy to staging", "apply changes", "terraform apply", "helm upgrade", "kubectl apply", "rollout", "deploy check", "validate deployment", "validate infrastructure", or wants to verify or apply infrastructure changes.
user-invocable: true
context: fork
argument-hint: "[--dry-run | --apply] [environment]"
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Bash(kubectl *)
  - Bash(helm *)
  - Bash(kustomize *)
  - Bash(terraform *)
  - Bash(actionlint *)
  - Bash(docker *)
  - Bash(git *)
  - Bash(make *)
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - mcp__perplexity-ask__perplexity_ask
---

# Deploy Infrastructure

Validate and deploy changes to Kubernetes, Terraform, Helm, or Kustomize with pre-flight checks, security validation, and rollback support.

## Usage

```
/deploying-infra --dry-run              # Validate only (default)
/deploying-infra --apply staging        # Apply to staging
/deploying-infra --apply production     # Apply to production (requires confirmation)
```

`--dry-run` runs steps 1–5 (validation only). `--apply` runs all 8 steps.

---

## Step 1: Parse Arguments

**Default**: `--dry-run` (safe mode)

- `--dry-run` → Validate without applying (stops after step 5)
- `--apply` → Apply changes after validation
- `[environment]` → Target environment (staging, production, dev)
- `--background` → Run validation in background, return agent ID

---

## Step 2: Detect Infrastructure Type

Use Glob to find infrastructure files (quick scan):

- `**/*.yaml`, `**/*.yml` - K8s, Helm, Kustomize
- `.github/workflows/*.yml` - GitHub Actions
- `**/*.tf` - Terraform
- `**/Dockerfile*`, `**/docker-compose*.yml` - Docker
- `**/kustomization.yaml` - Kustomize
- `**/Chart.yaml` - Helm

**If no infrastructure detected**: "No infrastructure files found. Looking for: \*.tf, Chart.yaml, kustomization.yaml, k8s/, Dockerfile"

---

## Step 3: Pre-flight Validation

Spawn **infra-engineer** for validation:

```
Task(
  subagent_type="infra-engineer",
  run_in_background={true if --background else false},
  description="Pre-flight validation",
  prompt="Validate infrastructure before deployment.

  Type: {detected_type}
  Environment: {environment}
  Mode: {dry-run|apply}

  Run pre-flight checks:

  **Kubernetes:**
  - kubectl apply --dry-run=client -f <files>
  - Check: security contexts, resource limits, non-root users
  - Check: liveness/readiness probes defined
  - Check: no 'latest' image tags
  - Check: namespace exists or will be created
  - Check: secrets/configmaps referenced exist

  **Helm:**
  - helm lint <chart>
  - helm template --debug
  - helm diff upgrade (if helm-diff installed)
  - Check: values.yaml has sensible defaults

  **Kustomize:**
  - kustomize build | kubectl apply --dry-run=client -f -
  - Validate overlays for {environment}

  **GitHub Actions:**
  - actionlint (if available)
  - Check: secrets not hardcoded
  - Check: permissions minimized (not 'write-all')
  - Check: pinned action versions (@vX.Y.Z not @main)

  **Terraform:**
  - terraform fmt -check
  - terraform validate
  - terraform plan -out=tfplan
  - Check: no hardcoded credentials
  - Check: state backend configured
  - Check: no destructive changes without confirmation
  - Check: state lock acquired

  **Dockerfile:**
  - Multi-stage builds where appropriate
  - Non-root user (USER directive)
  - Pinned base image tags (not :latest)
  - No secrets in build args

  Output format:
  READY/BLOCKED per category with file:line for issues.
  Severity: CRITICAL / IMPORTANT / SUGGESTION"
)
```

**If --background:** Return agent ID immediately for later collection.

---

## Step 4: Review Changes

**Present diff/plan to user:**

```
## Pre-flight: {READY|BLOCKED}

### Changes Summary
{terraform plan output / helm diff / kubectl diff}

### Resources Affected
- {resource type}: {count} to create, {count} to modify, {count} to destroy

### Warnings
- {any destructive changes}
- {any security concerns}
```

**If BLOCKED**: Stop, show blockers.

---

## Step 5: Research Best Practices (if needed)

For uncertain findings, use Perplexity for current best practices:

```
mcp__perplexity-ask__perplexity_ask with:
"Current best practices for {specific concern} in {technology} 2024-2025"
```

**If --dry-run**: Stop here with validation summary.

---

## Step 6: Confirm Production Deploys

**If environment = production:**

**STOP**: `AskUserQuestion`

| Header     | Question              | Options                                                                                                            |
| ---------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Production | Deploy to PRODUCTION? | 1. **Yes, deploy** - Apply changes now<br>2. **Review again** - Show full diff<br>3. **Cancel** - Abort deployment |

---

## Step 7: Apply Changes

```bash
# Record deployment start
echo "$(date -Iseconds) DEPLOY_START env=$environment" >> .deploy.log

# Apply based on type
case $type in
  terraform)
    terraform apply tfplan
    ;;
  helm)
    helm upgrade --install {release} {chart} -f values-{env}.yaml
    ;;
  kustomize)
    kustomize build overlays/{env} | kubectl apply -f -
    ;;
  k8s)
    kubectl apply -f k8s/{env}/ --recursive
    ;;
esac

# Record completion
echo "$(date -Iseconds) DEPLOY_END status=$?" >> .deploy.log
```

---

## Step 8: Post-Deploy Verification

```bash
# Wait for rollout
kubectl rollout status deployment/{name} --timeout=300s

# Health check
kubectl get pods -l app={name}
```

**If rollout fails:**

```
ROLLBACK AVAILABLE

kubectl rollout undo deployment/{name}
# or
terraform apply -target=... (previous state)
# or
helm rollback {release}
```

## Output

```
DEPLOYMENT COMPLETE
===================
Environment: {env}
Type: {terraform|helm|kustomize|k8s}
Duration: {time}
Agent ID: {id} (use /agent:resume {id} to continue)

Applied:
- {resource}: {action}

Status: {HEALTHY|DEGRADED|FAILED}

Rollback: {command if needed}
```

---

## Key Principles

1. **Dry-run by default** - Never apply without explicit --apply
2. **Production requires confirmation** - Extra gate for prod
3. **Rollback ready** - Always show rollback command
4. **Log everything** - .deploy.log for audit trail

Pairs with `managing-infra` skill for patterns and reference material.

---

**Execute deployment workflow now.**
