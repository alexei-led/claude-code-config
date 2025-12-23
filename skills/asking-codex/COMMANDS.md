# Codex CLI Reference

Run `codex --help` to see all available commands and options.
Run `codex <command> --help` for command-specific flags.

## Commands

| Command         | Purpose                       |
| --------------- | ----------------------------- |
| `codex`         | Interactive mode              |
| `codex exec`    | Non-interactive execution     |
| `codex review`  | Code review (non-interactive) |
| `codex resume`  | Resume previous session       |
| `codex apply`   | Apply diff from last session  |
| `codex sandbox` | Run commands in sandbox       |

## Key Flags (exec)

| Flag                        | Purpose                                                 |
| --------------------------- | ------------------------------------------------------- |
| `--full-auto`               | Auto-approve + workspace write sandbox                  |
| `-m, --model`               | Specify model                                           |
| `-s, --sandbox`             | Sandbox: read-only, workspace-write, danger-full-access |
| `-i, --image`               | Attach image(s)                                         |
| `-o, --output-last-message` | Save response to file                                   |
| `--output-schema`           | JSON schema for structured output                       |
| `--json`                    | JSONL event output                                      |
| `-C, --cd`                  | Set working directory                                   |

## Review Flags

| Flag            | Purpose                                  |
| --------------- | ---------------------------------------- |
| `--uncommitted` | Review staged/unstaged/untracked changes |
| `--base BRANCH` | Review against base branch               |
| `--commit SHA`  | Review specific commit                   |

## Discovery

```bash
codex --help            # All commands
codex exec --help       # Exec flags
codex review --help     # Review flags
codex resume --help     # Resume options
```

## Examples

```bash
# Non-interactive task
codex exec "Analyze this codebase for issues"

# With file modifications
codex exec --full-auto "Add input validation"

# Code review against main
codex review --base main

# Review uncommitted changes
codex review --uncommitted "Focus on security"

# Resume last session
codex exec resume --last "Continue fixing issues"

# Structured output
codex exec --output-schema schema.json "Extract project info"
```
