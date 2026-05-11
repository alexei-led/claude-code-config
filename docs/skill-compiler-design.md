# Skill Compiler — Design

**Status**: Implemented (see `scripts/build/compile.py`). The migration plan at `docs/plans/completed/20260511-skill-compiler-migration.md` is finished; this doc remains as the architectural reference.
**Principle**: KISS. Single source of truth under `src/`. All generated outputs under `dist/`. Root-level files only where target platforms require them.

## Goal

Compile vendor-neutral skills into per-target plugin/extension trees for Claude Code, Codex CLI, Gemini CLI, and Pi Agent. Base follows [agentskills.io](https://agentskills.io/specification). Per-target overlays add divergence where needed.

## Layout at a glance

```
src/                                # ALL hand-edited
  skills/<skill>/                   # one dir per skill (see "Skill source layout")
  agents/<agent>/                   # one dir per agent (see "Agent source layout")
  hooks/<hook>.sh                   # flat hook scripts
  hooks/hooks.source.yaml           # hook event source-of-truth
  plugins/<plugin>/plugin.yaml      # plugin composition manifests

dist/                               # ALL generated (linguist-generated=true)
  claude/plugins/<plugin>/...       # full CC plugin tree (skills + agents)
  codex/plugins/<plugin>/...        # full Codex plugin tree (skills + .toml agents)
  gemini/skills/<skill>/            # Gemini skill trees
  gemini/agents/<agent>.md          # Gemini subagents
  gemini/hooks/hooks.json           # Gemini hook manifest
  pi/skills/<skill>/                # flat Pi skills
  pi/agents/<agent>.md              # flat Pi agents

# Generated, at repo root (platforms require root location):
.claude-plugin/marketplace.json     # CC marketplace; sources → ./dist/claude/plugins/*
.agents/plugins/marketplace.json    # Codex marketplace; sources → ./dist/codex/plugins/*
gemini-extension.json               # Gemini manifest; references ${extensionPath}/dist/gemini/*
AGENTS.md                           # cross-platform catalog

# Committed symlinks at root (Gemini requires conventional locations):
skills      -> dist/gemini/skills
hooks       -> dist/gemini/hooks
```

Rules of thumb:

- If it's under `src/` → edit it.
- If it's under `dist/` or is a generated root-level file → do not edit; run `make build`.
- Root symlinks exist solely because Gemini's extension loader scans extension-root subdirs by hard-coded names.

## Skill source layout

```
src/skills/<skill>/
  SKILL.md                          # vendor-neutral base (agentskills.io)
  scripts/, references/, assets/    # base support files
  <target>/                         # ALL per-target customization — optional
    body.md                         # per-target body overlay (full or mirror mode) — partial, no frontmatter
    frontmatter.yaml                # per-target frontmatter overlay — partial
    scripts/, references/, assets/  # per-target support-file overlay
```

`<target>` ∈ {`claude`, `codex`, `gemini`, `pi`}. One subfolder per target groups everything that target customizes — body, frontmatter, support files. Empty subfolder absent → no customization for that target. One mechanism, scales to any per-target file tree.

**Base `SKILL.md`**: agentskills.io frontmatter (`name`, `description`) + markdown body. No agent-specific tool names. No model-specific phrasing. Use generic instructions; models know how to invoke `git`, linters, etc.

**Claude-only runtime features must not appear in base.** These work on Claude Code only and pass through verbatim on other targets (no expansion):

- `$ARGUMENTS`, `$N`, `$name` argument substitutions
- `` !`cmd` `` and ` ```! ` dynamic context injection (preprocessor)
- `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` variables

If a skill needs them, put the whole body in `claude/body.md` (full-replacement overlay) and keep base `SKILL.md` body generic. See OpenAI's [Codex migration differences](https://github.com/openai/skills/blob/main/skills/.curated/migrate-to-codex/references/differences.md) for the complete list of Claude features that don't translate to Codex.

**Support files**: renderer copies base `scripts/`, `references/`, `assets/`, then overlays `<target>/<dir>/` on top — matching paths replace, new paths add. No deletion.

## Agent source layout

Mirrors skills. Agents are sub-task delegates that other agents (or the main agent) spawn via their tool — `Task` (Claude), `spawn_agent` (Codex), `invoke_agent` (Gemini), `Agent` (Pi extension).

```
src/agents/<agent>/
  AGENT.md                          # vendor-neutral base — frontmatter (name, description) + markdown body (system prompt)
  <target>/                         # per-target customization (optional)
    body.md                         # body overlay (full or mirror) — partial, no frontmatter
    frontmatter.yaml                # per-target frontmatter overlay — partial
```

Agent name = parent directory name (`src/agents/go-engineer/AGENT.md` → agent `go-engineer`).

### Subagent support matrix (verified from official docs)

| Tool   | Project agent path                 | Format    | Required base fields                            |
| ------ | ---------------------------------- | --------- | ----------------------------------------------- |
| Claude | `.claude/agents/<name>.md`         | MD + YAML | `name`, `description`                           |
| Codex  | `.codex/agents/<name>.toml`        | **TOML**  | `name`, `description`, `developer_instructions` |
| Gemini | `.gemini/agents/<name>.md`         | MD + YAML | `name`, `description`                           |
| Pi     | `.pi/agents/<name>.md` (extension) | MD + YAML | `description` (`name` from filename)            |

Sources: [Claude](https://code.claude.com/docs/en/agent-teams), [Codex](https://developers.openai.com/codex/subagents), [Gemini](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md), Pi (via user-installed subagent extension).

**No cross-tool `.agents/agents/` convention** — unlike skills, agents use vendor-namespaced directories.

### Codex TOML conversion

Codex requires TOML, not Markdown+YAML. The compiler converts:

- `name` → `name = "..."`
- `description` → `description = "..."`
- Markdown body → `developer_instructions = """..."""` (TOML triple-quoted)
- `model` → `model = "..."`
- `effort` → `model_reasoning_effort = "..."` (field rename)
- `tools` → not directly mapped; Codex uses `[mcp_servers.*]` blocks and `[[skills.config]]` arrays instead
- `nickname_candidates`, `sandbox_mode` → pass-through from `frontmatter.codex.yaml` overlay

Example Codex output:

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, missing tests."
developer_instructions = """
Review code like an owner. Prioritize correctness, security, regressions, and missing tests.
"""
model = "gpt-5.4"
model_reasoning_effort = "high"

[[skills.config]]
path = "reviewing-code"
enabled = true
```

### Frontmatter field mapping across targets

| Capability       | Claude             | Codex (TOML)                        | Gemini                     | Pi             |
| ---------------- | ------------------ | ----------------------------------- | -------------------------- | -------------- |
| Model override   | `model`            | `model`                             | (n/a)                      | `model`        |
| Reasoning effort | `effort`           | `model_reasoning_effort`            | (n/a)                      | `thinking`     |
| Tool allowlist   | `tools` (list)     | (use `mcp_servers`/`skills.config`) | `tools` (list + wildcards) | `tools` (csv)  |
| Color/UI hint    | `color`            | `nickname_candidates`               | (n/a)                      | (n/a)          |
| Skill access     | `skills` (preload) | `[[skills.config]]`                 | (via tools)                | `skills` (csv) |

Author puts the target-native form in `<target>/frontmatter.yaml`; the compiler does not auto-translate between fields with the same intent.

## Agent compiler output

| Target | Layout         | Output path                                                | Format conversion    |
| ------ | -------------- | ---------------------------------------------------------- | -------------------- |
| Claude | plugin-grouped | `dist/claude/plugins/<plugin>/agents/<name>.md`            | none                 |
| Codex  | plugin-grouped | `dist/codex/plugins/<plugin>/agents/<name>.toml`           | **YAML+body → TOML** |
| Gemini | flat           | `dist/gemini/agents/<name>.md` (extension root convention) | none                 |
| Pi     | flat           | `dist/pi/agents/<name>.md`                                 | none                 |

`plugin.yaml` lists agents alongside skills:

```yaml
skills: [reviewing-code, fixing-code, ...]
agents: [docs-keeper, go-engineer, go-qa, py-engineer, py-qa, ...]
hooks: [smart-lint, file-protector, ...]
```

## Body overlay (`<target>/body.md`)

Two modes, detected by content:

- **Full replacement**: no headers matching base → renderer uses overlay body as-is.
- **Mirror mode**: overlay mirrors base header structure; each header is an anchor.

### Mirror-mode operations

| Overlay header    | In base? | Op      | Result                                          |
| ----------------- | -------- | ------- | ----------------------------------------------- |
| `## section`      | yes      | replace | Replace whole section (header + body + subtree) |
| `## section (_+)` | yes      | append  | Append overlay content to section end           |
| `## section (+_)` | yes      | prepend | Prepend overlay content to section start        |
| `## new-section`  | no       | add     | Insert as new subsection of its parent          |

Match by full header path. Suffix `(...)` is stripped before matching. Anchor must be unique under its parent — duplicates fail the build. A header with no direct content is structural (nests deeper operations only).

## Frontmatter overlay (`<target>/frontmatter.yaml`)

YAML merged onto base frontmatter via `mergedeep.merge`, overlay-side wins. New keys added; existing keys replaced. No delete.

## Single-target or restricted skills

Declare in base frontmatter:

```yaml
---
name: analyzing-claude-usage
description: ...
targets: [claude]
---
```

Renderer skips this skill for any target not in the list. When `targets` is present, base `SKILL.md` may use target-specific names freely. The `targets` key is stripped from output frontmatter.

## Plugin composition

`src/plugins/<plugin>/plugin.yaml`:

```yaml
skills: [reviewing-code, fixing-code, committing-code, ...]
agents: [docs-keeper, go-engineer, ...]
hooks: [smart-lint, file-protector, ...]
```

Same skill/agent can belong to multiple plugins — just list it in each `plugin.yaml`.

## Renderer

Stack:

- `python-frontmatter` — frontmatter parse/serialize
- `mergedeep` — layered YAML merge (new dep, ~50KB)
- Plain regex for header parsing

Targets, output layout, and target-specific paths:

```python
TARGETS = ["claude", "codex", "gemini", "pi"]

# Per-target output strategy.
#   plugin: dist/<target>/plugins/<plugin>/skills/<skill>/
#   flat:   dist/<target>/skills/<skill>/
OUTPUT = {
    "claude": {"layout": "plugin",  "skill_dir": "skills",        "agent_dir": "agents"},
    "codex":  {"layout": "plugin",  "skill_dir": "skills",        "agent_dir": "agents"},
    "gemini": {"layout": "flat",    "skill_dir": "skills",        "agent_dir": "agents"},
    "pi":     {"layout": "flat",    "skill_dir": "skills",        "agent_dir": "agents"},
}
```

Compile loop:

```python
def main():
    root = repo_root()
    plugin_index = build_plugin_index(root / "src" / "plugins")
    for skill_dir in sorted((root / "src" / "skills").iterdir()):
        if not skill_dir.is_dir(): continue
        for target in TARGETS:
            compile_skill(skill_dir, target, plugin_index, root)
    generate_root_manifests(root, plugin_index)  # marketplace.json, gemini-extension.json
    ensure_gemini_symlinks(root)                  # skills -> dist/gemini/skills, etc.
```

Skill compile (≈30 lines):

```python
def compile_skill(skill_dir, target, plugin_index, root):
    base = frontmatter.load(str(skill_dir / "SKILL.md"))
    if "targets" in base.metadata and target not in base.metadata["targets"]:
        return

    fm = {k: v for k, v in base.metadata.items() if k != "targets"}
    fm_path = skill_dir / target / "frontmatter.yaml"
    if fm_path.exists():
        fm = mergedeep.merge({}, fm, yaml.safe_load(fm_path.read_text()) or {})

    body = base.content
    overlay = skill_dir / target / "body.md"
    if overlay.exists():
        body = apply_overlay(body, overlay.read_text())  # mirror or full

    for out_dir in output_dirs(skill_dir.name, target, plugin_index, root):
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "SKILL.md").write_text(
            frontmatter.dumps(frontmatter.Post(body, **fm)) + "\n"
        )
        copy_support_files(skill_dir, target, out_dir)
```

`output_dirs` returns `[dist/claude/plugins/<plugin>/skills/<skill>/, ...]` for plugin-grouped, `[dist/pi/skills/<skill>/]` for flat. Skills not listed in any `plugin.yaml` are skipped for plugin-grouped targets but still emitted for flat ones.

## Worked example

Base `src/skills/reviewing-code/SKILL.md`:

```markdown
---
name: reviewing-code
description: Code review for security, quality, tests, architecture.
---

# Code Review

Review changed code against project conventions and surface issues.

## Determine scope

Use git to find what changed.

## Run linters and checks

Run the project's linters, type checkers, and tests. Capture output as evidence.

## Review

Check security, quality, missing tests, architectural concerns. Cite `file:line`.

## Report

Group by severity. Include a fix for each.
```

`src/skills/reviewing-code/claude/body.md` — adds Claude-specific orchestration (mirror mode):

```markdown
# Code Review

## Run linters and checks (\_+)

For multi-language codebases, spawn parallel subagents — one per language reviewer — and aggregate findings.

## Multi-agent team mode

Pass `team` in arguments to run reviewers as a team. Pass `external` to add Codex/Gemini.
```

`src/plugins/dev-workflow/plugin.yaml`:

```yaml
skills: [reviewing-code, fixing-code, ...]
agents: [docs-keeper, ...]
hooks: [smart-lint, ...]
```

Build outputs:

- `dist/claude/plugins/dev-workflow/skills/reviewing-code/SKILL.md` — base + Claude overlay applied
- `dist/codex/plugins/dev-workflow/skills/reviewing-code/SKILL.md` — base only (no overlay)
- `dist/gemini/skills/reviewing-code/SKILL.md` — base only
- `dist/pi/skills/reviewing-code/SKILL.md` — base only
- `dist/claude/plugins/dev-workflow/.claude-plugin/plugin.json` — generated from plugin.yaml
- `.claude-plugin/marketplace.json` at repo root — generated, `source: ./dist/claude/plugins/dev-workflow`
- Root symlink `skills` → `dist/gemini/skills` — so Gemini's scanner finds skills

Overlays exist for capability divergence (Claude has subagents, Pi has its `Agent` extension), not for swapping shell commands.

## Target reference

All targets follow [agentskills.io](https://agentskills.io/specification). Per-target additions captured by overlays:

| Target   | Frontmatter extensions                                                                                                                                      | Companion files in `<target>/` | `allowed-tools` format    |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------- |
| `claude` | `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell` | none                           | YAML list or space-string |
| `codex`  | none                                                                                                                                                        | none                           | prompt guidance only      |
| `gemini` | none documented                                                                                                                                             | none                           | agentskills.io spec       |
| `pi`     | `metadata`, `disable-model-invocation`                                                                                                                      | none                           | space-delimited string    |

Sources: [Claude](https://code.claude.com/docs/en/skills), [Codex](https://developers.openai.com/codex/skills), [Gemini](https://geminicli.com/docs/cli/skills/), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md). Cross-reference: [OpenAI's Claude→Codex migration differences](https://github.com/openai/skills/blob/main/skills/.curated/migrate-to-codex/references/differences.md) enumerates every Claude feature that translates and every one that doesn't.

**Codex caveats** (per migration guide):

- `allowed-tools` is preserved as prompt guidance only — not enforced
- `user-invocable` has no direct Codex equivalent — Codex policy lives in user-side config (e.g., `~/.codex/`), not per-skill
- `model`, `effort`, `disable-model-invocation` are unsupported — author must rewrite into prompt guidance or omit
- `argument-hint`, `context`, `agent`, `hooks`, `paths`, `shell` have no Codex equivalent
- **Codex prefers plain English over tool names in instructions** — _"I do not need raw JSON from you; plain English is enough"_. Reinforces the rule: base `SKILL.md` should never reference tools by their native identifier.

### Native tool vocabulary (for overlay authors)

When authoring `<target>/body.md` or `<target>/frontmatter.yaml`, use the target's native tool names:

| Capability   | Claude                   | Codex                                       | Gemini                                                  | Pi                                           |
| ------------ | ------------------------ | ------------------------------------------- | ------------------------------------------------------- | -------------------------------------------- |
| Run shell    | `Bash(* *)`              | `exec_command`                              | `run_shell_command`                                     | `bash`                                       |
| Edit file    | `Edit` / `Write`         | `apply_patch`                               | `mcp_morphllm_edit_file` / `replace` / `write_file`     | `edit` / `write`                             |
| Read file    | `Read`                   | (via `exec_command`)                        | `read_file`                                             | `read`                                       |
| Search code  | `Grep` / `Glob`          | (via `exec_command`)                        | `mcp_morphllm_codebase_search` / `grep_search` / `glob` | `grep` / `find` / `ls`                       |
| Sub-agent    | `Task`                   | `spawn_agent` / `send_input` / `wait_agent` | `invoke_agent`                                          | `Agent` (extension)                          |
| Web search   | `WebSearch` / `WebFetch` | `web`                                       | `google_web_search` / `web_fetch`                       | `web_search` / `web_answer` / `web_research` |
| Docs lookup  | (via `Bash(ctx7 *)`)     | (via `exec_command`)                        | `mcp_context7_query-docs`                               | (via `bash` + `ctx7`)                        |
| Plan / todos | `TodoWrite`              | `update_plan`                               | `enter_plan_mode` / `tracker_create_task`               | `todo` (extension)                           |
| Ask user     | `AskUserQuestion`        | (n/a directly)                              | `ask_user`                                              | `ask_user_question` (extension)              |

Source: each target's CLI self-report. Names may evolve — verify against current docs before adding to overlays.

**Pi name constraint**: frontmatter `name` must equal parent dir name. Do not override in `pi/frontmatter.yaml`.

**Tool format**: per-target overlay uses native format directly. No renderer conversion.

## Discovery paths (what each target finds at repo root)

| Target | Reads at repo root                                                  | Points to                                                                                                  |
| ------ | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Claude | `.claude-plugin/marketplace.json`                                   | `./dist/claude/plugins/*`                                                                                  |
| Codex  | `.agents/plugins/marketplace.json`                                  | `./dist/codex/plugins/*`                                                                                   |
| Gemini | `gemini-extension.json`, `skills/`, `hooks/hooks.json`, `commands/` | symlinks → `dist/gemini/*`                                                                                 |
| Pi     | (none — manual symlinks per project)                                | `~/.pi/agent/skills` → `dist/pi/skills`, `~/.pi/agent/agents` → `dist/pi/agents` (see README "Pi" section) |

## Authoring patterns (lessons from migrating 4 skills + 38 agents)

### Vendor-neutral body checklist

A base `SKILL.md` / `AGENT.md` body is vendor-neutral when:

- No native tool names: no `Task(...)`, `Bash(* *)`, `apply_patch`, `spawn_agent`, `Read`/`Write`, `AskUserQuestion`, `TodoWrite`, `${CLAUDE_SKILL_DIR}`, `$ARGUMENTS`, `` !`cmd` ``, `mcp__*`. Native names live in `<target>/body.md` or `<target>/frontmatter.yaml`.
- Capabilities, not tools: say _"delegate to the `X` agent"_, _"ask a multi-choice question"_, _"track progress through these phases"_. Models map each to their native tool (`Task`, `AskUserQuestion`, `TaskCreate` for Claude; `spawn_agent`, prose, `update_plan` for Codex; etc.).
- Universal CLI commands stay (`git`, `golangci-lint`, `ruff`, `pytest`, `node`, `npm`). Models know them. Do not spell out `git diff HEAD` examples — they add tokens for zero information.
- Skill-specific commands stay literal (e.g., `node $SKILL_DIR/scripts/run.js`) since the model couldn't infer them.

### Description guidelines

- Lead with what the skill does. Follow with concrete trigger phrases the user is likely to say.
- Drop "NOT for X" anti-trigger clauses — low signal and they bloat the 1024-char budget.
- Use verbs the user actually types: _"review"_, _"audit"_, _"check"_, _"refactor"_, _"explore"_, _"deploy"_.

### LLM-friendly formatting

- No markdown tables in bodies — they are pipe-noise for tokens. Convert to bullet lists of pairs.
- No ASCII boxes / box-drawing characters (`│`, `╭`, `┤`, etc.) — same problem, even worse density. If a workflow needs to "print a reference card", describe the content in structured form and let the model format it for the user.
- Headers (`##`, `###`) are fine — structure helps the model.
- Short paragraphs. Numbered lists for ordered steps.
- Code blocks only for content that is literally code/commands (never for documentation tables).

### Mirror-mode vs full-replacement overlays

- **Mirror mode** (`(_+)` / `(+_)` / replace by header anchor): use when the target adds a small section, appends a paragraph, or replaces one section. Empirically used in `learning-patterns/claude/body.md` (replace 2 sections) and `reviewing-code/claude/body.md` (4 `(_+)` appends).
- **Full replacement** (no anchors): use when the target's body diverges by 50%+ from the base. Empirically used in `playwright-skill/pi/body.md` (terser Pi-flavored variant, 1355 bytes vs base 2883).
- **Most agents need only frontmatter overlay** — body is already vendor-neutral. 38 of 38 migrated agents needed zero body overlay; only frontmatter (tools, model, effort).

### Skill→agent references

Skills reference agents **by name only**: _"delegate to `go-engineer`"_. The compiler emits agents under the same name in every target's output (`go-engineer.md` for Claude/Gemini/Pi, `go-engineer.toml` for Codex). Each runtime maps the named reference to its native spawn (`Task(subagent_type="go-engineer")`, `spawn_agent("go-engineer")`, `invoke_agent("go-engineer")`, `Agent("go-engineer")`).

**Rule**: agent name = `src/agents/<name>/` parent directory. No name mangling per target.

### Cross-skill references

Avoid them. Per Perplexity research and Block Engineering authoring guide: skills should be self-contained. Don't write _"for X, use the foo-skill"_; describe what foo-skill does and let the agent's skill-discovery layer match.

Exception: a deterministic sequential pipeline where skill A's output feeds skill B's input — note it briefly.

### Compression targets

Original skills/agents averaged 200–450 lines. Post-migration averages: base ~100–150 lines, frontmatter overlay ~5–20 lines, body overlay (if any) ~30–60 lines. Most of the compression comes from:

- Removing tables (-30% tokens)
- Dropping literal CLI command examples for universal tools (-10%)
- Removing redundancy across phases (-15%)
- Dropping `<!-- CC-ONLY -->` fence blocks (replaced by per-target overlays)

### Commands are skills (Claude Code v2.1.3 unification)

Claude Code unified commands and skills in v2.1.3 — `.claude/commands/<name>.md` and `.claude/skills/<name>/SKILL.md` both produce `/<name>` with identical behavior. Skills are the canonical authoring format; commands are deprecated. ([Migration guide](https://github.com/melodic-software/claude-code-plugins/blob/main/.prompts/slash-commands-to-skill-migration.md))

The compiler emits **only skills**. Codex/Gemini still have their own command formats (TOML files), but those are not generated — skills cover the same UX across all four targets.

**Consolidation pattern for related commands**. Multiple commands sharing a domain/resource collapse into ONE skill. Empirical example: 8 `spec/*` commands (`init`, `new`, `interview`, `plan`, `work`, `status`, `done`, `help`) all use the same `specctl` script — they became one skill with per-action references:

```
src/skills/spec/
  SKILL.md                          # ~86 lines: intent routing + .spec/ structure + cross-cutting rules
  scripts/
    specctl                         # shared script — single canonical location
    specctl.py
  references/
    init.md, interview.md, plan.md, new.md, work.md, done.md, status.md, help.md
  claude/
    frontmatter.yaml                # union of allowed-tools across all 8 actions
```

**No hierarchical skills**. Verified via agentskills.io spec (`name` must be flat lowercase alphanumeric + hyphens, max 64 chars) and Claude Code docs (`plugin-name:skill-name` is plugin namespacing, not skill nesting). Two options:

- **Consolidate**: one skill with per-action references in `references/` (preferred — solves the shared-script question too)
- **Prefix**: flat skills with shared prefix (`spec-init`, `spec-plan`) — only when actions don't share resources

**Shared scripts**: place inside the consolidated skill's `scripts/` directory. Each reference invokes them via `$SKILL_DIR/scripts/<name>`. No symlinks across skills.

### Patterns learned from the spec migration (8 commands → 1 skill)

**Intent-driven routing, not argument-keyword parsing.** Skills are picked by description-match and follow prose instructions. Don't write _"Read the first word of the user's input as the action"_ — that's slash-command framing. Write _"Match the user's request to one of the workflows below"_ and let the model map natural language (`"plan REQ-auth"`, `"create an epic for auth"`, `"spec plan"`) to the same workflow. Avoid `$ARGUMENTS` in the body entirely.

**Describe by situation, not by argument mode.** The old command framing said _"Mode A: argument is a file path; Mode B: argument is empty"_. The skill framing says _"Situation A: `.spec/` doesn't exist; Situation B: `.spec/` exists with a doc path provided"_. The trigger is **observable state + user intent**, not literal argument parsing.

**Description mixes command-shape and intent-shape triggers.** A consolidated skill's description should match both `"spec plan"` (users who learned the command vocabulary) and `"plan an epic"` / `"create vertical-slice tasks"` (users who don't). Both styles map to the same workflow via description-match.

**Intra-skill cross-references are fine.** A consolidated skill's references CAN say _"Next: run the work workflow"_ — that's the same skill's other action, not a cross-skill leak. The Perplexity "self-contained" rule applies only to references that escape the skill (e.g. `Skill(skill="committing-code")`). Internal pipeline references stay.

**Per-action depth lives in `references/`.** SKILL.md is loaded at activation (~100 lines budget — kept under 500 per agentskills.io progressive-disclosure). Per-action detail loads only when the model picks that workflow. The spec skill split as 86 SKILL.md + ~1,200 lines across 8 references; only 1–2 references load per session.

**Frontmatter overlay is union of action tools.** When consolidating N commands into 1 skill, the `<target>/frontmatter.yaml` `allowed-tools` is the union of all N commands' tool lists. Generic `argument-hint: "[workflow] [args...]"` replaces per-action hints.

**Decorative ASCII reference cards are token waste.** Original help command was a 47-pipe `╭───┤` box; rewritten as plain headers + bullets, ~25% smaller, model formats output for the user naturally.

### Bulk migration approach

For >5 similar files, write a small Python helper using `python-frontmatter` + `pyyaml`:

```python
for src in SOURCES:
    post = frontmatter.load(str(src))
    meta = dict(post.metadata)
    base_meta = {k: meta[k] for k in {"name", "description"} if k in meta}
    overlay = {k: v for k, v in meta.items() if k not in {"name", "description"}}
    # write src/agents/<name>/AGENT.md from base_meta + post.content
    # write src/agents/<name>/claude/frontmatter.yaml from overlay
```

The 34-agent CC migration ran in <1 second. Pi-only agents got a similar script with `targets: [pi]` injected into base frontmatter.

## Migration

**Done.** The migration completed on 2026-05-11; this section is retained as historical reference. See the plan at `docs/plans/completed/20260511-skill-compiler-migration.md` for per-task acceptance evidence. Summary of the steps that ran:

1. Built renderer + tests (skills and agents share the overlay/output pipeline; agents add a TOML-conversion code path for Codex).
2. Moved skills to `src/skills/<skill>/` (one dir per skill).
3. Moved agents to `src/agents/<name>/AGENT.md` (one dir per agent, file always named `AGENT.md`).
4. Wrote `src/plugins/<p>/plugin.yaml` for each plugin, listing `skills`, `agents`, `hooks`.
5. Applied the vendor-neutral-body checklist to each base `SKILL.md` / `AGENT.md`; moved target-specific content into `<target>/body.md` + `<target>/frontmatter.yaml`.
6. Migrated `plugins/<p>/commands/*.md` to skills (standalone → individual skill, related → consolidated skill with `references/`).
7. Build → populated `dist/` and root-level generated files.
8. Added committed root symlinks for Gemini (`skills/`, `hooks/`) pointing into `dist/gemini/`.
9. Updated `.gitattributes`: `dist/**` and root-generated files marked `linguist-generated`.
10. Pi consumers symlink `~/.pi/agent/skills` and `~/.pi/agent/agents` to `dist/pi/*` manually (see README "Pi" section); the old `install-pi-exports.sh` was removed.
11. `make check` runs build + drift detection.
12. Deleted `scripts/build/generate-skills.py`, `generate-subagents.py`, `generate-hooks.py`, `generate-agents-md.py`, `generate-flat.sh`, `_common.py`, `CC-ONLY` markers, and the `flat/` tree.

## Out of scope

Per-model variants, hook event renaming, AGENTS.md regeneration logic changes (just reads from `dist/`), Pi extensions (hand-authored TypeScript), section deletion operator, target tool-leak validation.
