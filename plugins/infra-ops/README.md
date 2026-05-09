# infra-ops

Infrastructure and cloud operations: Kubernetes, Terraform, Helm, GitHub Actions, AWS, GCP. Exported for Claude Code, Codex CLI, Gemini CLI, and Pi.

## Skills (3)

| Skill             | Invocable | What It Does                                          |
| ----------------- | --------- | ----------------------------------------------------- |
| `deploying-infra` | yes       | Validate and deploy K8s/Terraform/Helm/GitHub Actions |
| `managing-infra`  | auto      | K8s resources, Terraform, Helm, Dockerfiles, Actions  |
| `using-cloud-cli` | auto      | GCP (gcloud, bq, gsutil) and AWS CLI patterns         |

Includes supplementary docs: `KUBERNETES.md`, `TERRAFORM.md`, `DOCKERFILE.md`, `GITHUB-ACTIONS.md`, `MAKEFILE.md`, `AWS.md`, `GCP.md`.

## Agents (1)

- `infra-engineer` (sonnet) — infrastructure implementation and validation (Claude Code only)

## External Providers

| Provider | Used For |
| --- | --- |
| Context7 CLI (`ctx7`) | Portable cloud and IaC documentation |
| Perplexity/web providers | Deployment research and best practices |
| Sequential Thinking MCP | Claude Code-only structured planning |
| MorphLLM MCP | Claude Code-only codebase search and batch editing |
