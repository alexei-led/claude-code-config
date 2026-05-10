# Deploy cc-thingz Skills and Agents

`cc-thingz` is the source of truth. Do not hand-copy generated skills or agents
into assistant-specific config directories unless you are making a temporary
one-off test. Generated exports are committed and deployable.

## Generated Outputs

| Consumer        | Output                             | Contains                                                                                  |
| --------------- | ---------------------------------- | ----------------------------------------------------------------------------------------- |
| Pi skills       | `flat/skills-pi/`                  | Pi-compatible Agent Skills directories                                                    |
| Pi agents       | `flat/agents-pi/`                  | Flat `pi-subagents` `.md` agent files                                                     |
| Pi extensions   | `flat/extensions-pi/`              | TypeScript extensions for `pi.on(...)` events and tools                                   |
| Codex CLI       | `plugins/*/skills-codex/`          | Plugin skill payloads referenced by `.codex-plugin/plugin.json`                           |
| Gemini CLI      | `AGENTS.md` + `flat/skills-codex/` | Extension context with linked skill files (via `gemini-extension.json` `contextFileName`) |
| AGENTS.md tools | `AGENTS.md` + `flat/skills-codex/` | Generated catalog for Codex, Gemini, and other AGENTS.md-aware tools                      |

Regenerate everything after changing source skills or agents:

```bash
make build
make check
```

`make build` copies the canonical `plugins/dev-workflow/hooks/smart-lint.sh`
and the `smart-lint/` modules into `platforms/pi/extensions/` so the Pi
extension can shell out to them. `make check` (= build + git diff) catches
any drift between canonical and copy in CI.

`make validate` checks canonical sources only — frontmatter, executable bits,
plugin layout, and banned tool names. Drift between canonical and generated
artifacts is caught by `make check`.

## Pi

### Requirements

Pi loads skills from `~/.pi/agent/skills/` and discovers directories containing
`SKILL.md`. Project skills can also live in `.pi/skills/`, but global deployment
uses `~/.pi/agent/skills/`.

Pi custom agents from `pi-subagents` are flat files:

```text
~/.pi/agent/agents/<name>.md
```

The filename is the agent name. No `name:` frontmatter is required.

Install the subagent extension before using `flat/agents-pi/`:

```bash
pi install npm:@tintinweb/pi-subagents
```

A pinned fork works too if you need unreleased behavior:

```bash
pi install git:github.com/alexei-led/pi-subagents@fix/pi-skill-discovery
```

### No-chezmoi install

Use the helper script from the repository root. It is dry-run by default:

```bash
scripts/release/install-pi-exports.sh
```

Apply after reviewing the plan:

```bash
scripts/release/install-pi-exports.sh --apply
```

This creates:

```text
~/.pi/agent/skills     -> <repo>/flat/skills-pi
~/.pi/agent/agents     -> <repo>/flat/agents-pi
~/.pi/agent/extensions -> <repo>/flat/extensions-pi
```

Existing `skills`, `agents`, or `extensions` paths are moved to timestamped
backups before the symlinks are created. The script does not install packages,
edit settings, or run Pi. Restart Pi or run `/reload` after applying.

### Bundled custom extensions

`platforms/pi/extensions/` ships TypeScript extensions that mirror
Claude-Code-native features in Pi. Pi auto-discovers them once
`~/.pi/agent/extensions` resolves to `flat/extensions-pi/`.

| Extension              | Role                                                     | Closest Claude Code analog |
| ---------------------- | -------------------------------------------------------- | -------------------------- |
| `smart-lint.ts`        | Runs `smart-lint.sh` after every turn that wrote a file  | PostToolUse hook           |
| `ask-user-question.ts` | `ask_user_question` tool with structured options         | AskUserQuestion            |
| `permission-gate.ts`   | Confirms dangerous bash (rm -rf, sudo, chmod 777)        | git-guardrails hook        |
| `protected-paths.ts`   | Blocks writes to `.env`, `.git/`, `node_modules/`        | file-protector hook        |
| `plan-mode/`           | `/plan` toggle for read-only exploration, step tracking  | Plan mode                  |
| `todo.ts`              | `todo` tool + `/todos` command, branch-aware state       | TaskCreate / TaskUpdate    |
| `subagent/`            | Spawns isolated `pi` processes (single, parallel, chain) | Agent / subagents          |
| `structured-output.ts` | `structured_output` tool that terminates the agent loop  | (none)                     |

All extensions import from `@mariozechner/pi-coding-agent`. `smart-lint.ts`
also reads `smart-lint.sh` from the same directory, kept in sync via
`make build` (which runs `sync-hooks` as part of regenerating every derived artifact).

[`apmantza/pi-lens`](https://github.com/apmantza/pi-lens) is a richer
post-edit pipeline (LSP, type-check, structural analysis) that overlaps
with `smart-lint.ts`. It is not bundled here — install it separately if
you prefer that stack.

### Standard third-party packages

| Package                             | Why                                                                        | Install                                  |
| ----------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------- |
| `@tintinweb/pi-subagents` (or fork) | Provides `Agent` / `get_subagent_result` / `steer_subagent` for subagents  | `pi install npm:@tintinweb/pi-subagents` |
| `@mariozechner/pi-coding-agent`     | The `ExtensionAPI` that bundled extensions import from (transitive Pi dep) | (resolved by Pi)                         |

If you want the script to regenerate exports first:

```bash
scripts/release/install-pi-exports.sh --build --apply
```

Manual equivalent:

```bash
repo="$HOME/src/cc-thingz"
mkdir -p ~/.pi/agent
mv ~/.pi/agent/skills ~/.pi/agent/skills.backup.$(date +%Y%m%d%H%M%S) 2>/dev/null || true
mv ~/.pi/agent/agents ~/.pi/agent/agents.backup.$(date +%Y%m%d%H%M%S) 2>/dev/null || true
ln -s "$repo/flat/skills-pi" ~/.pi/agent/skills
ln -s "$repo/flat/agents-pi" ~/.pi/agent/agents
```

### chezmoi install

Manage symlinks in chezmoi source instead of copying generated outputs.

Example source files:

```text
dot_pi/agent/symlink_skills.tmpl
dot_pi/agent/symlink_agents.tmpl
```

Contents:

```gotemplate
{{ .chezmoi.homeDir }}/.local/share/cc-thingz/flat/skills-pi
```

```gotemplate
{{ .chezmoi.homeDir }}/.local/share/cc-thingz/flat/agents-pi
```

Then remove copied generated resources from chezmoi source:

```text
dot_pi/agent/skills/**
dot_pi/agent/agents/**
```

Keep only private local Pi resources in chezmoi, such as settings, private API
config, local prompts, and local-only extensions. Generated cc-thingz skills and
agents belong in cc-thingz, not chezmoi. Two copies drift. They always drift.

Preview before applying:

```bash
chezmoi diff ~/.pi/agent/skills ~/.pi/agent/agents ~/.pi/agent/settings.json
```

Expected live diff:

```text
~/.pi/agent/skills -> ~/.local/share/cc-thingz/flat/skills-pi
~/.pi/agent/agents -> ~/.local/share/cc-thingz/flat/agents-pi
```

Apply only after reviewing:

```bash
chezmoi apply ~/.pi/agent/skills ~/.pi/agent/agents
```

If chezmoi refuses because a directory changed since the last write, inspect the
diff first. Use `--force` only when you intentionally replace the copied
directories with symlinks.

### Pi verification

After deployment:

```bash
ls -ld ~/.pi/agent/skills ~/.pi/agent/agents
readlink ~/.pi/agent/skills
readlink ~/.pi/agent/agents
pi list | rg 'pi-subagents|@tintinweb/pi-subagents'
```

Then restart Pi or run `/reload` in the TUI.

Smoke checks:

- Skill list includes `context7-cli`, `planning-exec`, and language skills.
- `Agent` tool is available.
- Custom agents include `scout`, `planner`, `reviewer`, `worker`, and
  `playwright-tester`.
- A read-only `Agent` call with `scout` can inspect the current repo.

### Subagent schedules

`.pi/subagent-schedules/` is reserved for Pi cron-style schedules. It is empty
by design and not deployed by `install-pi-exports.sh`. See
[.pi/subagent-schedules/README.md](../.pi/subagent-schedules/README.md) for the
intended layout when schedules are introduced.

### MCP references in source

Canonical skills ship `mcp__perplexity-ask`, `mcp__morphllm`, `mcp__deepwiki`,
and `mcp__plugin_claude-mem_mcp-search` for Claude Code. The Pi overlay
generator strips them, so Pi exports remain MCP-free.

## Codex CLI

Codex consumes plugin manifests, not the Pi flat export.

Each plugin contains:

```text
plugins/<plugin>/.codex-plugin/plugin.json
plugins/<plugin>/skills-codex/<skill>/SKILL.md
```

The plugin manifest points Codex at `./skills-codex/`:

```json
{
  "skills": "./skills-codex/"
}
```

The repo marketplace is:

```text
.agents/plugins/marketplace.json
```

Install from a clone:

```bash
git clone https://github.com/alexei-led/cc-thingz.git
cd cc-thingz
codex
```

Inside Codex, open plugin management:

```text
/plugins
```

Select the `cc-thingz` marketplace, install the plugin you want, and enable it.
The interactive plugin browser is the current documented install path for local
marketplaces. If your Codex version exposes non-interactive plugin commands, use
those only after confirming they map to the same marketplace entries.

For local development, regenerate first:

```bash
make build check
```

Codex installs plugins into its own cache. If you change `skills-codex/`, update
or reinstall the plugin from `/plugins` so Codex sees the new copy.

## Gemini CLI

Gemini consumes extensions. The root extension uses:

```text
gemini-extension.json
AGENTS.md
flat/skills-codex/<skill>/SKILL.md
```

`gemini-extension.json` sets:

```json
{
  "contextFileName": "AGENTS.md"
}
```

`AGENTS.md` links every exported skill with `@flat/skills-codex/...` references
under the `## Skill files` section, so Gemini auto-loads each SKILL.md as
extension context. The same file serves Codex CLI and other AGENTS.md-aware
tools without needing a separate `GEMINI.md`. Install the full repository
extension, not only `flat/`, so those links resolve.

Install from GitHub:

```bash
gemini extensions install https://github.com/alexei-led/cc-thingz
```

Install from a local checkout:

```bash
gemini extensions install /path/to/cc-thingz
```

For active development, link instead of copying:

```bash
gemini extensions link /path/to/cc-thingz
```

Useful checks:

```bash
gemini extensions list
gemini
```

Inside Gemini:

```text
/extensions list
```

After source changes:

```bash
make build check
gemini extensions update
```

If you used `gemini extensions link`, restart Gemini after regenerating files;
there is no install copy to refresh.

## Adding or Changing Skills

Source order for Pi skills:

1. `SKILL.pi.md`
2. `SKILL.codex.md`
3. `SKILL.md` transformed for Pi
4. `platforms/pi/skills/*` for Pi-only skills

Source order for Pi agents:

1. `plugins/<plugin>/agents/<agent>.pi.md`
2. portable `plugins/<plugin>/agents/<agent>.md`
3. `platforms/pi/agents/*.md` for Pi-only agents

Use `SKILL.pi.md` or `<agent>.pi.md` when source instructions mention tools Pi
does not have. Pi exports must use real Pi tool names and must not mention
Claude-only or MCP tool names.

Docs lookup is through `context7-cli`:

```bash
ctx7 library <name> "<specific query>"
ctx7 docs /org/project "<specific query>"
```

Fallback:

```bash
npx ctx7@latest library <name> "<specific query>"
npx ctx7@latest docs /org/project "<specific query>"
```
