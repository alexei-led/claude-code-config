# Claude Code Complete Guide

Comprehensive reference for commands, agents, skills, hooks, and scripts.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Commands](#commands)
- [Agents](#agents)
- [Skills](#skills)
- [Hooks](#hooks)
- [Scripts](#scripts)
- [MCP Integration](#mcp-integration)
- [Workflows](#workflows)

---

## Architecture Overview

### Command Flow

```mermaid
flowchart LR
    User[User] --> Command[/command]
    Command --> Skill{Skill<br/>WHEN}
    Skill --> Agent[Agent<br/>HOW]
    Agent --> Tool[Tool/CLI]
    Tool --> Summary[Summary]
    Summary --> User
```

### Hook System

```mermaid
flowchart LR
    subgraph Events
        SS[SessionStart]
        UPS[UserPromptSubmit]
        PTU[PreToolUse]
        POTU[PostToolUse]
    end

    subgraph Hooks
        SSS[session-start]
        SE[skill-enforcer]
        FP[file-protector]
        SL[smart-lint]
    end

    SS --> SSS
    UPS --> SE
    PTU --> FP
    POTU --> SL
```

---

## Master-Clone Pattern

**Key insight from Anthropic research**: Don't create highly specialized "expert" subagents. They're brittle and often underperform.

### The Pattern

Instead of creating custom specialists, **clone the main agent with a focused prompt**:

```
Main Agent (full capabilities)
    ├── Clone + "Review this Go code for security issues"
    ├── Clone + "Implement this feature following existing patterns"
    └── Clone + "Research best practices for X"
```

### Why It Works

1. **Same capabilities** - Clones inherit all tools, skills, and context
2. **Focused attention** - Narrow prompt = focused output
3. **No brittleness** - No custom logic that can break
4. **Parallel execution** - Multiple clones work simultaneously

### Implementation

Your engineer agents (`go-engineer`, `python-engineer`, `typescript-engineer`) follow this pattern:

```yaml
model: opus # Same powerful model
tools: [Read, Bash, Grep, Glob, ...] # Analysis tools (NO Edit/Write)
skills: [writing-go, looking-up-docs, ...] # Skill inheritance
---
You are an Expert Go Engineer... # Focused prompt

## Output Mode: Propose Only
Return structured proposals for main context to apply.
```

They analyze and propose changes but **do not apply edits directly**. This ensures:

- User approval for each edit
- No autonomous changes bypassing the approval loop
- Clean separation: subagents explore, main context implements

### When to Use Subagents

| Scenario               | Approach                         |
| ---------------------- | -------------------------------- |
| Deep code analysis     | Clone with analysis prompt       |
| Parallel exploration   | Multiple clones, different areas |
| Feature implementation | Engineer agent (focused clone)   |
| Research task          | Researcher agent (focused clone) |
| Simple lookup          | Direct MCP tool call (no agent)  |

### Anti-Patterns to Avoid

1. **Over-specialized agents** - Agent that only does one narrow thing
2. **Custom tool restrictions** - Limiting tools "for safety" often backfires
3. **Chained agents** - Agent A calls Agent B calls Agent C (fragile)
4. **Stateful agents** - Agents that need to remember across invocations

---

## Skill vs Agent vs Command

| Component   | When to Use                  | Context Impact            |
| ----------- | ---------------------------- | ------------------------- |
| **Skill**   | Inject knowledge/patterns    | Loaded on-demand, minimal |
| **Agent**   | Parallel work, deep analysis | Separate context window   |
| **Command** | User-invoked workflows       | Orchestrates agents/tools |

---

## Commands

### Code Quality (`/code:*`)

| Command              | Description                        | Example              |
| -------------------- | ---------------------------------- | -------------------- |
| `/code:fix`          | Zero-tolerance quality enforcement | `/code:fix`          |
| `/code:review`       | Multi-agent code review            | `/code:review deep`  |
| `/code:docs`         | Documentation updates              | `/code:docs`         |
| `/code:deploy-check` | K8s/CI validation                  | `/code:deploy-check` |
| `/code:commit`       | Smart commit grouping              | `/code:commit`       |

#### `/code:review` Modes

```bash
/code:review                 # Language engineers only
/code:review deep            # 6-12 specialized sub-agents
```

### Testing (`/test:*`)

| Command         | Description                 |
| --------------- | --------------------------- |
| `/test:e2e`     | E2E testing with Playwright |
| `/test:improve` | Improve test quality        |

### Spec-Driven (`/spec:*`)

| Command        | Description                      |
| -------------- | -------------------------------- |
| `/spec:init`   | Initialize feature specification |
| `/spec:gen`    | Generate from specification      |
| `/spec:work`   | Continue spec-driven work        |
| `/spec:status` | Check implementation progress    |
| `/spec:sync`   | Sync feature list from code      |

### Other Commands

| Command        | Description                           |
| -------------- | ------------------------------------- |
| `/docs:lookup` | Library docs via Context7             |
| `/research`    | Web research via Perplexity           |
| `/learn`       | Extract session learnings → CLAUDE.md |

---

## Agents

### Agent Hierarchy

```mermaid
flowchart TB
    subgraph Engineers[Language Engineers - opus]
        GE[go-engineer]
        PE[python-engineer]
        TE[typescript-engineer]
    end

    subgraph GoSpec[Go Specialists]
        GQ[go-qa]
        GT[go-tests]
        GI[go-impl]
        GID[go-idioms]
        GD[go-docs]
        GS[go-simplify]
    end

    subgraph PySpec[Python Specialists]
        PQ[py-qa]
        PT[py-tests]
        PI[py-impl]
        PID[py-idioms]
        PD[py-docs]
        PS[py-simplify]
    end

    GE -.-> GoSpec
    PE -.-> PySpec
```

### Language Engineers

| Agent                 | Model | Focus                              |
| --------------------- | ----- | ---------------------------------- |
| `go-engineer`         | opus  | Go development, clean architecture |
| `python-engineer`     | opus  | Python development, type safety    |
| `typescript-engineer` | opus  | TypeScript, React, strict typing   |

### Language Specialists (Deep Review)

**Go Specialists:**

| Agent         | Focus                                |
| ------------- | ------------------------------------ |
| `go-qa`       | Logic, security (OWASP), performance |
| `go-tests`    | Test quality, table-driven tests     |
| `go-impl`     | Requirements, DI, edge cases         |
| `go-idioms`   | Patterns, error handling, stdlib     |
| `go-docs`     | Documentation, comments              |
| `go-simplify` | Over-abstraction, dead code          |

**Python Specialists:**

| Agent         | Focus                        |
| ------------- | ---------------------------- |
| `py-qa`       | Logic, security, performance |
| `py-tests`    | pytest, fixtures, coverage   |
| `py-impl`     | Requirements, DI, edge cases |
| `py-idioms`   | PEP8, type hints, Protocols  |
| `py-docs`     | Docstrings, README           |
| `py-simplify` | Over-abstraction, dead code  |

**TypeScript Specialists:**

| Agent      | Focus                         |
| ---------- | ----------------------------- |
| `ts-tests` | Vitest, React Testing Library |
| `ts-docs`  | JSDoc, TSDoc, comments        |

### Infrastructure & Utility

| Agent                   | Model  | Focus                                |
| ----------------------- | ------ | ------------------------------------ |
| `infra-engineer`        | opus   | K8s, Terraform, Helm, GitHub Actions |
| `docs-keeper`           | sonnet | Documentation maintenance            |
| `pdf-parser`            | haiku  | PDF extraction and analysis          |
| `playwright-tester`     | opus   | E2E browser testing                  |
| `perplexity-researcher` | haiku  | Web research                         |

---

## Skills

Skills provide domain knowledge and trigger conditions.

```mermaid
flowchart LR
    Prompt[User Prompt] --> Enforcer[skill-enforcer hook]
    Enforcer --> |keywords| Skill[Skill Activated]
    Skill --> Agent[Spawn Agent]
    Agent --> Result[Summary]
```

### Available Skills

| Skill                 | Triggers When           |
| --------------------- | ----------------------- |
| `writing-go`          | Go development          |
| `writing-python`      | Python development      |
| `writing-typescript`  | TypeScript development  |
| `looking-up-docs`     | Library documentation   |
| `researching-web`     | Web research            |
| `searching-code`      | Codebase exploration    |
| `refactoring-fast`    | Batch refactoring       |
| `managing-infra`      | K8s, Terraform, CI/CD   |
| `using-cloud-cli`     | GCP, AWS CLI operations |
| `using-git-worktrees` | Parallel development    |
| `using-modern-cli`    | Modern CLI tools        |
| `testing-e2e`         | Playwright testing      |

---

## Hooks

### Hook Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Claude
    participant H as Hooks
    participant T as Tools

    U->>C: Prompt
    C->>H: UserPromptSubmit
    H-->>C: skill suggestions
    C->>T: Tool call
    H->>H: PreToolUse check
    T->>T: Execute
    T->>H: PostToolUse
    H-->>C: lint results
    C->>U: Response
```

### Active Hooks

| Hook                | Event            | Purpose                   |
| ------------------- | ---------------- | ------------------------- |
| `session-start.sh`  | SessionStart     | Project context on start  |
| `skill-enforcer.sh` | UserPromptSubmit | Suggests relevant skills  |
| `file-protector.sh` | PreToolUse       | Protects sensitive files  |
| `smart-lint.sh`     | PostToolUse      | Auto-lints modified files |
| `notify.sh`         | Notification     | Desktop notifications     |

### Configuration

Hooks read from `~/.claude/hook-config.json` for easy customization:

```json
{
  "fileProtector": { "protectedPatterns": [...] },
  "smartLint": { "excludePatterns": [...] },
  "performanceMonitor": { "contextWarningThreshold": 0.10 }
}
```

### smart-lint.sh

Auto-detects and lints:

| Language      | Tools                |
| ------------- | -------------------- |
| Go            | golangci-lint, gofmt |
| TypeScript/JS | prettier, eslint     |
| Python        | ruff, black, mypy    |
| YAML          | yamllint             |
| Shell         | shellcheck           |
| K8s           | kubeval, actionlint  |

---

## Scripts

### copilot-proxy.sh

Rate limit fallback using GitHub Copilot API.

```bash
~/.claude/scripts/copilot-proxy.sh           # Start
~/.claude/scripts/copilot-proxy.sh --status  # Check
~/.claude/scripts/copilot-proxy.sh --stop    # Stop
```

---

## MCP Integration

| Server                | Purpose               |
| --------------------- | --------------------- |
| `sequential-thinking` | Multi-step reasoning  |
| `context7`            | Library documentation |
| `perplexity-ask`      | Web research          |
| `playwright`          | E2E browser testing   |

---

## Workflows

### Feature Development

```mermaid
flowchart LR
    A[Design] --> B[Implement] --> C[Review] --> D[Commit]

    C -.- C1[/code:review]
    D -.- D1[/code:commit]
```

```bash
# implement...
/code:review deep
/code:commit
```

### Quick Quality

```bash
/code:fix  # Zero tolerance
```

### Pre-deployment

```bash
/code:deploy-check
```

---

## File Structure

```
~/.claude/
├── README.md           # Overview
├── GUIDE.md            # This file
├── CLAUDE.md           # Instructions
├── agents/             # Agent definitions
├── commands/           # Slash commands
├── skills/             # Domain knowledge
├── hooks/              # Event handlers
└── scripts/            # Helpers
```
