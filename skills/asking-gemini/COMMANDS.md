# Gemini CLI Reference

Run `gemini --help` to see all available options and commands.

## Key Flags

| Flag                  | Purpose                                             |
| --------------------- | --------------------------------------------------- |
| `-p "prompt"`         | Non-interactive prompt (deprecated, use positional) |
| `"prompt"`            | Positional prompt for one-shot mode                 |
| `-i "prompt"`         | Interactive mode starting with prompt               |
| `-m model`            | Specify model (e.g., gemini-2.5-pro)                |
| `-y, --yolo`          | Auto-approve all tool actions                       |
| `--approval-mode`     | Set: default, auto_edit, or yolo                    |
| `-s, --sandbox`       | Run in sandbox                                      |
| `-r, --resume`        | Resume previous session (latest or index)           |
| `-o, --output-format` | Output: text, json, stream-json                     |

## Subcommands

```bash
gemini mcp              # Manage MCP servers
gemini extensions       # Manage extensions
gemini --list-sessions  # List available sessions
```

## Shell Execution

In interactive mode, prefix with `!` to run shell commands:

```
> !git status
> !ls -la
```

## Discovery

```bash
gemini --help           # All flags and commands
gemini mcp --help       # MCP management help
gemini --list-extensions # Available extensions
```

## Examples

```bash
# One-shot query
gemini "Explain this architecture"

# Interactive with initial prompt
gemini -i "Let's design an API"

# Resume last session
gemini -r latest

# Auto-approve with specific model
gemini -y -m gemini-2.5-pro "Review this design"
```
