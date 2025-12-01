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
[[ "$PROMPT_LOWER" =~ skill\( ]] && exit 0

skills=""

# go-patterns: Go development
# Triggers: .go files, go commands, Go-specific terms
if echo "$PROMPT_LOWER" | grep -qE '\.go\b|go\.(mod|sum)|go (test|build|run|fmt|vet|mod|get|generate)|golangci|mockery|\bgolang\b|\bgoroutine|\bchannel\b|\bdefer\b.*func|urfave|testify|cobra/|idiomatic go|in go\b|go (code|project|package|module|interface|struct)'; then
	skills+="go-patterns "
fi

# python-dev: Python development
# Triggers: .py files, Python commands, Python frameworks
if echo "$PROMPT_LOWER" | grep -qE '\.pyi?\b|pyproject|requirements\.txt|setup\.py|__init__|python[3]?\b|\buv (run|pip|sync|add|lock)|\bruff\b|pytest|poetry\b|mypy\b|django|flask|fastapi|pandas|numpy|pydantic|dataclass|type hint|asyncio|pip install'; then
	skills+="python-dev "
fi

# infra-k8s: Kubernetes/Terraform/Infrastructure
# Triggers: K8s resources, IaC tools, container orchestration
if echo "$PROMPT_LOWER" | grep -qE '\.tf\b|\.tfvars|dockerfile|docker-compose|chart\.yaml|kustomization|values\.yaml|\bkubectl\b|\bhelm\b|\bkustomize\b|\bterraform\b|kubernetes|k8s\b|\bpod[s]?\b|\bdeployment[s]?\b|\bingress\b|\bconfigmap|\bnamespace[s]?\b|\breplica[s]?\b|\bstatefulset|\bdaemonset|cronjob|\bhpa\b|networkpolic|\bcluster\b.*(deploy|scale|node|config)|manifest|container.*(image|registry|port)|service\s*account|node\s*pool'; then
	skills+="infra-k8s "
fi

# cloud-cli: GCP/AWS cloud CLI patterns
# Triggers: Cloud provider CLIs, cloud services
if echo "$PROMPT_LOWER" | grep -qE '\bgcloud\b|\bgsutil\b|\bbq\s|\baws\s|\baz\s|bigquery|cloud\s*(run|function|sql|storage)|gke\b|gcs\b|pubsub|dataflow|firestore|spanner|\bs3\b|\bec2\b|aws.*lambda|lambda.*(function|handler)|\becs\b|\beks\b|\brds\b|dynamodb|\bsqs\b|\bsns\b|cloudformation|cloudwatch|service\s*account|iam.*(role|policy|permission)|\bbucket[s]?\b|--project\b|--region\b'; then
	skills+="cloud-cli "
fi

# looking-up-docs: Documentation lookup
# Triggers: Explicit doc-seeking language
if echo "$PROMPT_LOWER" | grep -qE '\bdocs\b|\bdocumentation\b|api\s*(reference|docs)|look\s*up.*(docs|api|syntax|usage|reference)|find.*(docs|documentation|reference)|check.*(docs|documentation)|man\s*page|reference.*(guide|manual)|rtfm|read\s*the\s*docs|official.*(docs|documentation)'; then
	skills+="looking-up-docs "
fi

# researching-web: Web research with Perplexity
# Triggers: Research language, comparisons, current info requests
if echo "$PROMPT_LOWER" | grep -qE '\bresearch\b|search.*(web|online)|look\s*up.*online|find\s*out.*(about|if|whether)|compare.*(tool|lib|framework|approach|option|technolog)|(\w+)\s+vs\s+(\w+)|pros\s*(and|&)\s*cons|trade[\s-]?off.*(between|of|for|consider)|which.*(better|should|recommend)|latest.*(version|release|update)|current.*(version|best)|what.?s\s*new\s*in|best\s*practice|recommended.*(way|approach|pattern)|up[\s-]?to[\s-]?date|2024|2025'; then
	skills+="researching-web "
fi

# reviewing-code: Code review with Codex
# Triggers: Review requests, bug finding, security audit
if echo "$PROMPT_LOWER" | grep -qE 'review.*(code|this|my|pr|pull|change|implementation|file)|code\s*review|check.*(code|implementation|this).*(for|quality)|find.*(bug|issue|problem)|security.*(audit|review|check|scan)|vulnerabil|code.*(quality|smell)|potential.*(issue|bug|problem|vulnerabil)|what.?s\s*wrong\s*with.*(code|this|implementation)|audit.*(code|security)'; then
	skills+="reviewing-code "
fi

# using-git-worktrees: Git worktrees for isolation
# Triggers: Explicit worktree or isolation intent
if echo "$PROMPT_LOWER" | grep -qE 'worktree|git\s*worktree|isolat.*(work|branch|develop|implement|environment)|separate.*(workspace|environment|branch)|parallel.*(branch|work|develop)|work.*(multiple|parallel).*branch|clean.*(workspace|environment|slate)|fresh.*(workspace|environment|branch)'; then
	skills+="using-git-worktrees "
fi

# consulting-design: Design consultation with Gemini
# Triggers: Architecture decisions, design trade-offs, brainstorming
if echo "$PROMPT_LOWER" | grep -qE '\barchitect|\bsystem\s*design|design\s*pattern|component.*(design|architect)|trade[\s-]?off.*(between|of|for|consider)|alternative.*(approach|solution|design|way|option|method)|which.*(approach|way|design|method|pattern).*(better|should|recommend|prefer)|how\s*should.*(design|architect|structure|approach|organize)|brainstorm.*(solution|idea|approach|option|way)|explore.*(option|possibilit|approach|alternative|idea)|evaluate.*(approach|design|option|trade|architectur)'; then
	skills+="consulting-design "
fi

# Output only if skills detected (minimal context footprint)
if [[ -n "$skills" ]]; then
	# Trim trailing space
	skills="${skills% }"
	echo "→ ACTIVATE: $skills"
fi
