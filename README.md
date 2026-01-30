# Claude Code Configuration

Global configuration for Claude Code CLI.

## Structure

```
~/.claude/
├── CLAUDE.md              # Global instructions (always loaded)
├── MCP_Sequential.md      # Sequential thinking guide
├── settings.json          # Settings, permissions, hooks, environments
├── keybindings.json       # Custom keybindings
├── hook-config.json       # Optional hook configuration
├── commands/              # Custom slash commands
│   ├── code/              # Code workflow commands
│   ├── spec/              # Spec-driven development
│   ├── test/              # Testing commands
│   ├── agent/             # Agent management
│   └── ai/                # AI utilities
├── skills/                # Reusable skills (auto-suggested)
│   ├── writing-*/         # Language-specific development
│   ├── managing-infra/    # Infrastructure patterns
│   ├── reviewing-code/    # Code review
│   └── ...
├── hooks/                 # Event-triggered scripts
│   ├── session-start.sh   # SessionStart: show context
│   ├── skill-enforcer.sh  # UserPromptSubmit: suggest skills
│   ├── file-protector.sh  # PreToolUse: block sensitive files
│   ├── smart-lint.sh      # PostToolUse: auto-lint on edit
│   └── notify.sh          # Notification: system alerts
└── scripts/               # Helper scripts
    ├── auth-helper.sh     # Multi-provider auth routing
    └── cliproxy.sh        # CLIProxyAPI for Codex/Gemini
```

## Environments

Switch between API providers with `ce`:

```bash
ce                    # Default (Anthropic API)
ce vertex             # Vertex AI
ce codex              # OpenAI Codex via CLIProxyAPI
ce gemini             # Gemini via CLIProxyAPI
ce deepseek           # DeepSeek
ce zai                # Z.ai
```

Environments are defined in `settings.json` under `env.*` keys.

## Commands

User-invocable commands (slash commands):

| Command         | Description                 |
| --------------- | --------------------------- |
| `/spec:work`    | Main spec-driven workflow   |
| `/spec:init`    | Initialize .spec/ structure |
| `/spec:status`  | Show progress               |
| `/code:deploy`  | Deploy infrastructure       |
| `/test:e2e`     | Run E2E tests               |
| `/test:improve` | Improve test quality        |
| `/ai:consult`   | Get fresh perspective       |
| `/agent:resume` | Resume agent by ID          |
| `/learn`        | Extract learnings           |

## Skills

Skills are auto-suggested by the `skill-enforcer` hook based on prompt content.
They provide specialized knowledge and tool access for specific domains.

### Development

- `writing-go` - Go 1.25+ patterns
- `writing-python` - Python 3.14+ patterns
- `writing-typescript` - TypeScript 5.x patterns
- `writing-web` - HTML/CSS/JS/HTMX

### Infrastructure

- `managing-infra` - K8s, Terraform, Helm, GHA
- `using-cloud-cli` - GCP, AWS CLI patterns
- `checking-deploy` - Validate configs

### Workflow

- `reviewing-code` - Multi-agent review
- `refactoring-code` - Batch refactoring
- `committing-code` - Smart commits
- `searching-code` - WarpGrep exploration

## Hooks

Event-triggered automation:

| Hook              | Event            | Purpose                    |
| ----------------- | ---------------- | -------------------------- |
| session-start.sh  | SessionStart     | Show git/spec context      |
| skill-enforcer.sh | UserPromptSubmit | Suggest relevant skills    |
| file-protector.sh | PreToolUse       | Block sensitive file edits |
| smart-lint.sh     | PostToolUse      | Auto-lint after edits      |
| notify.sh         | Notification     | System notifications       |

### Hook Configuration

Optional: Create `hook-config.json` to customize hook behavior.
Hooks fall back to sensible defaults if this file doesn't exist.

## Adding New Components

### New Command

```bash
mkdir -p ~/.claude/commands/category
cat > ~/.claude/commands/category/name.md << 'CMDEOF'
---
context: fork
allowed-tools: [Task, Read, Grep]
description: Brief description
---

# Command Name

Instructions for Claude...
CMDEOF
```

### New Skill

```bash
mkdir -p ~/.claude/skills/skill-name
cat > ~/.claude/skills/skill-name/SKILL.md << 'SKILLEOF'
---
name: skill-name
description: When to use this skill
user-invocable: false
context: fork
agent: appropriate-agent
allowed-tools: [Read, Bash, Grep, Glob]
---

# Skill Name

Guidance and patterns...
SKILLEOF
```

## Debugging

```bash
# Check settings
cat ~/.claude/settings.json | jq .

# Test hook manually
echo '{"prompt":"write go code"}' | ~/.claude/hooks/skill-enforcer.sh

# Check hook logs
tail -f ~/.claude/logs/performance.jsonl

# Validate configuration
claude --version
```
