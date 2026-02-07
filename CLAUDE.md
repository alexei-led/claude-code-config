# Development Partnership

Build production-quality code together. My guidance helps when you're stuck—ask for it.

## Critical Workflow

### Research → Plan → Implement

**IMPORTANT**: Follow this sequence for every implementation task:

1. **Research**: Explore the codebase, understand existing patterns
2. **Plan**: Create a detailed implementation plan and verify it with me
3. **Implement**: Execute the plan with validation checkpoints

### Automated Checks are Mandatory

**IMPORTANT**: All hook issues are BLOCKING. Fix ALL issues before continuing.

When hooks report issues (exit code 2):

1. **Stop immediately** and address all issues
2. **Fix every issue** until everything is GREEN
3. **Verify the fix** by re-running the failed command
4. **Resume your original task** with todo list awareness

### Reality Checkpoints

**Stop and validate** at these moments:

- After implementing a complete feature
- Before starting a new major component
- When something feels wrong
- Before declaring "done"

Run: `make fmt && make test && make lint`

## Spec-Driven Development

### Distributed Spec System (.spec/)

Detected by `.spec/` folder. Markdown + YAML frontmatter, one file per task/requirement.

**Structure:**

```
.spec/
├── reqs/           # REQ-*.md (WHAT - requirements)
├── epics/          # EPIC-*.md (grouping tasks)
├── tasks/          # TASK-*.md (HOW - implementation)
├── memory/         # pitfalls.md, conventions.md, decisions.md
├── SESSION.yaml    # Current session state (auto-managed)
└── PROGRESS.md     # Activity log (last 10 entries)
```

**Task Status:** `todo`, `in_progress`, or `done`

**Abstraction levels:**
| Location | Level | Contains |
|----------|-------|----------|
| `.spec/reqs/` | WHAT | Success criteria, constraints |
| `.spec/tasks/` | HOW | Implementation steps, acceptance criteria |

**Commands (8 total):**
| Command | Purpose |
|---------|---------|
| `/spec:init` | Initialize project |
| `/spec:interview` | Deep questioning → REQ-\*.md |
| `/spec:plan` | Create EPIC + TASK files from REQ |
| `/spec:work` | Main workflow - select, plan, implement, verify |
| `/spec:status` | Progress overview |
| `/spec:new` | Create new task or requirement |
| `/spec:done` | Mark complete with evidence |
| `/spec:help` | Methodology quick reference |

**Quick queries:**

```bash
specctl status                # Progress overview
specctl ready                 # Next tasks (priority-ordered)
specctl session show          # Current session state
specctl validate              # Check for issues
```

**Agent:** `spec-planner` — Creates implementation plans with style learning

**One Task Per Session:** Focus on ONE task. Complete it fully before starting another.

### Task Completion Protocol

**NEVER** mark done until ALL pass:

1. **Build**: `make build` - compiles clean
2. **Test**: `make test` - ALL tests pass
3. **Lint**: `make lint` - ZERO issues
4. **Verify**: Manual or E2E verification

### Context Recovery

If session was interrupted:

1. Run `specctl session resume` for recovery info (task, step, base commit)
2. Check `git status` for uncommitted changes
3. Check current branch - if on `task/*`, continue that task
4. Run `/spec:work` which auto-detects and resumes from SESSION.yaml

## Tools & Agents

### MCP Tools

**Sequential Thinking**: See @MCP_Sequential.md for complex debugging/architecture (3+ components).

**MorphLLM**: Use `edit_file` for batch refactoring, `warpgrep_codebase_search` for codebase understanding. Details in searching-code and refactoring-code skills.

### Use Multiple Agents

_Leverage subagents aggressively_ for better results:

- Spawn agents to explore different parts of the codebase in parallel
- Use one agent to write tests while another implements features
- For complex refactors: One agent identifies changes, another implements them

### Agent Teams

Coordinate parallel Claude Code sessions. Each teammate has own context window.

| Scenario                                     | Use      | Why                                       |
| -------------------------------------------- | -------- | ----------------------------------------- |
| Code review, competing hypotheses            | Teams    | Reviewers challenge each other's findings |
| Independent modules/layers                   | Teams    | Each teammate owns separate files         |
| Cross-layer changes (frontend+backend+infra) | Teams    | Parallel development, no conflicts        |
| Research, sequential deps, same-file edits   | Subagent | Simple report-back, no conflicts          |

Size tasks as self-contained units, assign different files to avoid conflicts. Teams cost more tokens—worth it for parallel exploration/review, not for routine tasks.

### Subagent Resumption

Long-running agents return an `agentId`. Resume with Task tool's `resume` parameter or `/agent:resume`.

## Working Memory

When context gets long:

- Re-read this CLAUDE.md file
- Summarize progress in PROGRESS.md
- Document current state before major changes

Maintain TODO.md structure: Current Task → Completed → Next Steps

## Problem-Solving

When stuck or confused:

1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Spawn agents for parallel investigation
3. **Simplify** - The simple solution is usually correct
4. **Ask** - Present alternatives and ask for preference

## Performance & Security

- No premature optimization—benchmark before claiming faster
- Validate all inputs at system boundaries
- Prepared statements for SQL (never concatenate!)

## Usage Optimization

Agents, skills, and commands have explicit model settings to reduce 5-hour usage.

### Environments

Switch providers with `ce <env>`:

| Environment | Provider                   | Best For                        |
| ----------- | -------------------------- | ------------------------------- |
| `default`   | Anthropic API              | Standard development            |
| `vertex`    | Vertex AI                  | Enterprise, GCP integration     |
| `codex`     | OpenAI Codex (CLIProxyAPI) | Code completion, fast iteration |
| `gemini`    | Gemini (CLIProxyAPI)       | Large context, multimodal       |
| `deepseek`  | DeepSeek                   | Reasoning, cost-effective       |
| `zai`       | Z.ai                       | Alternative provider            |

CLIProxyAPI environments (codex, gemini) require `cliproxy.sh` running on localhost:8317.

### Model Selection

| Model  | Use For                                              |
| ------ | ---------------------------------------------------- |
| Opus   | Architecture, security analysis, complex debugging   |
| Sonnet | Implementation, testing, documentation, coordination |
| Haiku  | Discovery, CLI help, lookups, progress, simple tasks |

### Token Efficiency

- Request concise output: "5 lines max", "JSON only", "bullet points"
- Use summaries instead of full file dumps
- Fork heavy analysis (`context: fork`) to avoid main context pollution
- Batch related edits in single tool calls

### Optimized Components

**Haiku**: go-docs, py-docs, ts-docs, web-docs, looking-up-docs, using-cloud-cli, using-modern-cli, agent:resume, spec:status, spec:done, spec:new
**Sonnet**: docs-keeper, playwright-tester, spec-planner, researching-web, checking-deploy, testing-e2e, spec:init, spec:work, code:deploy

## Working Together

- This is always a feature branch—no backwards compatibility needed
- When in doubt, choose clarity over cleverness
- Avoid complex abstractions or "clever" code—the simple solution is usually better
- Never add refactoring-style comments
- Comments: lean, informative, useful and short—only when helpful. No comments in tests
- **REMINDER**: If this file hasn't been referenced in 30+ minutes, RE-READ IT!
