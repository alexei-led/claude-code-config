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

## Commands Overview

| Category            | Commands                                                               |
| ------------------- | ---------------------------------------------------------------------- |
| **Code Quality**    | `/code:fix` `/code:review` `/code:consult` `/code:docs` `/code:commit` |
| **AI Consultation** | `/ai:consult`                                                          |
| **Testing**         | `/test:coverage` `/test:generate`                                      |
| **Spec-Driven**     | `/spec:init` `/spec:work` `/spec:status`                               |
| **Research**        | `/research` `/docs:lookup`                                             |

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

    AC --> |gemini| GC
    AC --> |codex| CA
    AC --> |panel| APA

    APA --> |4 perspectives| Summary[Synthesized Summary]
```

| Mode                 | Use For                                                   |
| -------------------- | --------------------------------------------------------- |
| `/ai:consult gemini` | Architecture, design trade-offs, brainstorming            |
| `/ai:consult codex`  | Code review, security, implementation advice              |
| `/ai:consult panel`  | Critical decisions (Codex + Gemini + Claude + Perplexity) |

---

## Agents

| Agent                 | Model  | Focus                   |
| --------------------- | ------ | ----------------------- |
| `go-engineer`         | opus   | Go development          |
| `python-engineer`     | opus   | Python development      |
| `typescript-engineer` | opus   | TypeScript/React        |
| `gemini-consultant`   | haiku  | Architecture via Gemini |
| `codex-assistant`     | haiku  | Code review via Codex   |
| `ai-panel`            | sonnet | Multi-AI orchestration  |

Deep review spawns 6+ specialists per language. See [GUIDE.md](GUIDE.md#agents).

---

## Hooks

| Hook             | Trigger       | Purpose         |
| ---------------- | ------------- | --------------- |
| `skill-enforcer` | Prompt submit | Suggests skills |
| `smart-lint`     | After edits   | Auto-linting    |
| `file-protector` | Before edits  | Protects files  |

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
