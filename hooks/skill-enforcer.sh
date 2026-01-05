#!/bin/bash
# Skill-enforcer hook - detects relevant skills from prompt and suggests activation
# Outputs minimal context only when skills detected; silent otherwise

set -euo pipefail

# Read prompt from stdin (JSON input from Claude Code)
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // .' 2>/dev/null || echo "$INPUT")
PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')

# Skip if prompt too short (likely greeting/command)
[[ ${#PROMPT_LOWER} -lt 10 ]] && exit 0

# Skip if user is already explicitly activating skills
[[ "$PROMPT_LOWER" =~ [Ss]kill\( ]] && exit 0

# Skip common follow-up patterns
[[ "$PROMPT_LOWER" =~ ^(yes|no|ok|okay|sure|thanks|continue|proceed|go\ ahead|do\ it|looks\ good|lgtm)$ ]] && exit 0

skills=""

# writing-go: Idiomatic Go 1.25+ development
# Triggers: .go files, go commands, Go-specific terms
if echo "$PROMPT_LOWER" | grep -qE '\.go\b|go\.(mod|sum)|go (test|build|run|fmt|vet|mod|get|generate)|golangci|mockery|\bgolang\b|\bgoroutine|\bchannel\b|\bdefer\b.*func|urfave|testify|cobra/|idiomatic go|in go\b|go (code|project|package|module|interface|struct)|write.*go|implement.*go'; then
	skills+="writing-go "
fi

# writing-python: Idiomatic Python 3.14+ development
# Triggers: .py files, Python commands, Python frameworks
if echo "$PROMPT_LOWER" | grep -qE '\.pyi?\b|pyproject|requirements\.txt|setup\.py|__init__|python[3]?\b|\buv (run|pip|sync|add|lock)|\bruff\b|pytest|poetry\b|mypy\b|django|flask|fastapi|pandas|numpy|pydantic|dataclass|type hint|asyncio|pip install|write.*python|implement.*python'; then
	skills+="writing-python "
fi

# writing-typescript: TypeScript development with strict typing
# Triggers: .ts files, TypeScript commands, Node.js/React/Bun
if echo "$PROMPT_LOWER" | grep -qE '\.tsx?\b|typescript|tsconfig|package\.json|\bnpm\b|\bbun\b|\byarn\b|\bvite\b|react|next\.?js|node\.?js|\bexpress\b|\best\b|vitest|jest|eslint|prettier|write.*typescript|implement.*ts|strict typing'; then
	skills+="writing-typescript "
fi

# managing-infra: K8s, Terraform, Helm, Kustomize, GitHub Actions
# Triggers: K8s resources, IaC tools, container orchestration, CI/CD
if echo "$PROMPT_LOWER" | grep -qE '\.tf\b|\.tfvars|dockerfile|docker-compose|chart\.yaml|kustomization|values\.yaml|\bkubectl\b|\bhelm\b|\bkustomize\b|\bterraform\b|kubernetes|k8s\b|\bpod[s]?\b|\bdeployment[s]?\b|\bingress\b|\bconfigmap|\bnamespace[s]?\b|\breplica[s]?\b|\bstatefulset|\bdaemonset|cronjob|\bhpa\b|networkpolic|manifest|container.*(image|registry|port)|service\s*account|node\s*pool|github.*action|\.github/workflows|workflow.*yaml'; then
	skills+="managing-infra "
fi

# using-cloud-cli: GCP/AWS cloud CLI patterns
# Triggers: Cloud provider CLIs, cloud services, BigQuery
if echo "$PROMPT_LOWER" | grep -qE '\bgcloud\b|\bgsutil\b|\bbq\s|\baws\s|bigquery|cloud\s*(run|function|sql|storage)|gke\b|gcs\b|pubsub|dataflow|firestore|spanner|\bs3\b|\bec2\b|aws.*lambda|lambda.*(function|handler)|\becs\b|\beks\b|\brds\b|dynamodb|\bsqs\b|\bsns\b|cloudformation|cloudwatch|iam.*(role|policy|permission)|\bbucket[s]?\b|--project\b|--region\b'; then
	skills+="using-cloud-cli "
fi

# looking-up-docs: Library documentation via Context7
# Triggers: Explicit doc-seeking language, API reference needs
if echo "$PROMPT_LOWER" | grep -qE '\bdocs\b|\bdocumentation\b|api\s*(reference|docs)|look\s*up.*(docs|api|syntax|usage|reference)|find.*(docs|documentation|reference)|check.*(docs|documentation)|man\s*page|reference.*(guide|manual)|how (to|do|does).*work|official.*(docs|documentation)|library.*docs|version.*specific'; then
	skills+="looking-up-docs "
fi

# researching-web: Web research via Perplexity AI (best practices, comparisons, standards)
# Triggers: Research language, comparisons, best practices, industry standards
if echo "$PROMPT_LOWER" | grep -qE '\bresearch\b|search.*(web|online)|look\s*up.*online|find\s*out.*(about|if|whether)|compare.*(tool|lib|framework|approach|option|technolog)|(\w+)\s+vs\s+(\w+)|pros\s*(and|&)\s*cons|trade[\s-]?off|which.*(better|should|recommend)|latest.*(version|release|update)|current.*(version|best)|what.?s\s*new\s*in|best\s*practice|up[\s-]?to[\s-]?date|2024|2025|2026|industry\s*standard|owasp|recommended\s*(practice|approach|pattern)|perplexity'; then
	skills+="researching-web "
fi

# using-git-worktrees: Isolated git worktree management
# Triggers: Explicit worktree or isolation intent for feature work
if echo "$PROMPT_LOWER" | grep -qE 'worktree|git\s*worktree|isolat.*(work|branch|develop|implement|environment)|separate.*(workspace|environment|branch)|parallel.*(branch|work|develop)|work.*(multiple|parallel).*branch|clean.*(workspace|environment|slate)|fresh.*(workspace|environment|branch)|feature.*isolation'; then
	skills+="using-git-worktrees "
fi

# searching-code: Intelligent codebase search via WarpGrep
# Triggers: Understanding code flow, tracing, cross-file exploration, large repos
if echo "$PROMPT_LOWER" | grep -qE 'how\s*does.*work|trace.*(flow|data|request|call)|understand.*(codebase|code|flow|architecture)|find\s*all.*(implementation|usage|call|reference)|cross[\s-]?file|multi[\s-]?hop|where.*implemented|explore.*(codebase|code)|large\s*repo|warpgrep|intelligent\s*search|reason.*about.*code'; then
	skills+="searching-code "
fi

# refactoring-fast: Fast batch refactoring via MorphLLM edit_file
# Triggers: Multi-file batch changes, style updates everywhere, complex prompt → many changes
if echo "$PROMPT_LOWER" | grep -qE 'refactor.*(across|multiple|batch|all|every)|batch.*(edit|rename|update|change)|rename.*(across|everywhere|all|every)|update.*(pattern|import|style).*everywhere|(multi[\s-]?file|cross[\s-]?file).*(refactor|update|change)|morphllm|edit_file|5\+?\s*files|same\s*pattern.*files|style.*every'; then
	skills+="refactoring-fast "
fi

# Output only if skills detected (silent when no match)
if [[ -n "$skills" ]]; then
	skills="${skills% }"
	echo "→ Consider skills: $skills"
fi
# Silent exit when no skills detected - reduces context noise
