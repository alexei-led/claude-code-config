---
name: asking-gemini
description: Consults Gemini AI for architecture alternatives, design trade-offs, and brainstorming. Use when evaluating architectural approaches, comparing design options, or generating creative ideas. Not for implementation or documentation lookup.
allowed-tools: Bash
---

# Design Consultation with Gemini CLI

Invoke Gemini CLI for architecture advice, design reviews, and brainstorming.

## Quick Usage

```bash
# Non-interactive prompt
gemini -p "Your prompt here"

# With helper script
~/.claude/skills/asking-gemini/scripts/ask.sh brainstorm "How to handle auth?"
~/.claude/skills/asking-gemini/scripts/ask.sh review "Current REST API design"
~/.claude/skills/asking-gemini/scripts/ask.sh compare "gRPC vs REST for internal services"
```

## When to Use

| Use Case               | Example                                        |
| ---------------------- | ---------------------------------------------- |
| Architecture decisions | "Trade-offs of microservices vs monolith"      |
| Design alternatives    | "Different caching strategies for this system" |
| Brainstorming          | "Creative solutions for rate limiting"         |
| Comparing approaches   | "Redis vs Memcached for sessions"              |

## Modes

The helper script supports context-aware modes:

| Mode         | Purpose                               |
| ------------ | ------------------------------------- |
| `prompt`     | Raw prompt (default)                  |
| `brainstorm` | Generate 5-10 ideas with trade-offs   |
| `review`     | Analyze design, identify alternatives |
| `compare`    | Compare options systematically        |

## References

- [COMMANDS.md](COMMANDS.md) - Slash commands and CLI flags
- [scripts/ask.sh](scripts/ask.sh) - Helper script
