# Skill eval roadmap

The current suite covers all 36 skills with 71 eval cases. Use this roadmap for adding the next layer of tests without turning the suite into expensive confetti.

## Groups

### 1. Coding execution loop

Skills: `coding`, `fixing-code`, `improving-tests`, `refactoring-code`, `documenting-code`, `committing-code`.

Focus:

- assumptions before implementation
- repro before fix
- one issue at a time
- behavior-first tests
- safe commit grouping
- verification after changes

### 2. Code understanding and review

Skills: `searching-code`, `smart-explore`, `reviewing-code`, `improve-codebase-architecture`, `reviewing-cc-config`, `linting-instructions`.

Focus:

- scoped code maps, not repo dumps
- evidence-backed findings
- architecture vs line-level cleanup boundaries
- token-efficient exploration
- config/prompt review boundaries

### 3. Language and platform implementation

Skills: `writing-go`, `writing-python`, `writing-typescript`, `writing-web`, `testing-e2e`, `playwright-skill`.

Focus:

- language-specific idioms
- verification commands
- framework boundaries
- internal helper activation guards

### 4. External information and second opinions

Skills: `context7-cli`, `looking-up-docs`, `researching-web`, `exploring-repos`, `using-gemini`, `mem-history`.

Focus:

- Context7 CLI docs lookup vs broad research
- current sources and citations
- no private-code leakage to external tools
- second-opinion results are verified, not trusted blindly
- memory/history is queried, not invented

### 5. Infrastructure and operations

Skills: `managing-infra`, `deploying-infra`, `using-cloud-cli`.

Focus:

- design vs deployment boundaries
- account/project/namespace confirmation
- dry-run/plan before apply
- explicit confirmation before destructive work
- rollback and verification

### 6. Planning, thinking, and collaboration

Skills: `brainstorming-ideas`, `debating-ideas`, `grill-me`, `learning-patterns`, `ccgram-messaging`, `using-git-worktrees`.

Focus:

- brainstorming vs debate vs grilling boundaries
- reusable learning extraction
- inter-agent messaging workflow
- worktrees only when isolation is warranted

### 7. Developer utilities and usage analysis

Skills: `using-modern-cli`, `analyzing-usage`, `evolving-config`.

Focus:

- concrete modern CLI rewrites
- usage/cost/burn-rate analysis
- scoped config evolution, not rewrites

## Additional cases to add next

### Command-level operational cases

Many current prompts ask the model to describe a workflow. Add cases that require concrete command sequences without mutating state:

- `committing-code` — show `git status`, `git diff`, `git log`, safe `git add` groups.
- `fixing-code` — show exact narrow test command and broader verification.
- `deploying-infra` — show dry-run/plan commands and explicit approval gates.
- `analyzing-usage` — show concrete `ccusage` commands.
- `ccgram-messaging` — show concrete inbox/send/broadcast commands.

### Neighboring-skill routing matrix

Add explicit boundary pairs where the wrong skill is tempting:

- `looking-up-docs` vs `researching-web`
- `brainstorming-ideas` vs `grill-me` vs `debating-ideas`
- `reviewing-code` vs `reviewing-cc-config`
- `writing-web` vs `writing-typescript`
- `managing-infra` vs `deploying-infra`
- `coding` vs language-specific implementation skills

Assertions should require naming the better route and avoiding the wrong workflow.

### Privacy and secret leakage

Add fixtures with fake secrets/private paths and require safe handling:

- `researching-web` — do not paste private code/secrets into web tools.
- `using-gemini` — scope what is sent externally.
- `committing-code` — never stage `.env`, PEM, credentials.
- `deploying-infra` / `using-cloud-cli` — confirm account/project before destructive operations.

### Verification discipline

Add cases that require final verification commands:

- `writing-go` — `go test ./...`, race/vet when relevant.
- `writing-python` — `ruff`, `pyright`, `pytest`.
- `writing-typescript` — `tsc --noEmit`, `bun test`, lint.
- `writing-web` — browser/manual/Playwright smoke check.
- `documenting-code` — `git diff --stat`, links/examples/placeholders.

### Artifact-producing cases

Add cases that produce or inspect artifacts, not just text:

- `testing-e2e` — traces/screenshots/reports on failure.
- skill eval infrastructure — summary Markdown and HTML report presence.
- `analyzing-usage` — chart/calendar output.
- `searching-code` — code map with read-next files.

### Codex/Gemini overlay parity

Run the same eval fixtures against `SKILL_EVAL_SOURCE=skills-codex` before trusting Codex/Gemini exported skills. Add assertions for platform-neutral wording: no Claude-only tool names, no missing flat skill links, and no stale Gemini context. Use `make validate` for Pi export checks: no banned Pi tool names, valid frontmatter, resolved local links, and executable support scripts.

### Internal-skill activation guards

Internal/non-user-invocable skills should have direct-invocation tests:

- `coding`
- `refactoring-code`
- `using-modern-cli`
- `playwright-skill`

Expected behavior: use the skill as support only, or route to the user-facing skill when directly invoked.

## Lessons from the first full run

- Boundary/routing tests find the most useful failures.
- Positive assertions grade better than negative assertions.
- Some skills contain good instructions but the target model omits them unless the eval prompt asks for command-level detail.
- Treat `WITH-SKILL FAILURES TO FIX` as the action list.
- Treat `WITHOUT-SKILL FAILURES` as lift signal, not a bug.
- If a judge result is wrong, tighten the assertion before weakening the skill. Annoying, but cheaper than lying to yourself.
