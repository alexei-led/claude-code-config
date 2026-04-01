# Changelog

All notable changes to this Claude Code configuration are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
major = breaking config/hook changes, minor = new skills/features, patch = fixes.

## [1.2.2] - 2026-04-01

Documentation accuracy fixes for README.

### Fixed

- Agent model table: engineers were listed as opus but are actually sonnet
- Add 4 missing skills to user-invocable table (analyzing-usage, learning-patterns, linting-instructions, using-git-worktrees)
- Move learning-patterns and using-git-worktrees from auto-activated to user-invocable
- Add playwright-skill to auto-activated table, pdf-parser to agents table
- Update dev-tools skill count: 13 → 14
- Narrow linting-instructions enforcer triggers to skill/agent authoring context
- Clarify linting-instructions description: references Anthropic model cards

## [1.2.1] - 2026-04-01

System card-derived instruction hardening for all agents and skills.

### Added

- `linting-instructions` skill: model-based prompt review against system card rules
- `scripts/lint-instructions.py`: advisory regex linter with uv inline deps
- `docs/instruction-lint-rules.md`: 12 rules (6 universal, 3 opus, 3 sonnet) with citations
- `make lint-instructions` target (advisory, doesn't fail CI)
- Skill-enforcer trigger for linting-instructions

### Fixed

- Opus agents (6): add efficiency constraints, tool failure handling, grounding, read-only clauses
- Sonnet agents (24): add anti-eagerness clauses, scope locks for review agents
- `infra-engineer`: add destructive action safety for cloud CLI commands
- `docs-keeper`: add write scope ceiling for Edit/Write/MultiEdit tools
- `web-engineer`: add scope boundaries, failure handling, workflow structure
- `web-docs`: add "Run Tooling First" section (was only doc agent missing it)
- `managing-infra`: add mandatory dry-run before terraform/kubectl/helm apply
- Writing skills (4): add verify-after-generate with build/lint commands
- `committing-code`: add secrets detection guard for .env/pem/credentials
- `documenting-code`, `improving-tests`, `debating-ideas`: add failure handling
- `mem-history`: add scope description and output format template

### Changed

- Skill count: 29 → 30 (new linting-instructions in dev-tools)
- All instruction fixes derived from Claude Opus 4.6 and Sonnet 4.6 system cards

## [1.2.0] - 2026-03-31

Optional claude-mem integration for AST-based code navigation and cross-session memory.

### Added

- `smart-explore` skill: AST-based code navigation via smart_outline/smart_search/smart_unfold (10-20x token savings)
- `mem-history` skill: cross-session memory search with 3-layer workflow and graceful fallback
- Claude-mem MCP tools added to all 30 agents (25 review + 5 engineer) as optional tools
- Historical context check in `reviewing-code` (Step 0) and `fixing-code` (Pre-Phase 2)
- Project history option in `brainstorming-ideas` Phase 3 checkpoint
- Smart Explore column in `searching-code` decision table
- `smart-explore` and `mem-history` detection patterns in skill-enforcer hook
- Claude-Mem Integration section in README with installation guide and resilience docs

### Changed

- Skill count: 27 → 29 (2 new skills in dev-tools plugin)
- All review agent frontmatter converted to multi-line tools format
- Engineer agents gain `### Memory (claude-mem)` body section

## [1.1.1] - 2026-03-31

Full repository review and cleanup.

### Fixed

- Broken specctl test path after plugin restructuring (10 test failures)
- Ruff config referencing deleted `scripts/ce` (linter was scanning nothing)
- Plugin version mismatch (all plugin.json now match marketplace 1.1.1)
- Skill-enforcer missing 4 user-invocable skills
- `learning-patterns` skill name mismatch (was `learn`, now matches directory)
- CI gate not detecting cancelled job state
- README skill counts (26 → 27)

### Added

- Per-plugin README.md for all 9 plugins
- Makefile with lint, test, validate, fmt, flat, ci, setup, release targets
- CONTRIBUTING.md with plugin authoring guide and PR checklist
- Pre-commit hook running full CI pipeline
- Release tag script with automatic version bumping
- CI badge, version badge, and project narrative in README
- Dependabot pip ecosystem tracking
- `using-gemini` skill documented in README

### Changed

- Replaced monolithic GUIDE.md with per-plugin READMEs + expanded project README
- CI and release workflows now use Makefile targets
- All lint/test jobs run unconditionally on push to master
- Dependabot frequency: monthly → weekly

### Removed

- GUIDE.md (split into per-plugin READMEs)
- Orphaned root files: claude-powerline.json, MCP_Sequential.md, .claude-hooks-config.sh, .claude-hooks-ignore
- install-tools.sh (user-specific, not marketplace-related)

## [1.1.0] - 2026-03-30

Restructured as a 9-plugin marketplace for community sharing.

### Added

- MIT LICENSE file
- Marketplace metadata (description, version, categories, tags)
- Plugin-level `plugin.json` manifests for all 9 plugins

### Changed

- Restructured from flat config into 9 installable plugins
- 26 skills, 34 agents, 9 hooks, 9 commands across all plugins
- Updated README with correct installation syntax per official plugin docs
- Updated GUIDE with plugin-relative paths and companion tool notes

## [1.0.0] - 2026-02-28

Initial versioned release of the Claude Code configuration.

### Added

- 23 skills: brainstorming, committing, debating, deploying-infra, documenting,
  evolving-config, fixing, improving-tests, learning-patterns, looking-up-docs,
  managing-infra, refactoring, researching-web, reviewing, searching,
  testing-e2e, using-cloud-cli, using-git-worktrees, using-modern-cli,
  writing-go, writing-python, writing-typescript, writing-web
- 14 agents for Go, Python, TypeScript, web, infrastructure, and planning
- Spec-driven development system (specctl + spec skills)
- CI workflow with config validation, linting, and tests
- Global CLAUDE.md with universal development practices
- Project CLAUDE.md with config-repo-specific guidance
- Git hooks: gitleaks pre-commit, enforcer post-tool-use
