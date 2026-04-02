# Add AGENTS.md Generation and Rebrand as CC-First Plugin Suite

## Overview

Two complementary changes to cc-thingz:

1. **R1 — AGENTS.md generation**: Add a build script that generates `AGENTS.md` from the actual `flat/skills-codex/` directory, categorized by plugin. This is the Linux Foundation-backed standard adopted by 60K+ repos and supported by Codex CLI, Gemini CLI, GitHub Copilot, Cursor, and 15+ other tools. Currently cc-thingz has no AGENTS.md at all.

2. **R2(A) — CC-first rebrand**: Rebrand from "cross-platform collection" to "Claude Code plugin suite with skill export." This honestly reflects the architecture: 34 agents, 9 hooks, 9 commands are CC-only. Codex/Gemini get the 29 portable skills — valuable, but a subset.

**Version**: 1.4.0 (minor — new feature + identity change)

## Context

- No `AGENTS.md` exists anywhere in the repo
- `GEMINI.md` is hand-authored and has drifted (23 of 29 skills listed, missing 6)
- The build system already generates `skills-codex/` overlays and `flat/` symlinks
- `validate-config.py` validates CC, Codex, and Gemini manifests but nothing for AGENTS.md
- README line 12 says "cross-platform collection" but 80%+ features are CC-only
- Current version: 1.3.0 (released 2026-04-02)

### Skills missing from GEMINI.md

`evolving-config`, `learning-patterns`, `linting-instructions`, `mem-history`, `smart-explore`, `using-gemini` — 6 skills present in `flat/skills-codex/` but not referenced.

## Development Approach

- **Testing approach**: Regular (code first, then tests)
- Complete each task fully before moving to the next
- Run `make fmt && make ci` after each task
- **CRITICAL**: every task MUST include new/updated tests for code changes
- **CRITICAL**: update this plan file when scope changes during implementation

## Testing Strategy

- **Unit tests**: Add tests for the new `generate-agents-md.py` script in `tests/`
- **Validation**: Add `validate-agents-md` check to `make validate`
- **CI**: Ensure AGENTS.md generation + validation runs in CI pipeline

## Progress Tracking

- Mark completed items with `[x]` immediately when done
- Add newly discovered tasks with ➕ prefix
- Document issues/blockers with ⚠️ prefix

## Implementation Steps

### Task 1: Create `scripts/generate-agents-md.py`

**Files:**
- Create: `scripts/generate-agents-md.py`

Script walks `flat/skills-codex/*/SKILL.md`, reads frontmatter (`name`, `description`), groups by plugin (resolve symlink → plugin name), and emits `AGENTS.md`.

Output format:

```markdown
# cc-thingz — AI Coding Skills

A Claude Code plugin suite with portable skill export for Codex CLI, Gemini CLI,
and AGENTS.md-compatible tools.

30 skills across 9 plugins — code review, language tooling, infrastructure,
testing, and developer utilities.

## Skills

### Development Workflow
| Skill | Description |
|-------|-------------|
| reviewing-code | Multi-agent code review ... |
...

### Go Development
...
```

- [ ] Create `scripts/generate-agents-md.py` with `sync`, `--check`, `--hook` modes (matching `generate-overlays.py` pattern)
- [ ] Walk `flat/skills-codex/*/SKILL.md`, parse frontmatter for `name` and `description`
- [ ] Resolve symlinks to determine plugin grouping (`flat/skills-codex/X -> ../../plugins/<plugin>/skills-codex/X`)
- [ ] Map plugin names to human-friendly category titles (e.g., `dev-workflow` → `Development Workflow`)
- [ ] Generate markdown table per category with skill name and description
- [ ] `--check` mode: compare generated content vs existing `AGENTS.md`, exit 1 if stale
- [ ] `--hook` mode: sync + `git add AGENTS.md`
- [ ] Make script executable (`chmod +x`)

### Task 2: Generate initial AGENTS.md and fix GEMINI.md drift

**Files:**
- Create: `AGENTS.md` (generated)
- Modify: `GEMINI.md`

- [ ] Run `scripts/generate-agents-md.py` to create `AGENTS.md`
- [ ] Review generated output for accuracy and formatting
- [ ] Fix `GEMINI.md`: add 6 missing skill includes (`evolving-config`, `learning-patterns`, `linting-instructions`, `mem-history`, `smart-explore`, `using-gemini`)
- [ ] Verify `AGENTS.md` skill count matches `flat/skills-codex/` count

### Task 3: Wire AGENTS.md into build system

**Files:**
- Modify: `Makefile`
- Modify: `scripts/validate-config.py`

- [ ] Add `agents-md` target to Makefile: `uv run python scripts/generate-agents-md.py`
- [ ] Add `validate-agents-md` target: `uv run python scripts/generate-agents-md.py --check`
- [ ] Add `validate-agents-md` to the `validate` phony prerequisites
- [ ] Update `ci` target: change `lint overlays validate test` to `lint overlays agents-md validate test` (generate before validate)
- [ ] Add `validate_agents_md()` function to `validate-config.py`: check `AGENTS.md` exists (warning if missing)
- [ ] Write tests for `generate-agents-md.py` in `tests/test_generate_agents_md.py`
- [ ] Run `make ci` — must pass

### Task 4: Rebrand README.md

**Files:**
- Modify: `README.md`

Changes to make (line numbers reference current file):

- [ ] **Line 12 tagline**: Replace "A cross-platform collection of AI coding skills and plugins for **Claude Code**, **OpenAI Codex CLI**, and **Google Gemini CLI**" → "A **Claude Code** plugin suite — 30 skills, 34 agents, 9 hooks, and 9 commands — with portable skill export for Codex CLI, Gemini CLI, and AGENTS.md-compatible tools"
- [ ] **Line 14 opening**: Replace "Originally developed for Claude Code, all skills are now served with platform-optimized instructions..." → "Built for Claude Code, with all 29 skills exported as platform-optimized instructions for Codex CLI, Gemini CLI, and any tool supporting the AGENTS.md standard."
- [ ] **Badges (lines 6-8)**: Change Codex badge from "plugin_compatible" to "skill_export", Gemini badge from "extension_compatible" to "skill_export". Add AGENTS.md badge.
- [ ] **Section "Cross-Platform Architecture" (line 189)**: Rename to "Skill Export Architecture". Update opening sentence to "All skills are exported with platform-optimized instructions via a build system..."
- [ ] **Skills section intro (line 111)**: Replace "All 30 skills work across Claude Code, Codex CLI, and Gemini CLI" → "All skills are authored for Claude Code and exported with platform-optimized instructions for Codex CLI, Gemini CLI, and AGENTS.md-compatible tools."
- [ ] **Installation section**: Add AGENTS.md mention under Codex/Gemini — note that `AGENTS.md` at repo root is available for any AGENTS.md-compatible tool
- [ ] Review all remaining "cross-platform" wording and soften to "skill export" where appropriate

### Task 5: Update metadata and marketplace descriptions

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `gemini-extension.json`

- [ ] Update `.claude-plugin/marketplace.json` `metadata.description`: "A Claude Code plugin suite for development workflows, language tooling, infrastructure ops, and more — with portable skill export for Codex CLI and Gemini CLI"
- [ ] Update `gemini-extension.json` `description`: "29 portable development skills exported from cc-thingz — Go, Python, TypeScript, web, infrastructure, code review, testing, and more"
- [ ] Verify no other files reference "cross-platform" in metadata fields

### Task 6: Add tests for generate-agents-md.py

**Files:**
- Create: `tests/test_generate_agents_md.py`

- [ ] Test `compute_desired_content()` with a mock `flat/skills-codex/` directory containing sample skills
- [ ] Test symlink resolution for plugin grouping
- [ ] Test `--check` mode returns 0 when in sync, 1 when stale
- [ ] Test missing `flat/skills-codex/` directory handled gracefully
- [ ] Test category mapping (plugin name → display title)
- [ ] Run `make test` — all tests must pass

### Task 7: Update CHANGELOG and validate

**Files:**
- Modify: `CHANGELOG.md`

- [ ] Add `## [1.4.0] - 2026-04-02` entry with Added/Changed sections
- [ ] Added: AGENTS.md generation (`scripts/generate-agents-md.py`), `make agents-md` and `validate-agents-md` targets, AGENTS.md badge
- [ ] Changed: Rebranded from "cross-platform collection" to "Claude Code plugin suite with skill export", updated README messaging, marketplace descriptions, GEMINI.md skill list (added 6 missing skills)
- [ ] Fixed: GEMINI.md skill drift (6 skills were missing)
- [ ] Run `make ci` — full pipeline must pass
- [ ] Verify AGENTS.md, GEMINI.md, and all configs are in sync

### Task 8: Verify acceptance criteria

- [ ] `AGENTS.md` exists at repo root with all 29 skills categorized
- [ ] `make agents-md` generates `AGENTS.md` from `flat/skills-codex/`
- [ ] `make validate-agents-md` (via `make validate`) exits 0
- [ ] `GEMINI.md` lists all 29 skills (no drift)
- [ ] README leads with Claude Code, positions Codex/Gemini as skill export
- [ ] No "cross-platform" language in tagline, badges, or section headers
- [ ] All tests pass: `make ci`
- [ ] CHANGELOG documents all changes under 1.4.0

### Task 9: [Final] Move plan to completed

- [ ] Move this plan to `docs/plans/completed/`

## Technical Details

### AGENTS.md format

Pure markdown, no frontmatter. Follows the Linux Foundation AGENTS.md spec:
- Project overview with identity
- Skill catalog organized by category (table format)
- No @includes (Codex reads raw markdown)
- Size target: under 32 KiB (Codex `project_doc_max_bytes` default)

### Plugin → Category mapping

```python
PLUGIN_TITLES = {
    "dev-workflow": "Development Workflow",
    "go-dev": "Go Development",
    "python-dev": "Python Development",
    "typescript-dev": "TypeScript Development",
    "web-dev": "Web Development",
    "infra-ops": "Infrastructure & Operations",
    "dev-tools": "Developer Tools",
    "spec-system": "Spec-Driven Development",
    "testing-e2e": "End-to-End Testing",
}
```

### Symlink resolution

`flat/skills-codex/writing-go` → `../../plugins/go-dev/skills-codex/writing-go`

Extract plugin name from resolved path: `resolved.parts` after `plugins/` and before `skills-codex/`.

## Post-Completion

**Version bump**: Run `make release V=1.4.0` after all changes committed.

**GitHub release**: Create release with notes covering AGENTS.md adoption and CC-first rebrand.
