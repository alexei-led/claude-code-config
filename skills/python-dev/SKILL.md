---
name: python-dev
description: Idiomatic Python development. Use when writing Python code, CLI tools, or services. Emphasizes stdlib, type hints, uv/ruff toolchain, and minimal dependencies.
---

# Python Principles

## Toolchain

- **uv** for packages (not pip/poetry)
- **ruff** for lint + format (not flake8/black)
- **Python 3.13+** latest features
- **pyproject.toml** for config

## Design

- Stdlib first, external deps only when justified
- Type hints everywhere
- Explicit over implicit
- Fail fast with clear exceptions
- Environment variables for config

## Structure

- `src/<package>/` layout
- Flat modules over deep nesting
- `__main__.py` for CLI entry

## Style

- Type hints on all functions
- Dataclasses for simple data
- Pathlib over os.path
- f-strings for formatting
- Context managers for resources

## Naming

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Short but meaningful names

## Patterns

- Pattern matching for dispatch (3.10+)
- Structural typing with Protocol
- Generator expressions over list comprehensions when iterating once
- `|` for type unions (3.10+)

## CLI Pattern

- typer or argparse
- Environment-driven config
- Structured output (JSON option)
- Docker-first deployment

## Security

- Input validation at boundaries
- Allowlist over denylist
- No shell=True with user input
