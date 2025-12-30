# Claude Code Configuration

Production-quality setup with specialized agents, AI consultation, and zero-tolerance quality enforcement.

**[Complete Reference Guide →](GUIDE.md)**

---

## Quick Start

```bash
# Quality check before commit
/code:fix

# Multi-agent code review
/code:review deep external

# AI consultation (architecture, code review, panel)
/ai:consult gemini "caching strategy"
/ai:consult panel "gRPC vs REST for internal services?"
```

---

## MCP Servers Setup

Add to `~/.claude.json` under `"mcpServers"`:

```json
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "bunx",
      "args": ["@upstash/context7-mcp@latest"]
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "bunx",
      "args": ["@modelcontextprotocol/server-sequential-thinking"],
      "env": {}
    },
    "perplexity-ask": {
      "type": "stdio",
      "command": "bunx",
      "args": ["server-perplexity-ask"],
      "env": {
        "PERPLEXITY_API_KEY": "<YOUR_PERPLEXITY_API_KEY>"
      }
    },
    "gemini": {
      "type": "stdio",
      "command": "bunx",
      "args": ["@tuannvm/gemini-mcp-server"],
      "env": {
        "GEMINI_MODEL": "gemini-3-pro-preview"
      }
    },
    "codex": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-as-mcp@latest"]
    }
  }
}
```

### MCP Tools Reference

| Server                  | Tools                                                          | Purpose                                   |
| ----------------------- | -------------------------------------------------------------- | ----------------------------------------- |
| **context7**            | `resolve-library-id`, `query-docs`                             | Library documentation lookup              |
| **sequential-thinking** | `sequentialthinking`                                           | Multi-step reasoning                      |
| **perplexity-ask**      | `perplexity_ask`                                               | Web research                              |
| **gemini**              | `gemini`, `brainstorm`, `web-search`, `analyze-media`, `shell` | Gemini AI consultation, web search, media |
| **codex**               | `spawn_agent`, `spawn_agents_parallel`                         | OpenAI Codex subagents                    |

### Required Permissions

Add to `~/.claude/settings.json` under `"permissions.allow"`:

```json
{
  "permissions": {
    "allow": [
      "mcp__sequential-thinking__sequentialthinking",
      "mcp__perplexity-ask__perplexity_ask",
      "mcp__context7__resolve-library-id",
      "mcp__context7__get-library-docs",
      "mcp__gemini__gemini",
      "mcp__gemini__web-search",
      "mcp__gemini__analyze-media",
      "mcp__gemini__shell",
      "mcp__gemini__brainstorm",
      "mcp__gemini__fetch-chunk",
      "mcp__gemini__ping",
      "mcp__gemini__help",
      "mcp__codex__spawn_agent",
      "mcp__codex__spawn_agents_parallel"
    ]
  }
}
```

---

## Commands

| Command              | Description                                  |
| -------------------- | -------------------------------------------- |
| `/ai:consult`        | Consult AI assistants (codex/gemini/panel)   |
| `/code:fix`          | Fix ALL issues via parallel agents           |
| `/code:review`       | Multi-agent code review                      |
| `/code:consult`      | Consult Codex for code review                |
| `/code:docs`         | Update documentation via docs-keeper         |
| `/code:commit`       | Create bundled commits with concise messages |
| `/code:deploy-check` | Validate K8s/CI configs                      |
| `/test:coverage`     | Test coverage analysis (80% minimum)         |
| `/test:generate`     | Generate tests following best practices      |
| `/spec:init`         | Initialize spec-driven project               |
| `/spec:work`         | Continue spec-driven development             |
| `/spec:status`       | Quick progress check                         |
| `/spec:sync`         | Sync feature_list.json from code/git         |
| `/spec:gen`          | Generate app_spec.txt from markdown          |
| `/research`          | Research topics via Perplexity AI            |
| `/docs:lookup`       | Look up library documentation via Context7   |

---

## AI Consultation

```mermaid
flowchart LR
    subgraph Command
        AC[/ai:consult]
    end

    subgraph Agents
        GC[gemini-consultant]
        CA[codex-assistant]
        APA[ai-panel]
    end

    subgraph "Gemini Specialists"
        GR[gemini-researcher]
        GMA[gemini-media-analyst]
        GSH[gemini-shell-helper]
    end

    AC --> |gemini| GC
    AC --> |codex| CA
    AC --> |panel| APA

    GC --> |brainstorm tool| Methodologies
    GR --> |web-search tool| RealTimeInfo
    GMA --> |analyze-media tool| PDFs/Images
    GSH --> |shell tool| Commands

    APA --> |4 perspectives| Summary[Synthesized Summary]
```

| Mode                 | Use For                                                   |
| -------------------- | --------------------------------------------------------- |
| `/ai:consult gemini` | Architecture, design trade-offs, brainstorming            |
| `/ai:consult codex`  | Code review, security, implementation advice              |
| `/ai:consult panel`  | Critical decisions (Codex + Gemini + Claude + Perplexity) |

### Brainstorming Methodologies (via Gemini)

| Methodology       | Description                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| `divergent`       | Generate many diverse ideas                                               |
| `convergent`      | Refine and evaluate existing ideas                                        |
| `scamper`         | Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse |
| `design-thinking` | Human-centered, empathy-driven approach                                   |
| `lateral`         | Unexpected connections, challenge assumptions                             |
| `auto`            | AI selects best methodology                                               |

---

## Agents

### Primary Engineers

| Agent                 | Model | Focus                            |
| --------------------- | ----- | -------------------------------- |
| `go-engineer`         | opus  | Go development with stdlib-first |
| `python-engineer`     | opus  | Python development, type hints   |
| `typescript-engineer` | opus  | TypeScript/React strict typing   |
| `infra-engineer`      | opus  | K8s, Terraform, Helm, CI/CD      |

### AI Consultation

| Agent                  | Model  | MCP Tools                       | Focus                          |
| ---------------------- | ------ | ------------------------------- | ------------------------------ |
| `gemini-consultant`    | haiku  | `gemini`, `brainstorm`          | Architecture, design, ideation |
| `gemini-researcher`    | haiku  | `web-search`                    | Real-time web research         |
| `gemini-media-analyst` | haiku  | `analyze-media`                 | PDF/image analysis             |
| `gemini-shell-helper`  | haiku  | `shell`                         | Shell command generation       |
| `codex-assistant`      | haiku  | `codex`, `review`               | Code review via Codex          |
| `ai-panel`             | sonnet | `gemini`, `codex`, `perplexity` | Multi-AI orchestration         |
| `claude-reviewer`      | sonnet | -                               | Fresh perspective review       |

### Language Specialists (for deep reviews)

| Go            | Python        | TypeScript |
| ------------- | ------------- | ---------- |
| `go-docs`     | `py-docs`     | `ts-docs`  |
| `go-idioms`   | `py-idioms`   | `ts-tests` |
| `go-impl`     | `py-impl`     | -          |
| `go-qa`       | `py-qa`       | -          |
| `go-simplify` | `py-simplify` | -          |
| `go-tests`    | `py-tests`    | -          |

### Utility Agents

| Agent         | Model  | Focus                      |
| ------------- | ------ | -------------------------- |
| `docs-keeper` | sonnet | Documentation maintenance  |
| `pdf-parser`  | haiku  | PDF parsing and extraction |

---

## Skills (Auto-Triggered)

| Skill                    | Triggers On                                   |
| ------------------------ | --------------------------------------------- |
| `asking-gemini`          | Architecture, design, brainstorming, SCAMPER  |
| `asking-codex`           | Code review, security audit, bug detection    |
| `researching-web-gemini` | Google search, real-time info, current events |
| `researching-web`        | Web research via Perplexity                   |
| `analyzing-media`        | PDF analysis, image analysis, OCR, diagrams   |
| `generating-shell`       | Shell commands, bash scripts, unix pipes      |
| `looking-up-docs`        | Library documentation via Context7            |
| `writing-go`             | `.go` files, Go commands                      |
| `writing-python`         | `.py` files, Python commands                  |
| `writing-typescript`     | `.ts/.tsx` files, npm/bun                     |
| `managing-infra`         | K8s, Terraform, Helm, GitHub Actions          |
| `using-cloud-cli`        | GCP/AWS CLI, BigQuery                         |
| `using-git-worktrees`    | Isolated git worktrees for parallel dev       |
| `using-modern-cli`       | rg/fd/bat/eza/sd over grep/find/cat/ls/sed    |

---

## CLI Tools

Modern CLI replacements are pre-configured for better performance.

```bash
# Install all recommended tools
~/.claude/scripts/install-tools.sh
```

| Task         | Modern      | Traditional | Why                                 |
| ------------ | ----------- | ----------- | ----------------------------------- |
| Search text  | `rg`        | grep        | 10-100x faster, respects .gitignore |
| Find files   | `fd`        | find        | Simpler syntax, ignores .git        |
| View files   | `bat`       | cat         | Syntax highlighting, line numbers   |
| List files   | `eza`       | ls          | Icons, git status, tree view        |
| Replace text | `sd`        | sed         | Intuitive regex, preview mode       |
| Disk usage   | `dust`      | du          | Visual tree, sorted by size         |
| Processes    | `procs`     | ps          | Tree view, sortable columns         |
| Diff files   | `delta`     | diff        | Syntax highlighting, side-by-side   |
| JSON         | `jq`        | -           | Query and transform JSON            |
| YAML         | `yq`        | -           | Query and transform YAML            |
| Fuzzy find   | `fzf`       | -           | Interactive fuzzy finder            |
| Benchmarking | `hyperfine` | time        | Statistical analysis, warmup        |
| Code stats   | `tokei`     | cloc        | Fast LOC counter                    |
| Markdown     | `glow`      | -           | Terminal markdown viewer            |
| Git TUI      | `lazygit`   | -           | Interactive git interface           |

### LSP Servers

| Language   | Server                       |
| ---------- | ---------------------------- |
| Go         | `gopls`                      |
| Python     | `pyright`                    |
| TypeScript | `typescript-language-server` |

---

## Hooks

| Hook             | Trigger       | Purpose                       |
| ---------------- | ------------- | ----------------------------- |
| `skill-enforcer` | Prompt submit | Suggests relevant skills      |
| `smart-lint`     | After edits   | Auto-linting (Go, Python, TS) |
| `file-protector` | Before edits  | Protects sensitive files      |
| `notify`         | Notification  | Desktop notifications         |

---

## Copilot Proxy (Rate Limit Fallback)

```bash
~/.claude/scripts/copilot-proxy.sh           # Start
~/.claude/scripts/copilot-proxy.sh --status  # Check
~/.claude/scripts/copilot-proxy.sh --stop    # Stop
```

Switch configs: edit `settings.json`, swap `env` ↔ `env.copilot`/`env.vertex`.

---

## Quality Standards

- **Zero tolerance**: ALL linting/tests must pass
- **80% coverage**: Enforced via `/test:coverage`
- **Security first**: OWASP checks in code review

---

**[Full documentation →](GUIDE.md)** | Commands, agents, skills, hooks, workflows
