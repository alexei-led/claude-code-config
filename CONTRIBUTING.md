# Contributing

> [!CAUTION]
> **First-time contributors: open a GitHub issue first. Do not open a pull request.**
>
> PRs from first-time contributors will be closed without review. Open an
> [issue](https://github.com/alexei-led/cc-thingz/issues/new/choose) describing
> the bug, idea, or proposed change. Wait for a maintainer to acknowledge and
> agree on scope before writing code. Once you have at least one merged PR,
> this restriction no longer applies.
>
> **Why:** this repo encodes opinionated, hand-tuned prompts. Drive-by PRs that
> tweak wording, add abstractions, or refactor "for cleanliness" cost more to
> review than they save. Issues are cheap. Aligned PRs ship.

## Table of Contents

- [Ground Rules](#ground-rules)
- [Setup](#setup)
- [Repository Layout](#repository-layout)
- [Development Workflow](#development-workflow)
- [Adding a Plugin](#adding-a-plugin)
- [Adding a Skill, Agent, Hook, or Command](#adding-a-skill-agent-hook-or-command)
- [Pi Exports](#pi-exports)
- [Make Targets](#make-targets)
- [Pull Request Checklist](#pull-request-checklist)
- [Commit and PR Style](#commit-and-pr-style)
- [Reporting Bugs and Security Issues](#reporting-bugs-and-security-issues)

## Ground Rules

- **Canonical sources only.** Edit files under `plugins/<plugin>/skills/`,
  `plugins/<plugin>/agents/`, `plugins/<plugin>/hooks/`, and the top-level
  `scripts/`. Everything under `skills-codex/`, `skills-pi/`, `agents-pi/`,
  `flat/`, `AGENTS.md`, and `GEMINI.md` is generated — do not edit by hand.
- **Run `make build` after changes.** Generated artifacts must be in sync.
  CI runs `make check` (build + `git diff --exit-code`) and will fail on drift.
- **Surgical changes.** Match existing style. Don't rename, restructure, or
  reformat unrelated files in the same PR.
- **No new dependencies without discussion.** Open an issue first.

## Setup

```bash
make setup    # Install pre-commit hook and dev dependencies (uv-managed)
```

Required tools on `PATH`:

- `uv` (Python toolchain)
- `shellcheck` and `shfmt` (shell linting)
- `markdownlint-cli2` (optional but recommended)
- `bun` or `node` if you plan to run `make skill-evals*`

## Repository Layout

```text
cc-thingz/
├── plugins/<plugin>/
│   ├── .claude-plugin/plugin.json     # Claude Code manifest
│   ├── .codex-plugin/plugin.json      # Codex CLI manifest
│   ├── gemini-extension.json          # Gemini CLI manifest
│   ├── skills/<skill>/SKILL.md        # Canonical skill source (CC-flavored)
│   ├── skills-codex/<skill>/SKILL.md  # Generated — Codex/Gemini overlay
│   ├── skills-pi/<skill>/SKILL.md     # Generated — Pi overlay
│   ├── agents/<agent>.md              # Claude Code agent
│   ├── agents/<agent>.pi.md           # Optional Pi agent override
│   ├── hooks/                         # Claude Code only
│   └── commands/                      # Claude Code only
├── platforms/pi/                      # Pi-only runtime skills/agents
├── scripts/                           # Build, validate, install scripts
├── flat/                              # Generated symlink trees for chezmoi/Pi
├── tests/                             # pytest + bats
├── AGENTS.md                          # Generated — AGENTS.md standard output
├── GEMINI.md                          # Generated — Gemini context (mirrors AGENTS.md)
└── Makefile
```

## Development Workflow

```bash
# 1. Make changes to canonical sources under plugins/<plugin>/...

# 2. Regenerate derived artifacts
make build

# 3. Verify everything passes locally
make ci          # lint + validate + check (drift) + test

# 4. Commit canonical source AND regenerated artifacts together
git add -A
git commit
```

If `make check` fails after `make build`, it means generated artifacts
changed — commit them. Never use `--no-verify` to bypass hooks.

## Adding a Plugin

1. Create `plugins/<your-plugin>/` and add three manifests:

   `plugins/<your-plugin>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "your-plugin",
     "description": "What it does",
     "version": "2.2.0",
     "author": { "name": "Your Name" }
   }
   ```

   `plugins/<your-plugin>/.codex-plugin/plugin.json`:

   ```json
   {
     "name": "your-plugin",
     "version": "2.2.0",
     "description": "What it does",
     "skills": "./skills-codex/",
     "interface": {
       "displayName": "Your Plugin",
       "shortDescription": "What it does",
       "developerName": "Your Name",
       "category": "Development"
     }
   }
   ```

   `plugins/<your-plugin>/gemini-extension.json`:

   ```json
   {
     "name": "your-plugin",
     "version": "2.2.0",
     "description": "What it does"
   }
   ```

2. Register the plugin in **both** marketplace files:
   - `.claude-plugin/marketplace.json`
   - `.agents/plugins/marketplace.json`

3. Add a `plugins/<your-plugin>/README.md` documenting the plugin.

4. Run `make build` to generate Codex/Pi overlays, AGENTS.md, GEMINI.md,
   and `flat/` symlinks.

5. Update the plugin table in the top-level `README.md`.

## Adding a Skill, Agent, Hook, or Command

- **Skills:** add `plugins/<plugin>/skills/<skill>/SKILL.md` with name +
  description frontmatter. Codex, Gemini, and Pi versions are generated.
- **Agents:** add `plugins/<plugin>/agents/<agent>.md`. Add
  `<agent>.pi.md` only if Pi cannot run the canonical version.
- **Hooks:** add the script under `plugins/<plugin>/hooks/`. Hook
  registration is generated from `hooks.source.yaml` — run
  `make generate-hooks` after editing the source.
- **Commands:** Claude Code only — add under `plugins/<plugin>/commands/`.

After any of the above, run `make build && make ci`.

## Pi Exports

Pi output is generated, not hand-ported.

```bash
make build validate
```

Rules:

- Add `SKILL.pi.md` only when the canonical skill references tools or
  workflows Pi cannot run.
- Pi-allowed tools: `read`, `bash`, `edit`, `write`, `ask_user_question`,
  `structured_output`, `todo`, `Agent`, `get_subagent_result`,
  `steer_subagent`, `web_search`, `web_answer`, `web_research`.
- For Context7 docs lookup in Pi, use `ctx7` or `npx ctx7@latest` — never
  the Context7 MCP server.
- Pi-only runtime skills live under `platforms/pi/skills/`.
- Pi-only agents live under `platforms/pi/agents/` as flat `.md` files
  (filename is the agent name).

Chezmoi deployment (optional) symlinks:

```text
~/.pi/agent/skills -> ~/.local/share/cc-thingz/flat/skills-pi
~/.pi/agent/agents -> ~/.local/share/cc-thingz/flat/agents-pi
```

Do not keep copied cc-derived skills or agents in chezmoi after the symlink
migration. Two sources of truth means twice the rot.

See [docs/pi-skill-export.md](docs/pi-skill-export.md) for full Pi, Codex,
and Gemini deployment details.

## Make Targets

```bash
make help             # List all targets
make ci               # Full local CI (lint + validate + check + test)
make lint             # Python (ruff) + shell (shellcheck/shfmt) + markdown
make test             # pytest
make validate         # Frontmatter, executable bits, plugin layout
make build            # Regenerate every derived artifact
make check            # build + git diff --exit-code (drift detection — CI gate)
make fmt              # Auto-format Python and shell
make skill-evals-fast # Fast paid eval loop (no baseline, no HTML, advisory)
```

## Pull Request Checklist

Before opening a PR, confirm **all** of the following:

- [ ] You have at least one merged PR, **or** an existing issue acknowledged
      by a maintainer.
- [ ] Linked issue number is in the PR description (`Closes #123`).
- [ ] `make ci` passes locally.
- [ ] Plugin version bumped in `.claude-plugin/plugin.json` and
      `.codex-plugin/plugin.json` (and `gemini-extension.json` if applicable).
- [ ] Both marketplace files updated if adding/removing plugins.
- [ ] `CHANGELOG.md` entry added.
- [ ] Top-level `README.md` plugin table updated (skill/agent counts) if
      counts changed.
- [ ] Plugin `README.md` updated if you added skills, agents, hooks, or
      commands.
- [ ] `make build` was run; generated artifacts are committed in the same PR.
- [ ] PR is focused on one logical change. No drive-by reformatting.

## Commit and PR Style

- Imperative mood, lowercase type prefix:
  `feat: add foo skill`, `fix(go-dev): correct lint hook`, `docs: …`,
  `refactor: …`, `chore: …`.
- Body explains **why**, not what — the diff already shows what.
- One logical change per commit. Squash noise locally before pushing.
- PR title matches the merge commit you'd want in `git log`.

## Reporting Bugs and Security Issues

- **Bugs and feature ideas:** open a GitHub
  [issue](https://github.com/alexei-led/cc-thingz/issues/new/choose) with
  a minimal reproduction.
- **Security vulnerabilities:** do **not** open a public issue. Email
  alexei.led@gmail.com with details and proof of concept. Acknowledgement
  within 72 hours.
