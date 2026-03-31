# Contributing

## Setup

```bash
make setup    # Install pre-commit hook + dev dependencies
```

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
5. Run `make flat` to sync symlinks

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
- [ ] Plugin version bumped if modifying existing plugins
- [ ] CHANGELOG.md updated
- [ ] README.md plugin table updated (skill/agent counts)
- [ ] Plugin README.md updated if adding skills, agents, or hooks
- [ ] `make flat` run to sync flat/ directory
