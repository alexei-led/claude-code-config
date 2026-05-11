# Skill Compiler Migration

## Overview

End-to-end migration to the unified `src/` + `dist/` architecture described in `docs/skill-compiler-design.md`. Build the compiler that turns vendor-neutral skill/agent/hook sources under `src/` into per-target plugin/extension trees under `dist/` for Claude Code, Codex CLI, Gemini CLI, and Pi Agent. Migrate all remaining skills, commands, and hooks into the new structure. Generate plugin marketplace manifests from `src/plugins/<p>/plugin.yaml` composition files. Final task removes obsolete generators, old source paths (`plugins/<p>/skills/`, `agents/`, `commands/`, `skills-codex/`, `skills-pi/`, `agents-pi/`), `platforms/pi/`, `flat/`, and the Pi install helper.

**Problem solved**: today's pipeline has six scattered places for target-specific knowledge (Python constants, regex strings, `_EVENT_MAP`, preambles, `OUTPUT_DIRS`, CC-ONLY markers). After this migration: one canonical source per artifact, target-specific divergence in `<target>/{body.md, frontmatter.yaml}` overlays, dist/ is fully derived, single `make build` regenerates everything.

**Already migrated (proof-of-concept)**: 5 skills (committing-code, learning-patterns, playwright-skill, reviewing-code, spec) + 38 agents are in `src/` already. They serve as fixtures while the compiler is built.

## Context (from discovery)

- Design doc: `docs/skill-compiler-design.md` — full spec, ~500 lines, treat as authoritative
- Existing `src/` content: 5 skills, 38 agents (all in subfolder-overlay pattern: `<target>/body.md`, `<target>/frontmatter.yaml`)
- Existing `plugins/` content to migrate or delete: ~30 skills, 1 standalone command (`watch-team`), 8 spec commands (consolidated into the `spec` skill already), 10 hooks, 9 plugin dirs
- Existing generators to retire: `scripts/build/generate-skills.py`, `generate-subagents.py`, `generate-hooks.py`, `generate-agents-md.py`, `generate-flat.sh`, `scripts/release/install-pi-exports.sh`
- Target consumer constraints (from earlier research): `.claude-plugin/marketplace.json` at repo root, `.agents/plugins/marketplace.json` at repo root, `gemini-extension.json` at repo root + root `skills/` directory expected by Gemini; Codex agents are TOML, others MD+YAML
- 5 reinforcing controls on the source/generated split: `src/` prefix, `.gitattributes linguist-generated=true` for dist, generated-file watermarks, `make check` drift detection in CI, pre-commit hook auto-build
- Cross-target memory file = `AGENTS.md`; Claude uses `CLAUDE.md`; Codex reads `AGENTS.md`; Pi reads `AGENTS.md` by convention; Gemini configurable

## Development Approach

- **Testing approach**: Regular (code first, then tests) — write the implementation, then add tests for new/modified behavior before closing each task
- Complete each task fully before moving to the next
- Make small, focused changes
- **CRITICAL: every task MUST include new/updated tests** for code changes in that task
  - tests are not optional — they are a required part of the checklist
  - write unit tests for new compiler functions
  - write tests for migration-script helpers
  - write fixture-based golden tests for compiler output (compare regenerated dist against expected snapshot)
  - tests cover both success and error scenarios
- **CRITICAL: all tests must pass before starting next task** — no exceptions
- **CRITICAL: update this plan file when scope changes during implementation**
- Run tests after each change
- Maintain backward compatibility during migration phase (old generators stay until final cleanup)

## Testing Strategy

- **Unit tests** (`tests/test_compile_*.py`): cover compiler functions — frontmatter merge, body overlay (mirror/full), support-file overlay, target restriction, TOML conversion, validation
- **Fixture tests**: use the already-migrated 5 skills + 38 agents as fixtures. Generate dist/ from src/, snapshot the output, lock as goldens. Future compiler changes diff against goldens.
- **CI integration test**: `make check` (build + `git diff --exit-code`) is the regression gate — any source change must yield identical dist/ unless intentional
- **No e2e tests** for this repo (it's not a UI project; outputs are markdown/JSON files)

## Progress Tracking

- Mark completed items with `[x]` immediately when done
- Add newly discovered tasks with ➕ prefix
- Document issues/blockers with ⚠️ prefix
- Update plan if implementation deviates from original scope
- Keep plan in sync with actual work done

## Solution Overview

Build the compiler as a single Python entry point (`scripts/build/compile.py`) that runs three sub-pipelines (skills, agents, hooks) over a shared overlay engine (`scripts/build/overlay.py`). The overlay engine handles frontmatter merge (mergedeep), body overlay (mirror anchors or full replacement), and support-file overlay (`<target>/scripts/` etc.). Per-target output paths and format conversions (Codex TOML for agents) live in hardcoded `TARGETS` and `OUTPUT` dicts in `compile.py`. Plugin composition (`src/plugins/<p>/plugin.yaml`) determines plugin-grouped vs flat output distribution.

Marketplace manifests at repo root (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `gemini-extension.json`) are regenerated from `plugin.yaml` + per-plugin metadata. Root-level symlinks (`skills/`, `hooks/`) point into `dist/gemini/` for Gemini's extension-loader convention.

The migration is mechanical given the design is settled: bulk-migrate the remaining skills with a Python helper (proven approach from the 38-agent migration), write `plugin.yaml` per plugin, run the compiler, verify dist/ matches consumer expectations, then delete old paths in a final cleanup task.

## Technical Details

- **Data structures**: Python dicts/dataclasses for `Target`, `Skill`, `Agent`, `Plugin`, `OverlayResult`
- **Frontmatter merge**: `mergedeep.merge({}, base, overlay)` with overlay-side wins; filter result through `targets/<T>.yaml.allowed_keys` (or hardcoded in compiler — design says hardcoded)
- **Body overlay detection**: scan overlay content for `<!-- @replace`, `<!-- @add` (mirror mode) OR markdown headers matching base header structure (mirror mode) OR no anchors found (full replacement)
- **Codex TOML conversion**: emit `name = "..."`, `description = "..."`, markdown body → `developer_instructions = """..."""` triple-quoted, rename `effort` → `model_reasoning_effort`
- **Validator**: regex scan base SKILL.md / AGENT.md for forbidden tokens (`$ARGUMENTS`, `Task(`, `AskUserQuestion`, `mcp__`, inline-shell preprocessor backticks, `${CLAUDE_*}` variables); fail build if any are found in base. Skills with `targets: [claude]` in base frontmatter opt out of the check (Claude-only on purpose).
- **Output paths**: hardcoded dict per target (plugin-grouped for claude/codex/gemini, flat for pi)

## What Goes Where

- **Implementation Steps** (`[ ]` checkboxes): compiler code, migration helpers, fixture tests, CI updates, documentation
- **Post-Completion** (no checkboxes): install the new pipeline into downstream tooling (CI re-validation, marketplace publish verification, user-side Pi symlink instructions)

---

## Implementation Steps

### Task 1: Scaffold compiler entry point and target config

**Files:**
- Create: `scripts/build/compile.py`
- Create: `scripts/build/__init__.py` (if needed)
- Create: `tests/test_compile_scaffold.py`
- Modify: `pyproject.toml` (add `mergedeep` dependency)

- [x] add `mergedeep` to `pyproject.toml` dependencies
- [x] create `scripts/build/compile.py` with `TARGETS = ["claude", "codex", "gemini", "pi"]` and `OUTPUT` dict mapping each target to (layout, skill_dir, agent_dir, hook_dir)
- [x] add `main()` entry point that iterates targets and discovers `src/skills/*/`, `src/agents/*/`, `src/hooks/*/` (placeholders for now)
- [x] add `--dry-run` flag and basic logging
- [x] write tests for target config sanity (every target has all required fields)
- [x] run tests — must pass before task 2

### Task 2: Build shared overlay engine — frontmatter merge

**Files:**
- Create: `scripts/build/overlay.py`
- Create: `tests/test_overlay_frontmatter.py`

- [x] implement `load_base(path)` reading SKILL.md/AGENT.md/HOOK.sh frontmatter
- [x] implement `merge_frontmatter(base_meta, overlay_path)` using `mergedeep.merge` with overlay-side wins; handle missing overlay file
- [x] implement key filtering (drop unknown/forbidden keys per target — table from design doc)
- [x] strip `targets` key from output frontmatter (renderer metadata, not skill content)
- [x] write tests: base only / overlay adds keys / overlay replaces keys / overlay-side wins / missing overlay file
- [x] run tests — must pass before task 3

### Task 3: Build overlay engine — body mirror mode

**Files:**
- Modify: `scripts/build/overlay.py`
- Create: `tests/test_overlay_body_mirror.py`

- [x] implement `parse_sections(md)` splitting markdown by `^#+` headers into a tree (header path → content)
- [x] implement `apply_mirror(base_body, overlay_body)` walking overlay headers and matching them to base by path; default op = replace section subtree
- [x] implement `(_+)` append and `(+_)` prepend operations (strip suffix before path match)
- [x] implement "new section in overlay" = add to parent's children at end
- [x] handle anchor errors loudly: missing anchor for replace/append/prepend → raise with file:line
- [x] write tests: replace single section / append / prepend / add new section under parent / missing anchor errors / duplicate anchors error
- [x] run tests — must pass before task 4

### Task 4: Build overlay engine — body full-replacement detection

**Files:**
- Modify: `scripts/build/overlay.py`
- Create: `tests/test_overlay_body_full.py`

- [x] add detection: if overlay body has NO headers matching base AND no `(_+)`/`(+_)` suffixes anywhere, treat as full replacement (use overlay body as-is, ignore base body)
- [x] expose single `apply_body_overlay(base_body, overlay_body)` that internally branches mirror vs full
- [x] write tests: clear full-replacement case (different topic entirely) / mirror case (header matches base) / mixed-mode error (some headers match, some don't — pick one mode, document chosen behavior)
- [x] run tests — must pass before task 5

### Task 5: Build overlay engine — support files (scripts/, references/, assets/)

**Files:**
- Modify: `scripts/build/overlay.py`
- Create: `tests/test_overlay_support_files.py`

- [x] implement `apply_support_files(base_dir, target, output_dir)`: copy base `scripts/`, `references/`, `assets/`, then overlay `<target>/scripts/`, `<target>/references/`, `<target>/assets/` on top (same path = replace, new path = add)
- [x] preserve file mode (executable bit) when copying
- [x] never delete files (no deletion mechanism in v1 per design)
- [x] write tests: base files only / overlay adds new file / overlay replaces same path / executable bit preserved
- [x] run tests — must pass before task 6

### Task 6: Wire skill compilation pipeline

**Files:**
- Create: `scripts/build/compile_skill.py`
- Modify: `scripts/build/compile.py`
- Create: `tests/test_compile_skill.py`

- [x] implement `compile_skill(skill_dir, target, plugin_index, root)`:
  1. load base + per-target frontmatter overlay → merged frontmatter
  2. apply target restriction (`targets:` field)
  3. apply body overlay (mirror or full)
  4. inject per-target preamble if present (`scripts/build/preambles/<target>.md`)
  5. copy support files with overlay
  6. write final `SKILL.md` to dist output path
- [x] integrate into `compile.py` main loop
- [x] write fixture test: compile `src/skills/committing-code` for all 4 targets, snapshot outputs, lock as goldens
- [x] write fixture test: compile `src/skills/reviewing-code` (has Claude mirror overlay) for all 4 targets, snapshot, lock
- [x] write fixture test: compile `src/skills/playwright-skill` (has Pi full-replacement overlay) for all 4 targets
- [x] run tests — must pass before task 7

### Task 7: Implement Codex TOML conversion for agents

**Files:**
- Create: `scripts/build/codex_toml.py`
- Create: `tests/test_codex_toml.py`

- [x] implement `to_toml(agent_meta, body)` emitting:
  - `name = "..."`, `description = "..."` (TOML strings)
  - `developer_instructions = """..."""` (triple-quoted, body markdown)
  - rename `effort` → `model_reasoning_effort`
  - pass through `model`, `nickname_candidates`, `sandbox_mode`
  - emit `[mcp_servers.*]` and `[[skills.config]]` blocks from overlay yaml
- [x] handle multiline strings in TOML (escape `"""` if it appears in body)
- [x] write tests: minimal agent (name + description + body) / agent with model + effort / agent with mcp_servers / agent with skills.config / body containing triple-quotes
- [x] run tests — must pass before task 8

### Task 8: Wire agent compilation pipeline

**Files:**
- Create: `scripts/build/compile_agent.py`
- Modify: `scripts/build/compile.py`
- Create: `tests/test_compile_agent.py`

- [x] implement `compile_agent(agent_dir, target, plugin_index, root)`:
  1. load base + per-target frontmatter overlay → merged frontmatter
  2. apply target restriction (`targets:` field)
  3. apply body overlay (mirror or full)
  4. for Codex target: convert to TOML via `codex_toml.to_toml`; for others: emit as markdown + YAML
  5. write to dist output path with correct extension (`.md` or `.toml`)
- [x] integrate into `compile.py` main loop
- [x] write fixture tests: compile `src/agents/go-engineer` for all 4 targets (4 outputs: 3 .md + 1 .toml), snapshot
- [x] write fixture test: compile `src/agents/scout` (Pi-only, has `targets: [pi]`) — produces output only in dist/pi/, skipped for others
- [x] run tests — must pass before task 9

### Task 9: Migrate hooks to src/hooks/ structure

**Files:**
- Create: `src/hooks/<10 hook dirs>/HOOK.sh` (or HOOK.py for python hooks)
- Create: `src/hooks/<hook>/claude/frontmatter.yaml` where applicable
- Create: `tests/test_compile_hook.py`
- Create: `scripts/build/migrate_hooks.py` (one-shot helper)

- [x] write `scripts/build/migrate_hooks.py` to move `plugins/dev-workflow/hooks/*.sh` (and `session-start.py`) into `src/hooks/<hook>/HOOK.sh` form, extracting event metadata from current `hooks.source.yaml`
- [x] run helper — produces 9 hook dirs (smart-lint, skill-enforcer, file-protector, git-guardrails, test-runner, notify, session-start, worktree-create, worktree-remove)
- [x] for each hook dir, frontmatter (separate `meta.yaml`) declares: event (sessionstart / preedit / postedit / prebash / userpromptsubmit / notification / worktreecreate / worktreeremove), timeout, name, optional status_message
- [x] write tests: hooks discovery / event metadata parse / executable bit / support dir mirroring / idempotency
- [x] run tests — must pass before task 10

### Task 10: Wire hook compilation pipeline

**Files:**
- Create: `scripts/build/compile_hook.py`
- Modify: `scripts/build/compile.py`
- Create: `tests/test_compile_hook_pipeline.py`

- [x] implement `compile_hook(hook_dir, target, plugin_index, root)`:
  1. load hook script (`HOOK.sh` / `HOOK.py`), copy to per-plugin output dir for plugin-grouped targets
  2. for the hook event manifest, aggregate all hooks per target → write `hooks/hooks.json` for Gemini (BeforeTool/AfterTool/SessionStart syntax) and per-plugin `codex.hooks.json` (PreToolUse/PostToolUse/SessionStart syntax)
  3. Claude reads hook configuration from `.claude/settings.json` (out of scope for v1; manifest pass-through)
- [x] handle `${extensionPath}` vs `$PLUGIN_ROOT` substitution variables per target
- [x] retire the old `_EVENT_MAP` table — moves into the compiler as data
- [x] write tests: hook event → per-target manifest entries / multi-plugin aggregation for Gemini / per-plugin codex.hooks.json
- [x] run tests — must pass before task 11

### Task 11: Plugin composition and output path resolution

**Files:**
- Create: `src/plugins/<plugin>/plugin.yaml` for each of 9 plugins
- Create: `scripts/build/plugin_index.py`
- Create: `tests/test_plugin_index.py`

- [x] write `src/plugins/<plugin>/plugin.yaml` for each existing plugin (dev-workflow, dev-tools, go-dev, infra-ops, python-dev, spec-system, testing-e2e, typescript-dev, web-dev) listing `skills:`, `agents:`, `hooks:`, plus plugin metadata (name, description, version)
- [x] implement `build_plugin_index(root)` reading all `plugin.yaml` → `{skill_name → [plugin_names]}`, same for agents and hooks
- [x] implement `output_paths(name, kind, target, plugin_index, root)` returning list of dist paths (one per owning plugin for plugin-grouped targets, single flat path for Pi)
- [x] skills/agents not in any `plugin.yaml` are skipped for plugin-grouped targets but emitted for Pi (flat)
- [x] write tests: skill in one plugin / skill in multiple plugins / skill in no plugin / flat target ignores plugin_index
- [x] run tests — must pass before task 12

### Task 12: Generate marketplace manifests from plugin.yaml

**Files:**
- Create: `scripts/build/manifests.py`
- Create: `tests/test_manifests.py`
- Modify: `scripts/build/compile.py` (call after compilation)

- [x] implement `write_claude_marketplace(plugins, root)` → `.claude-plugin/marketplace.json` with plugins listing sources at `./dist/claude/plugins/<plugin>`
- [x] implement `write_codex_marketplace(plugins, root)` → `.agents/plugins/marketplace.json` with source.path at `./dist/codex/plugins/<plugin>`
- [x] implement `write_gemini_extension(plugins, root)` → `gemini-extension.json` at repo root, references `${extensionPath}/dist/gemini/`
- [x] implement `ensure_gemini_symlinks(root)` → create root-level `skills`, `hooks` symlinks pointing into `dist/gemini/`
- [x] write tests: manifests well-formed JSON / sources point to correct dist paths / Gemini symlinks created / idempotent (running twice produces no diff)
- [x] run tests — must pass before task 13

### Task 13: Add base-content validator (CC-only token detector)

**Files:**
- Create: `scripts/validate/validate_genericity.py`
- Modify: `scripts/validate/validate-config.py` (call validator)
- Create: `tests/test_validate_genericity.py`

- [ ] implement regex scanner: forbidden tokens in base SKILL.md/AGENT.md = `\$ARGUMENTS|Task\(|AskUserQuestion|TaskCreate|TodoWrite|mcp__|!`[^`]+`|\$\{CLAUDE_[A-Z_]+\}`
- [ ] opt-out: if base frontmatter has `targets: [claude]` (or just `claude`), skip the check for that artifact
- [ ] integrate into `make check` / pre-commit pipeline
- [ ] report violations as `file:line: token "<X>" not allowed in vendor-neutral base; move to claude/body.md or restrict to targets: [claude]`
- [ ] write tests: clean base passes / base with $ARGUMENTS fails / base with Task( fails / Claude-restricted base allowed to use them
- [ ] run tests — must pass before task 14

### Task 14: Wire `make build` and `make check` to new compiler

**Files:**
- Modify: `Makefile`
- Modify: `.gitattributes`

- [ ] add `make build` target invoking `uv run python scripts/build/compile.py`
- [ ] `make check` = `make build && git diff --exit-code` (drift detection)
- [ ] keep `make ci` chain intact (lint → validate → check → test)
- [ ] update `.gitattributes` with `dist/** linguist-generated=true`, `dist/** binary` for the symlink targets, and root-generated files
- [ ] (no test task — verified manually by running `make build` and checking dist/ exists and is non-empty after Tasks 1–13)
- [ ] commit a snapshot of `dist/` after running build; subsequent `make check` should be clean

### Task 15: Bulk-migrate batch 1 simple skills (frontmatter-only divergence)

**Files:**
- Create: `src/skills/<batch-1 skill dirs>/SKILL.md` (+ optional `claude/frontmatter.yaml`)
- Create: `scripts/build/migrate_skills.py` (one-shot helper, similar to migrate_agents.py)

- [ ] write `migrate_skills.py` adapting the agent-migration script: read base SKILL.md, split frontmatter (name + description stay; CC-specific keys move to claude/frontmatter.yaml)
- [ ] migrate writing-go, writing-python, writing-typescript, writing-web (4 skills)
- [ ] migrate sequential-thinking, using-modern-cli, using-cloud-cli, using-git-worktrees (4 skills)
- [ ] migrate refactoring-code, smart-explore, searching-code (3 skills)
- [ ] migrate brainstorming-ideas, grill-me, debating-ideas (3 skills) — already have codex/pi sidecars; preserve as `<target>/body.md`
- [ ] run `make build` after each batch; verify dist diff is sane
- [ ] write tests: migrated skill compiles cleanly for all 4 targets
- [ ] run tests — must pass before task 16

### Task 16: Bulk-migrate batch 2 — skills with target sidecars

**Files:**
- Create: `src/skills/<batch-2 skill dirs>/{SKILL.md, claude/, codex/, gemini/, pi/}` as needed

- [ ] migrate testing-e2e (has codex + pi sidecars) — preserve as overlay bodies
- [ ] migrate mem-history (has Pi sidecar)
- [ ] migrate exploring-repos (has Pi sidecar)
- [ ] migrate researching-web (has Pi sidecar)
- [ ] migrate reviewing-cc-config, evolving-config (Pi sidecar)
- [ ] migrate fixing-code (codex sidecar), improving-tests (codex sidecar), documenting-code (Pi sidecar)
- [ ] migrate deploying-infra (codex sidecar), managing-infra
- [ ] migrate linting-instructions, analyzing-usage, looking-up-docs, context7-cli, improve-codebase-architecture, ccgram-messaging
- [ ] each sidecar from old `SKILL.<target>.md` becomes `<target>/body.md` in the new structure
- [ ] `make build` after each cluster — verify outputs sane
- [ ] write tests: each migrated skill produces correct outputs for all 4 targets with overlay merging
- [ ] run tests — must pass before task 17

### Task 17: Migrate watch-team command as standalone skill

**Files:**
- Create: `src/skills/watch-team/SKILL.md`
- Create: `src/skills/watch-team/claude/frontmatter.yaml`

- [ ] read `plugins/dev-workflow/commands/watch-team.md`
- [ ] split frontmatter: name + description in base; allowed-tools / argument-hint / context in `claude/frontmatter.yaml`
- [ ] rewrite body intent-driven (drop `$ARGUMENTS` parsing if any, drop `Task()` syntax for capability descriptions)
- [ ] verify generic-validator passes on the base
- [ ] write test: watch-team compiles for all 4 targets
- [ ] run tests — must pass before task 18

### Task 18: Update CONTRIBUTING.md and README.md for new structure

**Files:**
- Modify: `CONTRIBUTING.md`
- Modify: `README.md`

- [ ] update CONTRIBUTING.md: src/ vs dist/ rules, vendor-neutral body checklist, no markdown tables / ASCII boxes guidance, how to add a skill / agent / hook / plugin
- [ ] update README.md installation sections: paths now under `dist/<target>/`, no manual symlink for Pi users (or document the new manual symlink convention)
- [ ] cross-link the design doc (`docs/skill-compiler-design.md`)
- [ ] (no test task — documentation)

### Task 19: Update CI workflows

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `scripts/git-hooks/pre-commit` (auto-rebuild if src/ changed)
- Modify: `scripts/git-hooks/pre-push` (already runs make check per current setup)

- [ ] CI: rename or replace the existing `overlays`/`pi-overlays`/`pi-agents`/`agents-md` make targets in CI with the unified `make build`
- [ ] update CI's Config Validation step to include the new genericity validator
- [ ] keep skill-evals CI job (unchanged — operates on the new dist/ outputs)
- [ ] update pre-commit hook to run `make build` if any file under `src/` changed
- [ ] write smoke test: CI dry-run produces same outputs as local `make build`
- [ ] run tests — must pass before task 20

### Task 20: Verify acceptance criteria

- [ ] verify `make ci` is green: lint + validate + check + test
- [ ] verify `dist/claude/plugins/<plugin>/skills/<skill>/SKILL.md` exists for every plugin's listed skills
- [ ] verify `dist/codex/plugins/<plugin>/agents/<name>.toml` exists for Codex agents (TOML)
- [ ] verify `dist/gemini/skills/<skill>/SKILL.md` and root symlink `skills -> dist/gemini/skills` works
- [ ] verify `dist/pi/skills/<skill>/SKILL.md` and `dist/pi/agents/<name>.md` exist flat
- [ ] verify root `.claude-plugin/marketplace.json` sources point at `./dist/claude/plugins/*`
- [ ] verify root `.agents/plugins/marketplace.json` sources point at `./dist/codex/plugins/*`
- [ ] verify root `gemini-extension.json` references `${extensionPath}/dist/gemini/`
- [ ] verify generic-validator catches a deliberately broken base SKILL.md (one-off check)

### Task 21: [Final] Cleanup — remove obsolete generators and old paths

**Files:**
- Delete: `scripts/build/generate-skills.py`
- Delete: `scripts/build/generate-subagents.py`
- Delete: `scripts/build/generate-hooks.py`
- Delete: `scripts/build/generate-agents-md.py`
- Delete: `scripts/build/generate-flat.sh`
- Delete: `scripts/build/preambles/` (if compiler doesn't use them; otherwise move into src/)
- Delete: `scripts/release/install-pi-exports.sh`
- Delete: `scripts/_common.py` if no remaining importers
- Delete: `plugins/*/skills/` (28 plugin/skill dirs — old source paths)
- Delete: `plugins/*/agents/` (old agent sources)
- Delete: `plugins/*/agents-pi/` (old Pi agent outputs)
- Delete: `plugins/*/skills-codex/` (old Codex outputs)
- Delete: `plugins/*/skills-pi/` (old Pi outputs)
- Delete: `plugins/*/commands/` (commands now skills under src/skills/)
- Delete: `platforms/pi/` (replaced by `dist/pi/`)
- Delete: `flat/` (replaced by `dist/`)
- Delete: CC-ONLY markers across any remaining files (grep cleanup)
- Delete: `tests/test_generate_*.py` for retired generators

- [ ] confirm new pipeline is fully functional (Tasks 1–20 green)
- [ ] grep for any remaining imports of deleted modules; fix or delete callers
- [ ] grep for `<!-- CC-ONLY` and remove markers in any file under `src/`
- [ ] delete the file/dir list above in one commit
- [ ] run `make ci` to confirm nothing depends on removed files
- [ ] update CHANGELOG.md noting the cutover
- [ ] move this plan to `docs/plans/completed/`

## Post-Completion

**Manual verification** (after merge):

- Install Claude Code plugin from this repo (`/plugin marketplace add ...`) and verify skills appear in `/<name>` menu
- Install Codex CLI plugin from `.agents/plugins/marketplace.json` and verify subagents available
- Install Gemini CLI extension (`gemini extensions install <repo-url>`) and verify skills appear in `/skills`
- Pi users: document the new install path (`ln -s $(pwd)/dist/pi/skills ~/.pi/agent/skills`, similar for agents, extensions). Update relevant docs.

**External system updates**:

- Update repo description / topics if "plugin format" or similar tags are visible
- Notify any downstream consumers of the dist/ path change in marketplace manifests
- Consider tagging a release (e.g. `v4.0.0`) marking the cutover
