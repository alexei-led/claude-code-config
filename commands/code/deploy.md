---
context: fork
argument-hint: [--dry-run | --apply] [environment]
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(kubectl:*)
  - Bash(helm:*)
  - Bash(kustomize:*)
  - Bash(terraform:*)
  - Bash(docker:*)
  - Bash(git:*)
  - Bash(make:*)
description: Deploy infrastructure changes with validation and rollback support
---

# Deploy Infrastructure

Deploy changes to Kubernetes, Terraform, or Helm with pre-flight validation.

## Usage

```
/code:deploy --dry-run              # Validate only (default)
/code:deploy --apply staging        # Apply to staging
/code:deploy --apply production     # Apply to production (requires confirmation)
```

---

## Step 1: Parse Arguments

**Default**: `--dry-run` (safe mode)

- `--dry-run` → Validate without applying
- `--apply` → Apply changes after validation
- `[environment]` → Target environment (staging, production, dev)

---

## Step 2: Detect Infrastructure Type

```bash
# Check for infrastructure files
ls -la *.tf 2>/dev/null && echo "TERRAFORM"
ls -la chart.yaml Chart.yaml 2>/dev/null && echo "HELM"
ls -la kustomization.yaml 2>/dev/null && echo "KUSTOMIZE"
ls -la k8s/ kubernetes/ manifests/ 2>/dev/null && echo "K8S_MANIFESTS"
```

**If no infrastructure detected**: "No infrastructure files found. Looking for: \*.tf, Chart.yaml, kustomization.yaml, k8s/"

---

## Step 3: Pre-flight Validation

Spawn **infra-engineer** for validation:

```
Task(
  subagent_type="infra-engineer",
  description="Pre-flight validation",
  prompt="Validate infrastructure before deployment.

  Type: {detected_type}
  Environment: {environment}
  Mode: {dry-run|apply}

  Run pre-flight checks:

  **Terraform:**
  - terraform fmt -check
  - terraform validate
  - terraform plan -out=tfplan
  - Check: no destructive changes without confirmation
  - Check: state lock acquired

  **Helm:**
  - helm lint
  - helm template --debug
  - helm diff upgrade (if helm-diff installed)

  **Kustomize:**
  - kustomize build | kubectl apply --dry-run=client -f -
  - Validate overlays for {environment}

  **K8s Manifests:**
  - kubectl apply --dry-run=client -f <files>
  - Check: namespace exists or will be created
  - Check: secrets/configmaps referenced exist

  Output: READY/BLOCKED with details"
)
```

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

**If --dry-run**: Stop here with summary.

**If --apply and BLOCKED**: Stop, show blockers.

---

## Step 5: Confirm Production Deploys

**If environment = production:**

**STOP**: `AskUserQuestion`

| Header     | Question              | Options                                                                                                            |
| ---------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Production | Deploy to PRODUCTION? | 1. **Yes, deploy** - Apply changes now<br>2. **Review again** - Show full diff<br>3. **Cancel** - Abort deployment |

---

## Step 6: Apply Changes

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

## Step 7: Post-Deploy Verification

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

---

## Step 8: Summary

```
DEPLOYMENT COMPLETE
===================
Environment: {env}
Type: {terraform|helm|kustomize|k8s}
Duration: {time}

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
