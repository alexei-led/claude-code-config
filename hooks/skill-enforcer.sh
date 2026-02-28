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
if echo "$PROMPT_LOWER" | grep -qE '\.go\b|go\.(mod|sum)|go (test|build|run|fmt|vet|mod|get|generate)|golangci|mockery|\bgolang\b|\bgoroutines?\b|\bchannel\b|\bdefer\b.*func|urfave|testify|cobra/|idiomatic go|in go\b|go (code|project|package|module|interface|struct)|write.*go|implement.*go|\berror\s*handling\b.*go'; then
	skills+="writing-go "
fi

# writing-python: Idiomatic Python 3.14+ development
# Triggers: .py files, Python commands, Python frameworks
if echo "$PROMPT_LOWER" | grep -qE '\.pyi?\b|pyproject|requirements\.txt|setup\.py|__init__|python[3]?\b|\buv (run|pip|sync|add|lock)|\bruff\b|pytest|poetry\b|mypy\b|django|flask|fastapi|pandas|numpy|pydantic|dataclass|type\s*hint|\btyping\b|asyncio|\basync\b.*\bawait\b|pip install|write.*python|implement.*python'; then
	skills+="writing-python "
fi

# writing-typescript: TypeScript development with strict typing
# Triggers: .ts files, TypeScript commands, Node.js/React/Bun
if echo "$PROMPT_LOWER" | grep -qE '\.(ts|tsx)\b|typescript|tsconfig|package\.json|\bnpm\b|\bbun\b|\byarn\b|\bvite\b|react|next\.?js|node\.?js|\bexpress\b|\best\b|vitest|jest|eslint|prettier|write.*typescript|implement.*ts|strict typing'; then
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

# refactoring-code: Fast batch refactoring via MorphLLM edit_file
# Triggers: Multi-file batch changes, style updates everywhere, complex prompt → many changes
if echo "$PROMPT_LOWER" | grep -qE 'refactor.*(across|multiple|batch|all|every)|batch.*(edit|rename|update|change)|rename.*(across|everywhere|all|every)|update.*(pattern|import|style).*everywhere|(multi[\s-]?file|cross[\s-]?file).*(refactor|update|change)|morphllm|edit_file|5\+?\s*files|same\s*pattern.*files|style.*every'; then
	skills+="refactoring-code "
fi

# reviewing-code: Multi-agent code review for security, quality, architecture
# Triggers: review, code review, check code, review changes, feedback on code
if echo "$PROMPT_LOWER" | grep -qE '\breview\b.*\b(code|changes|this|my|the)\b|\bcode\s*review\b|\bcheck\s*(this|my|the)?\s*code\b|\bdeep\s*(code\s*)?review\b|\bfeedback\s*(on)?\s*(my|the|this)?\s*code\b|review\s*(my|the|these)?\s*(changes|implementation|pr)\b|critique\s*(my|the|this)?\s*code'; then
	skills+="reviewing-code "
fi

# committing-code: Smart git commits with logical grouping
# Triggers: commit, save changes, create commit, bundle commits
if echo "$PROMPT_LOWER" | grep -qE '\bcommit\b|\bsave\s*(my|the)?\s*changes\b|\bcreate\s*(a\s*)?commit\b|\bbundle\s*commits?\b|\bgit\s*commit\b|\bcommit\s*(my|the|these)?\s*(changes|work|code)\b|\bsave\s*(my)?\s*work\b'; then
	skills+="committing-code "
fi

# fixing-code: Fix issues via parallel agents with zero tolerance
# Triggers: fix, fix issues, fix errors, fix bugs, fix lint, fix tests
if echo "$PROMPT_LOWER" | grep -qE '\bfix\s*(all|the|my|these|this|any)?\s*(issue|error|bug|problem|warning|lint|test|failure|type\s*error|build|compilation)s?\b|\bfix\s*(it|this|them|everything)\b|\bresolve\s*(the|all|these)?\s*(issue|error|bug)s?\b|\baddress\s*(the|all)?\s*(issue|error|warning)s?\b|make\s*(it|the|tests?|build)\s*(pass|work|green)\b'; then
	skills+="fixing-code "
fi

# documenting-code: Update documentation based on changes
# Triggers: update docs, document, add documentation, update readme, write docs
if echo "$PROMPT_LOWER" | grep -qE '\bupdate\s*(the|my)?\s*(docs|documentation|readme)\b|\bdocument\s*(this|the|my|these)?\s*(code|changes|function|api)?\b|\badd\s*(some|more)?\s*documentation\b|\bwrite\s*(the|some)?\s*docs\b|\bimprove\s*(the)?\s*documentation\b|\bdocstring|\bjsdoc\b|\bgodoc\b'; then
	skills+="documenting-code "
fi

# deploying-infra: Validate and deploy K8s, Terraform, Helm, GitHub Actions, Docker configs
# Triggers: deploy check, validate deployment, deploy to staging, terraform apply, helm upgrade, kubectl apply, rollout
if echo "$PROMPT_LOWER" | grep -qE '\bdeploy\s*check\b|\bcheck\s*(my|the)?\s*deploy(ment)?\b|\bvalidate\s*(my|the)?\s*(deployment|infrastructure|infra|k8s|kubernetes|helm|terraform|config)s?\b|\bcheck\s*(my|the)?\s*(k8s|kubernetes|helm|terraform|workflow|action)\s*(config|manifest|file)s?\b|\bverify\s*(the)?\s*infrastructure\b|\binfra\s*check\b|\bdeploy\s*to\s|apply\s*(the\s*)?(changes|infra)|terraform\s*apply|helm\s*(upgrade|install)|kubectl\s*apply|rollout'; then
	skills+="deploying-infra "
fi

# testing-e2e: E2E testing with Playwright MCP
# Triggers: e2e test, playwright, browser testing, UI automation
if echo "$PROMPT_LOWER" | grep -qE '\be2e\b.*\btest|\bplaywright\b|\bbrowser\s*(test|testing|automation)\b|\bui\s*(test|testing|automation)\b|\bend[\s-]?to[\s-]?end\b|\bvisual\s*(test|testing|regression)\b|\baccessibility\s*(test|testing|check)\b|\ba11y\s*(test|check)\b'; then
	skills+="testing-e2e "
fi

# writing-web: Simple web development with HTML, CSS, JS, HTMX
# Triggers: HTML, CSS, JS, web template, stylesheet, HTMX
if echo "$PROMPT_LOWER" | grep -qE '\bhtml\s*(template|file|page|component)?\b|\bcss\s*(style|file|class)?\b|\bstylesheet\b|\bhtmx\b|\bweb\s*(template|page|component|form)\b|\bhtml\s*and\s*css\b|\bvanilla\s*js\b|\bdom\s*manipulat|\.html\b|\.css\b'; then
	skills+="writing-web "
fi

# brainstorming-ideas: Collaborative design dialogue
# Triggers: brainstorm, design feature, explore approach, think through, ideate
if echo "$PROMPT_LOWER" | grep -qE '\bbrainstorm\b|\bideate\b|\bdesign\s*(a|an|this|the|new)?\s*(\w+\s+)?(feature|component|system|api|flow|architecture)\b|\bexplore\s*(approach|option|idea|design|alternative)s?\b|\bthink\s*through\b|\bbefore\s*(i|we)?\s*(implement|code|build|start)\b|\bplan\s*(out|this|the)?\s*(feature|implementation|design)\b|\bsketch\s*out\b|\bfigure\s*out\s*(how|what|the)\b|\bdesign\s*session\b|\bwhat\s*should\s*(i|we)\s*(build|implement|create)\b'; then
	skills+="brainstorming-ideas "
fi

# using-modern-cli: Modern CLI tools for better performance
# Triggers: grep/find/cat alternatives, bash scripts, command optimization
if echo "$PROMPT_LOWER" | grep -qE '\bripgrep\b|\brg\b.*search|\bfd\b.*find|\bbat\b.*file|\bsd\b.*replace|\beza\b|\bdust\b|\bprocs\b|\bmodern\s*cli\b|better\s*than\s*(grep|find|cat|sed|ls)|replace.*(grep|find|cat|sed|ls)|faster.*(search|find)|\.gitignore.*respect|bash\s*script|command.*chain|optimize.*(command|cli|shell)'; then
	skills+="using-modern-cli "
fi

# improving-tests: Review, refactor, and improve test quality
# Triggers: improve tests, refactor tests, test coverage, combine tests, table-driven, parametrize
if echo "$PROMPT_LOWER" | grep -qE '\bimprove\s*(my|the|these)?\s*tests?\b|\brefactor\s*(my|the|these)?\s*tests?\b|\btest\s*coverage\b|\bcombine\s*(the|my)?\s*tests?\b|\btable[\s-]?driven\b|\bparametri[sz]e\b|\btest\.each\b|\beliminate\s*test\s*waste\b|\btest\s*(quality|improvement|cleanup)\b'; then
	skills+="improving-tests "
fi

# learning-patterns: Extract learnings and generate customizations
# Triggers: learn, learnings, adapt config, session patterns
if echo "$PROMPT_LOWER" | grep -qE '\blearn\b.*\b(from|session|pattern|conversation)\b|\bextract\s*(the)?\s*learnings?\b|\bwhat\s*did\s*(we|i)\s*learn\b|\bsave\s*(the)?\s*learnings?\b|\badapt\s*(the|my)?\s*(config|configuration|settings)\b|\bsession\s*learnings?\b|\bimprove\s*claude\s*code\b|\bcustomiz.*(claude|config)\b|\b(learn|record)\s*from\s*(this|the|our)\s*(session|conversation|chat)\b'; then
	skills+="learning-patterns "
fi

# frontend-design: Create distinctive frontend interfaces
# Triggers: UI design, frontend, web component, page design, interface
if echo "$PROMPT_LOWER" | grep -qE '\bfrontend\s*design\b|\bui\s*design\b|\bdesign\s*(a|an|the|this)?\s*(ui|interface|page|component|landing|dashboard|form)\b|\bcreate\s*(a|an)?\s*(web|frontend)?\s*(component|page|interface)\b|\bpolished\s*(ui|design|interface)\b|\bproduction[\s-]?grade\s*(ui|frontend|interface)\b|\bdistinctive\s*(ui|design|interface)\b|\bavoid.*(generic|ai).*aesthetic'; then
	skills+="frontend-design:frontend-design "
fi

# spec:status: Progress overview for spec-driven projects
# Triggers: project status, progress, how far along, spec status
if echo "$PROMPT_LOWER" | grep -qE '\b(project|spec|task)\s*(status|progress|overview)\b|\bhow\s*(far|much|many|is)\s*(along|done|progress|left|remain|complete)\b|\bwhat.*(done|left|remain|progress|status)\b|\bshow\s*(me\s*)?(progress|status|overview)\b|\bhow.*project\s*(going|doing)\b'; then
	skills+="spec:status "
fi

# spec:help: Quick methodology guide for spec-driven development
# Triggers: how does spec work, spec guide, spec methodology
if echo "$PROMPT_LOWER" | grep -qE '\bhow\s*does\s*spec\b|\bspec\s*(guide|help|methodology|workflow|reference)\b|\bspec[\s-]driven\s*(guide|help|how)\b|\bwhat\s*(are|is)\s*(the)?\s*spec\s*(command|workflow|phase)'; then
	skills+="spec:help "
fi

# spec:work: Main workflow - select, plan, implement, verify
# Triggers: start/continue spec work, next task, work on task
if echo "$PROMPT_LOWER" | grep -qE '\b(start|begin|continue|resume)\s*(spec\s*)?(work|task|implementation)\b|\bnext\s*(ready\s*)?(task|work)\b|\bwork\s*on\s*(the\s*)?(next|a)\s*task\b|\bspec[\s:]work\b|\bpick\s*up\s*(a\s*)?(new\s*)?task\b'; then
	skills+="spec:work "
fi

# Output only if skills detected (silent when no match)
if [[ -n "$skills" ]]; then
	skills="${skills% }"
	echo "→ Consider skills: $skills"
fi
# Silent exit when no skills detected - reduces context noise
