# Claude Code Configuration

Production-quality setup with specialized agents and zero-tolerance quality enforcement.

---

## Quick Start

```bash
/code:fix           # Fix all lint/test issues
/code:review deep   # Multi-agent code review
/research "topic"   # Web research via Perplexity
```

---

## Commands

| Command              | Description                        |
| -------------------- | ---------------------------------- |
| `/code:fix`          | Fix ALL issues via parallel agents |
| `/code:review`       | Multi-agent code review            |
| `/code:docs`         | Update documentation               |
| `/code:commit`       | Create bundled commits             |
| `/code:deploy-check` | Validate K8s/CI configs            |
| `/test:e2e`          | E2E testing with Playwright        |
| `/test:improve`      | Improve test quality               |
| `/spec:init`         | Initialize spec-driven project     |
| `/spec:work`         | Continue spec-driven development   |
| `/spec:status`       | Quick progress check               |
| `/spec:sync`         | Sync feature_list from code        |
| `/research`          | Web research via Perplexity        |
| `/docs:lookup`       | Library docs via Context7          |

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

| Go            | Python        | TypeScript |
| ------------- | ------------- | ---------- |
| `go-qa`       | `py-qa`       | `ts-tests` |
| `go-tests`    | `py-tests`    | `ts-docs`  |
| `go-impl`     | `py-impl`     | -          |
| `go-idioms`   | `py-idioms`   | -          |
| `go-docs`     | `py-docs`     | -          |
| `go-simplify` | `py-simplify` | -          |

### Utility

| Agent                   | Focus                     |
| ----------------------- | ------------------------- |
| `docs-keeper`           | Documentation maintenance |
| `pdf-parser`            | PDF extraction            |
| `playwright-tester`     | E2E browser testing       |
| `perplexity-researcher` | Web research              |

---

## Skills (Auto-Triggered)

| Skill                 | Triggers On           |
| --------------------- | --------------------- |
| `writing-go`          | Go files              |
| `writing-python`      | Python files          |
| `writing-typescript`  | TypeScript files      |
| `looking-up-docs`     | Library documentation |
| `researching-web`     | Web research          |
| `searching-code`      | Codebase exploration  |
| `refactoring-fast`    | Batch refactoring     |
| `managing-infra`      | K8s, Terraform, CI/CD |
| `using-cloud-cli`     | GCP/AWS CLI           |
| `using-git-worktrees` | Parallel development  |
| `testing-e2e`         | Playwright testing    |

---

## MCP Servers

| Server                | Purpose              |
| --------------------- | -------------------- |
| `context7`            | Library docs         |
| `sequential-thinking` | Multi-step reasoning |
| `perplexity-ask`      | Web research         |
| `playwright`          | E2E browser testing  |

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
