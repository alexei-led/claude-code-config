---
allowed-tools:
- Bash
description: Prefer modern CLI tools — rg, fd, bat, eza, sd, dust, procs — over grep,
  find, cat, ls, sed, du, ps. Use when writing bash scripts, optimizing command chains,
  working with file searches, or replacing legacy Unix tools in workflows. NOT for
  application code logic, test writing, or infrastructure configuration.
name: using-modern-cli
user-invocable: false
---

# Modern CLI Tools

Use faster, ergonomic command-line tools installed on this system.

## Quick Reference

- **Search text** — `rg` (vs grep): 10-100x faster, respects .gitignore
- **Find files** — `fd` (vs find): Simpler syntax, ignores .git
- **View files** — `bat` (vs cat): Syntax highlighting, line numbers
- **List files** — `eza` (vs ls): Icons, git status, tree view
- **Replace text** — `sd` (vs sed): Intuitive regex, preview mode
- **Disk usage** — `dust` (vs du): Visual tree, sorted by size
- **Processes** — `procs` (vs ps): Tree view, sortable columns
- **Diff files** — `delta` (vs diff): Syntax highlighting, side-by-side

## Examples

```bash
# Search: rg instead of grep
rg "TODO" --type go           # Search Go files
rg -A 3 "error"               # 3 lines after match
rg -l "import"                # List files only

# Find: fd instead of find
fd "\.go$"                    # Find Go files
fd -e json src/               # By extension in src/
fd -x wc -l {}                # Execute on matches

# View: bat instead of cat
bat main.go                   # With syntax highlighting
bat -n file.py                # Line numbers only

# List: eza instead of ls
eza -la --git                 # Long format with git status
eza --tree -L 2               # Tree view, 2 levels

# Replace: sd instead of sed
sd "old" "new" file.txt       # Simple replacement
sd -p "pattern" "new" file    # Preview changes first
sd -p 'colour' 'color' docs/**/*.md  # Preview only; do not apply without explicit ask

# Disk: dust instead of du
dust -d 2                     # 2 levels deep

# Processes: procs instead of ps
procs --tree                  # Process tree
```

## Rules

- For preview-only replacement tasks, use `sd -p` and state it is preview-only. Do not emit a non-preview `sd` command unless the user explicitly asked to apply.
- If a modern tool is not on `PATH`, fall back to the legacy equivalent and note the fallback.
- Do not install missing tools silently; report what is missing and suggest `brew install <tool>`.

## Productivity Tools

```bash
# Fuzzy finder (pipe with fd/rg)
vim $(fd . | fzf)
rg "pattern" | fzf

# Benchmarking
hyperfine "rg pattern" "grep -r pattern"

# Code statistics
tokei .

# Markdown preview
glow README.md

# JSON/YAML processing
jq '.key' file.json
yq '.key' file.yaml
```
