# Contributing

## Setup

```bash
make setup    # Install pre-commit hook + dev dependencies
```

## Adding a Plugin

1. Create a directory under `plugins/<your-plugin>/`
2. Add `.claude-plugin/plugin.json` (Claude Code manifest):

   ```json
   {
     "name": "your-plugin",
     "description": "What it does",
     "version": "1.2.2",
     "author": { "name": "Your Name" }
   }
   ```

3. Add `.codex-plugin/plugin.json` (Codex CLI manifest):

   ```json
   {
     "name": "your-plugin",
     "version": "1.2.2",
     "description": "What it does",
     "skills": "./skills/",
     "interface": {
       "displayName": "Your Plugin",
       "shortDescription": "What it does",
       "developerName": "Your Name",
       "category": "Development"
     }
   }
   ```

4. Add `gemini-extension.json` (Gemini CLI manifest):

   ```json
   {
     "name": "your-plugin",
     "version": "1.2.2",
     "description": "What it does"
   }
   ```

5. Add skills, agents, hooks, or commands in their respective directories
6. Register the plugin in both marketplaces:
   - `.claude-plugin/marketplace.json` (Claude Code)
   - `.agents/plugins/marketplace.json` (Codex CLI)
7. Run `make flat` to sync symlinks

## Directory Structure

```
plugins/your-plugin/
├── .claude-plugin/
│   └── plugin.json           # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json           # Codex CLI manifest
├── gemini-extension.json     # Gemini CLI manifest
├── skills/
│   └── your-skill/
│       └── SKILL.md          # CC source (name + description frontmatter)
├── skills-codex/             # Build output — platform-optimized for Codex/Gemini
│   └── your-skill/
│       └── SKILL.md
├── agents/
│   └── your-agent.md         # Claude Code only
├── hooks/
│   └── your-hook.sh          # Claude Code only
└── commands/
    └── your-command.md       # Claude Code only
```

> **Note**: Skills are cross-compatible across Claude Code, Codex CLI, and Gemini CLI. Platform-specific optimizations are handled by the build system (`scripts/generate-overlays.py`). Agents, hooks, and commands are Claude Code-only.

## Available Commands

```bash
make help       # Show all commands
make ci         # Run full CI pipeline locally (lint + validate + test)
make lint       # Run all linters
make test       # Run pytest
make validate   # Validate configs and flat/ sync
make fmt        # Auto-format Python files
make flat       # Sync flat/ symlinks
```

## PR Checklist

- [ ] `make ci` passes
- [ ] Plugin version bumped in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
- [ ] CHANGELOG.md updated
- [ ] README.md plugin table updated (skill/agent counts)
- [ ] Plugin README.md updated if adding skills, agents, or hooks
- [ ] `make flat` run to sync flat/ directory
- [ ] Both marketplace files updated if adding/removing plugins
