# Claude Code Configuration

Personal Claude Code configuration managed with [chezmoi](https://chezmoi.io), shared across machines. Contains a curated set of skills, agents, hooks, and scripts that extend Claude Code with domain-specific workflows, multi-provider support, and spec-driven development.

## Structure

```
~/.claude/
├── CLAUDE.md               # Global instructions (universal dev practices)
├── GUIDE.md                # Detailed usage guide for all components
├── CHANGELOG.md            # Versioned changelog (semver)
├── model-profiles.json     # Model IDs per provider
├── settings.json           # Claude Code settings + hook registration
├── pyproject.toml          # Python tooling (validate-config, specctl)
├── .claude/CLAUDE.md       # Project instructions (config-repo-specific)
├── .github/workflows/      # CI (validation, linting, tests)
├── agents/                 # Specialized agents
├── commands/               # Slash commands (spec/*, watch-team)
├── hooks/                  # Event hooks
├── scripts/                # CLI tools (ce, specctl, cliproxy.sh, ...)
└── skills/                 # Workflow skills
```

## Quick Start

```bash
# 1. Apply dotfiles via chezmoi
chezmoi apply

# 2. Install Python tooling
cd ~/.claude && uv sync

# 3. Verify the active provider and model profiles
ce --show-models

# 4. (Optional) Initialize model profiles if missing
ce --init-model-profiles
```

The `ce` script switches Claude Code between providers. Run `ce vertex` to switch to Vertex AI, `ce default` to return to the Anthropic API.

## Key Components

| Component | Count | Description                                                                                         |
| --------- | ----- | --------------------------------------------------------------------------------------------------- |
| Skills    | 23    | Domain workflows: writing, reviewing, fixing, deploying, spec-driven dev, and more                  |
| Agents    | 14    | Specialized agents for Go, Python, TypeScript, web, infra, and planning                             |
| Hooks     | 7     | session-start, skill-enforcer, file-protector, smart-lint, notify, performance-monitor, test-runner |

Skills are loaded automatically by the `skill-enforcer` hook when trigger phrases match. Two skills (`evolving-config`, `learning-patterns`) are local to this repo; the rest are global.

## Providers

Switch with `ce <env>`:

| Environment | Provider         |
| ----------- | ---------------- |
| `default`   | Anthropic API    |
| `vertex`    | Vertex AI        |
| `copilot`   | GitHub Copilot   |
| `codex`     | OpenAI via proxy |
| `gemini`    | Gemini via proxy |
| `deepseek`  | DeepSeek         |
| `zai`       | Z.ai             |

Proxy environments (`codex`, `gemini`) require `cliproxy.sh` running on `localhost:8317`.

## Versioning

Releases follow [Semantic Versioning](https://semver.org/):

- **major** — breaking changes to hooks or config structure
- **minor** — new skills, agents, or features
- **patch** — fixes and refinements

Changes are documented in [CHANGELOG.md](CHANGELOG.md). Current release: **1.0.0**.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to master:

1. Config validation — frontmatter and cross-references (`scripts/validate-config.py`)
2. Python linting — `ruff check` and `ruff format --check`
3. Shell linting — `shellcheck` on all `.sh` files
4. Smoke tests — `pytest tests/`

To run locally before committing:

```bash
uv run python scripts/validate-config.py
uv run --extra test pytest tests/ -v
ruff check scripts/ && ruff format --check scripts/
shellcheck hooks/*.sh scripts/*.sh
```

## Further Reading

See [GUIDE.md](GUIDE.md) for detailed usage: skill invocation, agent coordination, hook behavior, spec-driven development workflow, and environment configuration.
