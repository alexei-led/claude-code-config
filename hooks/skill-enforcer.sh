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

# researching-web: Web search via Perplexity AI
# Triggers: Research language, comparisons, current info requests
if echo "$PROMPT_LOWER" | grep -qE '\bresearch\b|search.*(web|online)|look\s*up.*online|find\s*out.*(about|if|whether)|compare.*(tool|lib|framework|approach|option|technolog)|(\w+)\s+vs\s+(\w+)|pros\s*(and|&)\s*cons|trade[\s-]?off|which.*(better|should|recommend)|latest.*(version|release|update)|current.*(version|best)|what.?s\s*new\s*in|best\s*practice|up[\s-]?to[\s-]?date|2024|2025'; then
	skills+="researching-web "
fi

# asking-codex: Code review, bug detection, security analysis
# Triggers: Review requests, bug finding, security audit, quality concerns
if echo "$PROMPT_LOWER" | grep -qE 'review.*(code|this|my|pr|pull|change|implementation|file)|code\s*review|check.*(code|implementation|this).*(for|quality)|find.*(bug|issue|problem)|security.*(audit|review|check|scan)|vulnerabil|code.*(quality|smell)|potential.*(issue|bug|problem|vulnerabil)|what.?s\s*wrong\s*with.*(code|this|implementation)|audit.*(code|security)|\bbug\b|\bissue\b.*code|\bvulnerability\b|\baudit\b'; then
	skills+="asking-codex "
fi

# using-git-worktrees: Isolated git worktree management
# Triggers: Explicit worktree or isolation intent for feature work
if echo "$PROMPT_LOWER" | grep -qE 'worktree|git\s*worktree|isolat.*(work|branch|develop|implement|environment)|separate.*(workspace|environment|branch)|parallel.*(branch|work|develop)|work.*(multiple|parallel).*branch|clean.*(workspace|environment|slate)|fresh.*(workspace|environment|branch)|feature.*isolation'; then
	skills+="using-git-worktrees "
fi

# asking-gemini: Architecture alternatives, design trade-offs, brainstorming
# Triggers: Architecture decisions, design trade-offs, brainstorming, SCAMPER, design thinking
if echo "$PROMPT_LOWER" | grep -qE '\barchitect|\bsystem\s*design|design\s*pattern|component.*(design|architect)|alternative.*(approach|solution|design|way|option|method)|which.*(approach|way|design|method|pattern).*(better|should|recommend|prefer)|how\s*should.*(design|architect|structure|approach|organize)|brainstorm.*(solution|idea|approach|option|way)|explore.*(option|possibilit|approach|alternative|idea)|evaluate.*(approach|design|option|trade|architectur)|design.*decision|\bdecision\b|\boptions\b|\brecommend\b|scamper|design[\s-]?thinking|divergent[\s-]?thinking|convergent[\s-]?thinking|lateral[\s-]?thinking|creative[\s-]?(problem|solution)|ideation|generate.*(idea|option|alternative)'; then
	skills+="asking-gemini "
fi

# researching-web-gemini: Web research via Gemini with Google Search grounding
# Triggers: Google search, real-time info, current events, technology updates
if echo "$PROMPT_LOWER" | grep -qE 'google\s*(search|for)|search.*google|real[\s-]?time.*(info|data|search)|current.*(event|news|info|status)|live.*(data|info|update)|latest.*(news|update|info)|breaking.*(news|update)|today.?s.*(news|update)|search.*(current|latest|recent)|grounded.*(search|info)'; then
	skills+="researching-web-gemini "
fi

# analyzing-media: Image/PDF analysis via Gemini multimodal
# Triggers: PDF analysis, image analysis, screenshot analysis, diagram interpretation, OCR
if echo "$PROMPT_LOWER" | grep -qE '\.pdf\b|pdf\s*(file|document|analysis|extract|read|parse|content)|analyze.*(image|screenshot|diagram|pdf|photo|picture)|extract.*(from|text|data|table).*(pdf|image|screenshot)|read.*(pdf|image|screenshot)|interpret.*(diagram|chart|graph|visual|image)|screenshot.*(analysis|interpret|read)|ocr\b|document.*(extract|analysis|scan)|image.*(analysis|interpret|understand)|flowchart|architecture\s*diagram|erd\b|er\s*diagram|visual.*(analysis|content)|multimodal'; then
	skills+="analyzing-media "
fi

# generating-shell: Shell command generation via Gemini
# Triggers: Shell commands, bash scripts, unix pipes, awk/sed/grep
if echo "$PROMPT_LOWER" | grep -qE 'generate.*(shell|bash|command|script|pipe)|create.*(shell|bash|command|script)|write.*(shell|bash|script)|shell\s*(command|script|one[\s-]?liner)|bash\s*(command|script|one[\s-]?liner)|unix\s*(pipe|pipeline|command)|awk.*(command|script|pipe)|sed.*(command|script|pipe)|grep.*(command|pipe)|find.*(command|pipe)|complex.*(pipe|pipeline|command)|one[\s-]?liner|command[\s-]?line.*(for|to)|how\s*to.*(shell|bash|terminal|command[\s-]?line)|terminal\s*(command|script)'; then
	skills+="generating-shell "
fi

# testing-e2e: E2E testing with Playwright MCP
# Triggers: E2E tests, Playwright, browser testing, UI automation, HTMX testing
if echo "$PROMPT_LOWER" | grep -qE 'e2e\s*(test|testing)|end[\s-]?to[\s-]?end\s*(test|testing)|playwright|browser\s*(test|automation)|ui\s*(test|testing|automation)|visual\s*(test|regression)|accessibility\s*(test|check)|htmx\s*(test|testing)|test.*htmx|integration\s*test.*web|web\s*ui\s*test|selenium|cypress|puppeteer|headless\s*browser'; then
	skills+="testing-e2e "
fi

# Output only if skills detected (silent when no match)
if [[ -n "$skills" ]]; then
	skills="${skills% }"
	echo "→ Consider skills: $skills"
fi
# Silent exit when no skills detected - reduces context noise
