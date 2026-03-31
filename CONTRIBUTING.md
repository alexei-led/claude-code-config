# Contributing

## Adding a Plugin

1. Create a directory under `plugins/<your-plugin>/`
2. Add `.claude-plugin/plugin.json` with required fields:

   ```json
   {
     "name": "your-plugin",
     "description": "What it does",
     "version": "1.1.0",
     "author": { "name": "Your Name" }
   }
   ```

3. Add skills, agents, hooks, or commands in their respective directories
4. Register the plugin in `.claude-plugin/marketplace.json`

## Directory Structure

```
plugins/your-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── your-skill/
│       └── SKILL.md       # Requires name + description frontmatter
├── agents/
│   └── your-agent.md      # Requires name + description + tools frontmatter
├── hooks/
│   └── your-hook.sh
└── commands/
    └── your-command.md    # Requires description frontmatter
```

## Setup

Install the pre-commit hook to run all checks before each commit:

```bash
cp scripts/pre-commit .git/hooks/pre-commit
```

## Validation

```bash
uv run python scripts/validate-config.py    # Config and frontmatter checks
uv run --extra test python -m pytest tests/ -v  # Tests
uv run ruff check .                          # Python lint
uv run ruff format --check .                 # Python format
bash scripts/generate-flat.sh                # Sync flat/ symlinks
```

## PR Checklist

- [ ] `uv run python scripts/validate-config.py` passes with 0 errors and 0 warnings
- [ ] All tests pass
- [ ] Plugin version bumped if modifying existing plugins
- [ ] CHANGELOG.md updated
- [ ] README.md plugin table updated (skill/agent counts)
- [ ] GUIDE.md updated if adding skills, agents, or hooks
- [ ] `scripts/generate-flat.sh` run to sync flat/ directory
