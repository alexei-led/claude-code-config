# Claude Code Configuration

Production-quality setup with specialized agents and zero-tolerance quality enforcement.

---

## Quick Start

```bash
fix issues          # or /fixing-code
review code         # or /reviewing-code
commit changes      # or /committing-code
research "topic"    # or /researching-web
```

---

## Skills (User-Invocable)

Invoke via natural language or `/skill-name`:

| Skill                 | Triggers On                                     |
| --------------------- | ----------------------------------------------- |
| `brainstorming-ideas` | "brainstorm", "design feature", "think through" |
| `fixing-code`         | "fix", "fix issues", "fix errors"               |
| `reviewing-code`      | "review", "review code", "check this"           |
| `committing-code`     | "commit", "save changes", "git commit"          |
| `documenting-code`    | "update docs", "document", "write docs"         |
| `checking-deploy`     | "deploy check", "validate k8s"                  |
| `looking-up-docs`     | Library documentation via Context7              |
| `researching-web`     | "research", "compare X vs Y"                    |
| `using-git-worktrees` | Parallel development with worktrees             |

---

## Commands

| Command         | Description                       |
| --------------- | --------------------------------- |
| `/spec:init`    | Initialize spec-driven project    |
| `/spec:gen`     | Generate app_spec from markdown   |
| `/spec:work`    | Continue spec-driven development  |
| `/spec:status`  | Quick progress check              |
| `/spec:sync`    | Sync feature_list from code       |
| `/spec:align`   | Align spec with code (bottom-up)  |
| `/spec:audit`   | Audit spec abstraction levels     |
| `/test:e2e`     | E2E testing with Playwright       |
| `/test:improve` | Improve test quality              |
| `/agent:resume` | Resume a previously spawned agent |
| `/ai:consult`   | Independent review from Claude    |
| `/learn`        | Extract learnings → CLAUDE.md     |

---

## Agents

### Engineers

| Agent                 | Model | Focus                        |
| --------------------- | ----- | ---------------------------- |
| `go-engineer`         | opus  | Go development, stdlib-first |
| `python-engineer`     | opus  | Python, type hints           |
| `typescript-engineer` | opus  | TypeScript/React             |
| `infra-engineer`      | opus  | K8s, Terraform, CI/CD        |

### Specialists (deep reviews)

| Go            | Python        | TypeScript    |
| ------------- | ------------- | ------------- |
| `go-qa`       | `py-qa`       | `ts-qa`       |
| `go-tests`    | `py-tests`    | `ts-tests`    |
| `go-impl`     | `py-impl`     | `ts-impl`     |
| `go-idioms`   | `py-idioms`   | `ts-idioms`   |
| `go-docs`     | `py-docs`     | `ts-docs`     |
| `go-simplify` | `py-simplify` | `ts-simplify` |

### Spec-Driven

| Agent           | Focus                       |
| --------------- | --------------------------- |
| `spec-discover` | Project discovery, progress |
| `spec-planner`  | Implementation planning     |
| `spec-verifier` | Feature verification        |

### Utility

| Agent                   | Focus                     |
| ----------------------- | ------------------------- |
| `docs-keeper`           | Documentation maintenance |
| `pdf-parser`            | PDF extraction            |
| `playwright-tester`     | E2E browser testing       |
| `perplexity-researcher` | Web research              |

---

## Skills (Auto-Activated)

Hidden from `/` menu, triggered automatically:

| Skill                | Triggers On                |
| -------------------- | -------------------------- |
| `writing-go`         | Go code development        |
| `writing-python`     | Python code development    |
| `writing-typescript` | TypeScript code            |
| `writing-web`        | HTML/CSS/JS/HTMX           |
| `managing-infra`     | K8s, Terraform, CI/CD      |
| `using-cloud-cli`    | GCP/AWS CLI commands       |
| `using-modern-cli`   | rg, fd, bat, sd, eza, dust |
| `refactoring-code`   | Batch refactoring          |
| `searching-code`     | Codebase exploration       |
| `testing-e2e`        | Playwright testing         |

---

## MCP Servers

| Server                | Purpose                   |
| --------------------- | ------------------------- |
| `context7`            | Library docs              |
| `sequential-thinking` | Multi-step reasoning      |
| `perplexity-ask`      | Web research              |
| `playwright`          | E2E browser testing       |
| `morphllm`            | Fast editing, code search |

---

## Hooks

| Hook             | Purpose                  |
| ---------------- | ------------------------ |
| `skill-enforcer` | Suggests relevant skills |
| `smart-lint`     | Auto-lints after edits   |
| `file-protector` | Protects sensitive files |

---

## Environment Switching (`ce`)

```bash
ce              # TUI picker
ce z            # Switch to z.ai + launch
ce --continue   # TUI + continue session
```

| Provider | Alias | Pricing |
| -------- | ----- | ------- |
| default  | max   | $20/mo  |
| vertex   | v     | Pay/use |
| zai      | z     | $0.40/M |
| deepseek | ds    | $0.28/M |

---

**[Complete Guide →](GUIDE.md)**
