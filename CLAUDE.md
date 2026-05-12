# cc-thingz

Portable skills, agents, and hooks for Claude Code, Codex CLI, Gemini CLI, and Pi.

## Writing Agent/Skill Instructions

LLM signal hierarchy (MDEval benchmark + Perplexity research):

- HIGH: `#` headers, bullet/numbered lists, code blocks — always use
- MEDIUM: `**bold**` — ≤15% of prose lines; use for bullet labels (`- **Label**: desc`) and critical keywords only
- LOW/zero: `_italic_`, `---` horizontal rules, markdown tables, mermaid/ASCII diagrams — never use

Specific rules:

- `**Label:**` on its own line → `### Label` (real header, not bold pseudo-header)
- `**Sentence.** followed by prose` → strip bold, keep as plain sentence
- `---` before `##` or `**bold` → remove (redundant section break)
- `---` before ` ```` ` fence → keep (it's template content showing proposal format)

Run format lint: `python3 scripts/validate/lint-instructions.py`

Rules documented in: `docs/instruction-lint-rules.md` (F-NO-TABLE, F-NO-DIAGRAM, F-NO-HR, F-NO-ITALIC, F-BOLD-SPARSE)

## Build

```bash
make build    # compile src/ → dist/ for all four targets (claude, codex, gemini, pi)
make fmt      # auto-fix ruff + shfmt + markdownlint
make check    # full lint (ruff, shellcheck, markdownlint, validate-config)
```

`make build` needs sandbox disabled — uv cache at `~/.cache/uv` is restricted in the CC sandbox.
